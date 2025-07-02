import json
import yaml
import markdown
from pathlib import Path
from jinja2 import Template
from models import Session, Speaker

# Define the base directory for the berlin.pydata.org website
BERLIN_PYDATA_DIR = Path(__file__).parent.parent.resolve()


def load_config(file_path: Path) -> dict:
    """Load YAML configuration."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_sessions(file_path: Path) -> list[Session]:
    """Load and validate session data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [Session(**session_data) for session_data in data]


def load_speakers(file_path: Path) -> dict[str, Speaker]:
    """Load and validate speaker data, returning a dict keyed by ID."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return {speaker_data['ID']: Speaker(**speaker_data) for speaker_data in data}


def render_markdown(text: str) -> str:
    """Convert markdown text to HTML."""
    md = markdown.Markdown(extensions=['extra', 'nl2br'])
    return md.convert(text)


def generate_session_page(session: Session, speakers: list[Speaker], template: Template, output_dir: Path, social_images_dir: Path, default_social_image: Path, base_url: str) -> None:
    """Generate HTML page for a single session."""
    # Render description with markdown
    description_html = render_markdown(session.description)

    # Check if session-specific social image exists
    social_image_path = social_images_dir / f"{session.id}.png"
    has_session_image = social_image_path.exists()
    
    if has_session_image:
        social_image_url = f"{base_url}/{social_image_path.relative_to(BERLIN_PYDATA_DIR)}"
        session_image_url = social_image_url  # For displaying in the page
    else:
        # Fallback to default social image for meta tags only
        social_image_url = f"{base_url}/{default_social_image.relative_to(BERLIN_PYDATA_DIR)}"
        session_image_url = None  # No session-specific image to display

    # Render template
    html_content = template.render(
        session=session,
        speakers=speakers,
        description_html=description_html,
        base_url=base_url,
        social_image_url=social_image_url,
        has_session_image=has_session_image,
        session_image_url=session_image_url
    )

    # Write to file
    output_file = output_dir / f"{session.id}.html"
    output_file.write_text(html_content, encoding='utf-8')
    print(f"Generated: {output_file}")


def generate_index_page(sessions: list[Session], template_path: Path, output_dir: Path, base_url: str) -> None:
    """Generate the index page listing all sessions."""
    # Load index template
    with open(template_path, 'r') as f:
        template = Template(f.read())

    # Get unique tracks, sorted
    tracks = sorted(set(s.track_str for s in sessions if s.track_str))

    # Sort sessions by track, then by title
    sorted_sessions = sorted(sessions, key=lambda s: (s.track_str or 'zzz', s.title))

    # Render template
    html_content = template.render(
        sessions=sorted_sessions,
        tracks=tracks,
        base_url=base_url
    )

    # Write to file
    output_file = output_dir / "index.html"
    output_file.write_text(html_content, encoding='utf-8')
    print(f"Generated: {output_file}")


def main():
    # Load configuration
    config_path = Path(__file__).parent / 'config.yaml'
    config = load_config(config_path)
    base_url = config['base_url']

    # Construct absolute paths from config
    sessions_file = BERLIN_PYDATA_DIR / config['input_files']['sessions']
    speakers_file = BERLIN_PYDATA_DIR / config['input_files']['speakers']
    session_template_file = BERLIN_PYDATA_DIR / config['templates']['session']
    index_template_file = BERLIN_PYDATA_DIR / config['templates']['index']
    output_dir = BERLIN_PYDATA_DIR / config['output']['sessions_dir']
    social_images_dir = BERLIN_PYDATA_DIR / config['output']['social_images_dir']
    default_social_image = BERLIN_PYDATA_DIR / config['output']['default_social_image']

    # Load data
    print("Loading session data...")
    sessions = load_sessions(sessions_file)
    print(f"Loaded {len(sessions)} sessions")

    print("Loading speaker data...")
    speakers_dict = load_speakers(speakers_file)
    print(f"Loaded {len(speakers_dict)} speakers")

    # Load session template
    print("Loading session template...")
    with open(session_template_file, 'r') as f:
        session_template = Template(f.read())

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Generate pages
    print("\nGenerating session pages...")
    for session in sessions:
        # Get speakers for this session
        session_speakers = []
        for speaker_id in session.speaker_ids:
            if speaker_id in speakers_dict:
                session_speakers.append(speakers_dict[speaker_id])
            else:
                print(f"Warning: Speaker {speaker_id} not found for session {session.id}")

        # Generate page
        generate_session_page(
            session,
            session_speakers,
            session_template,
            output_dir,
            social_images_dir,
            default_social_image,
            base_url
        )

    # Generate index page
    print("\nGenerating index page...")
    generate_index_page(sessions, index_template_file, output_dir, base_url)

    print(f"\nDone! Generated {len(sessions)} session pages and index.")


if __name__ == "__main__":
    main()
