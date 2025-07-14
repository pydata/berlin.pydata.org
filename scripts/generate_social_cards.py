"""Generate social media cards using template v2 with upper-right safe zone."""

import hashlib
import json
import string
from io import BytesIO
from pathlib import Path

import requests
from models import Session, Speaker
from PIL import Image, ImageDraw, ImageFont

CARD_WIDTH = 1200
CARD_HEIGHT = 630
COLORS = {
    "text": "#ffffff",
    # "text": "#000000",
}
OUTPUT_DIR = Path("../images/social")
CACHE_DIR = Path(".speaker_photo_cache")
TEMPLATE_PATH = Path(
    "../images/social/social_card_speaker_template_v2.png"
    # "../images/social/social_card_speaker_template_v3.png"
)

# Safe zone definition
SAFE_ZONE_X = 600  # Template content starts at x=600
SAFE_ZONE_HEIGHT = 370  # Template content extends to y=370


class CardGenerator:
    """Generate social media cards for conference sessions using template v2."""

    def __init__(self):
        """Initialize the card generator."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(exist_ok=True)
        self.sessions = self._load_sessions()
        self.speakers = self._load_speakers()
        self.fonts = self._load_fonts()

    def _load_sessions(self) -> list[Session]:
        """Load sessions from JSON file."""
        with open("../../_data/berlin2025_sessions.json") as f:
            data = json.load(f)
        return [Session(**item) for item in data]

    def _load_speakers(self) -> dict[str, Speaker]:
        """Load speakers from JSON file and index by ID."""
        with open("../../_data/berlin2025_speakers.json") as f:
            data = json.load(f)
        speakers = [Speaker(**item) for item in data]
        return {speaker.id: speaker for speaker in speakers}

    def _load_fonts(self) -> dict[str, ImageFont.FreeTypeFont]:
        """Load fonts for text rendering."""
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]

        font_path = None
        for path in font_paths:
            if Path(path).exists():
                font_path = path
                break

        if font_path:
            fonts = {
                "title": ImageFont.truetype(font_path, 46),
                "subtitle": ImageFont.truetype(font_path, 28),
                "small": ImageFont.truetype(font_path, 24),
                "event_info": ImageFont.truetype(
                    font_path, 42
                ),  # 50% larger than subtitle
            }
        else:
            # Fallback to default font
            default_font = ImageFont.load_default()
            fonts = {
                "title": default_font,
                "subtitle": default_font,
                "small": default_font,
                "event_info": default_font,
            }
            print("Warning: Using default font. Text may not render as expected.")

        return fonts

    def _download_speaker_photo(self, url: str) -> Image.Image | None:
        """Download and cache speaker photo."""
        # Create a hash of the URL for cache filename
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_path = CACHE_DIR / f"{url_hash}.jpg"

        # Check cache first
        if cache_path.exists():
            try:
                return Image.open(cache_path)
            except Exception:
                cache_path.unlink()  # Remove corrupted cache file

        # Download the image
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            # Convert to RGB for JPEG saving (handles RGBA and P mode)
            if img.mode in ("RGBA", "P"):
                rgb_img = Image.new("RGB", img.size, COLORS["text"])
                if img.mode == "RGBA":
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                else:
                    rgb_img.paste(img)
                img = rgb_img

            # Cache for future use
            img.save(cache_path, "JPEG", quality=95)
            return img
        except Exception as e:
            print(f"Error downloading speaker photo from {url}: {e}")
            return None

    def _process_speaker_photo(
        self, photo: Image.Image, size: int = 200
    ) -> Image.Image:
        """Process speaker photo into a circular format with proper transparency."""
        # Convert to RGBA if not already
        if photo.mode != "RGBA":
            photo = photo.convert("RGBA")

        # Create a square thumbnail
        photo.thumbnail((size * 2, size * 2), Image.Resampling.LANCZOS)

        # Make it square by center-cropping
        width, height = photo.size
        if width != height:
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            photo = photo.crop((left, top, left + min_dim, top + min_dim))

        # Resize to exact size
        photo = photo.resize((size, size), Image.Resampling.LANCZOS)

        # Create circular mask
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        # Apply circular mask
        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(photo, (0, 0))
        output.putalpha(mask)

        return output

    def _wrap_text(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int
    ) -> list[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _is_ok(self, char: str) -> bool:
        """Social card text can only show ascii characters."""
        if any(
            [
                char in string.ascii_letters,
                char in string.digits,
                char in string.whitespace,
                char in string.punctuation,
            ]
        ):
            return True
        return False

    def _clean_text(self, text: str) -> str:
        """Social card text can only show ascii characters."""
        return "".join([t for t in text if self._is_ok(t)])

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _draw_text_smart(
        self,
        draw: ImageDraw.Draw,
        text: str,
        x: int,
        y: int,
        font: ImageFont.FreeTypeFont,
        fill: tuple | str,
    ) -> None:
        text = self._clean_text(text)
        """Smart text rendering that handles emojis properly with multiple fallback strategies."""
        # Convert hex color to RGB tuple if needed
        if isinstance(fill, str):
            fill = self._hex_to_rgb(fill)
        try:
            # Strategy 1: Try modern PIL emoji support with embedded_color
            draw.text((x, y), text, font=font, fill=fill, embedded_color=True)
        except Exception:
            try:
                # Strategy 2: Try without embedded_color (older PIL versions)
                draw.text((x, y), text, font=font, fill=fill)
            except Exception:
                try:
                    # Strategy 3: If emojis cause issues, render text-only version
                    import re

                    # Keep only alphanumeric, spaces, and common punctuation
                    text_only = re.sub(r'[^\w\s\-.,!?:;()[\]{}"\'\\/]', " ", text)
                    # Clean up multiple spaces
                    text_only = re.sub(r"\s+", " ", text_only).strip()

                    if text_only:
                        draw.text((x, y), text_only, font=font, fill=fill)
                    else:
                        # If no readable text remains, show placeholder
                        draw.text(
                            (x, y),
                            "[Content with special characters]",
                            font=font,
                            fill=fill,
                        )
                except Exception:
                    # Strategy 4: Ultimate fallback - ASCII only
                    try:
                        ascii_text = (
                            text.encode("ascii", "ignore").decode("ascii").strip()
                        )
                        if ascii_text:
                            draw.text((x, y), ascii_text, font=font, fill=fill)
                        else:
                            draw.text((x, y), "[Special content]", font=font, fill=fill)
                    except Exception:
                        # Strategy 5: Last resort - empty or minimal text
                        draw.text((x, y), "[Text]", font=font, fill=fill)

    def create_session_card(self, session: Session) -> Image.Image:
        """Create a social media card using template v2 approach."""
        # Load the template
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

        # Create a copy of the template
        img = Image.open(TEMPLATE_PATH).copy().convert("RGBA")

        # Get template dimensions
        width, height = img.size

        # Convert to RGB for final output
        final_img = Image.new("RGB", (width, height), (255, 255, 255))
        final_img.paste(img, (0, 0), img)

        draw = ImageDraw.Draw(final_img)

        # Use exact positions
        speaker_margin_x = 40
        speaker_margin_y = 50  # Same as v2

        # Get speaker photos (up to 2)
        speaker_photos = []
        for speaker_id in session.speaker_ids[:2]:  # Max 2 speakers
            if speaker_id in self.speakers:
                speaker = self.speakers[speaker_id]
                if speaker.picture:
                    photo = self._download_speaker_photo(
                        f"https://cfp.pydata.org/{speaker.picture}"
                    )
                    if photo:
                        speaker_photos.append((photo, speaker_id))

        # Adjust size based on number of speakers
        if len(speaker_photos) == 2:
            # Decrease by 33% when there are two speakers
            speaker_size = int(height * 0.495 * 0.67)  # ≈209px
        else:
            # Full size for single speaker
            speaker_size = int(height * 0.495)  # ≈312px

        # Process photos with the appropriate size
        processed_photos = []
        for photo, speaker_id in speaker_photos:
            processed_photo = self._process_speaker_photo(photo, size=speaker_size)
            processed_photos.append(processed_photo)

        # Place speaker photos in upper left
        if processed_photos:
            x_offset = speaker_margin_x
            for photo in processed_photos:
                final_img.paste(photo, (x_offset, speaker_margin_y), photo)
                x_offset += speaker_size + 20  # Add spacing between photos

        # Session title - align at bottom of safe zone box
        # Always use full width
        full_width = CARD_WIDTH - 80  # 1120px
        line_height = 60

        # Wrap text with full width
        title_lines = self._wrap_text(session.title, self.fonts["title"], full_width)

        # Calculate title block height
        title_block_height = len(title_lines[:5]) * line_height  # Max 5 lines

        # Position title so bottom edge is at y=520
        # Simple bottom alignment - no complex calculations needed
        title_y_start = 540 - title_block_height

        # Draw title lines with smart emoji handling
        title_y = title_y_start
        for i, line in enumerate(title_lines[:5]):  # Max 5 lines
            self._draw_text_smart(
                draw,
                line,
                40,
                title_y,
                self.fonts["title"],
                COLORS["text"],
            )
            title_y += line_height

        # Speaker names at bottom
        if session.speaker_ids:
            speaker_names = []
            for sid in session.speaker_ids[:3]:  # Show up to 3 speaker names
                if sid in self.speakers:
                    speaker_names.append(self.speakers[sid].name)

            if speaker_names:
                speakers_text = " • ".join(speaker_names)
                # Position at bottom with proper margin
                speaker_y = height - 80
                draw.text(
                    (40, speaker_y),
                    speakers_text,
                    font=self.fonts["subtitle"],
                    fill=COLORS["text"],
                )

        # Event info is already included in the template

        return final_img

    def create_default_card(self) -> Image.Image:
        """Create the default social media card."""
        # For the default card, just use the template as-is
        if TEMPLATE_PATH.exists():
            return Image.open(TEMPLATE_PATH).copy()
        else:
            # Fallback: create a simple card
            img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#7B3F99")
            draw = ImageDraw.Draw(img)
            draw.text(
                (CARD_WIDTH // 2, CARD_HEIGHT // 2),
                "PyData Berlin 2025",
                font=self.fonts["title"],
                fill=COLORS["text"],
                anchor="mm",
            )
            return img

    def generate_all_cards(self):
        """Generate social media cards for all sessions."""
        print(
            f"Generating {len(self.sessions)} session cards using {TEMPLATE_PATH.stem}...\n"
        )

        for i, session in enumerate(self.sessions):
            try:
                card = self.create_session_card(session)
                output_path = OUTPUT_DIR / f"{session.id}.png"
                card.save(output_path, "PNG", optimize=True)
                print(f"✓ [{i + 1:2d}/{len(self.sessions)}] Generated: {session.id}")
            except Exception as e:
                print(
                    f"✗ [{i + 1:2d}/{len(self.sessions)}] Error generating {session.id}: {e}"
                )

        # Generate default card
        try:
            default_card = self.create_default_card()
            default_card.save(
                OUTPUT_DIR / "social_card_default.png", "PNG", optimize=True
            )
            print("\n✓ Generated default social card")
        except Exception as e:
            print(f"\n✗ Error generating default card: {e}")

        print(f"\nAll cards saved to: {OUTPUT_DIR}")


def main():
    """Main function to generate all social media cards."""
    generator = CardGenerator()
    generator.generate_all_cards()


if __name__ == "__main__":
    main()
