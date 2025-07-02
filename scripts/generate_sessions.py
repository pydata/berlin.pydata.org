import json
import markdown
from pathlib import Path
from jinja2 import Template
from models import Session, Speaker


def load_sessions(file_path: str) -> list[Session]:
    """Load and validate session data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [Session(**session_data) for session_data in data]


def load_speakers(file_path: str) -> dict[str, Speaker]:
    """Load and validate speaker data, returning a dict keyed by ID."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return {speaker_data['ID']: Speaker(**speaker_data) for speaker_data in data}


def render_markdown(text: str) -> str:
    """Convert markdown text to HTML."""
    md = markdown.Markdown(extensions=['extra', 'nl2br'])
    return md.convert(text)


def generate_session_page(session: Session, speakers: list[Speaker], template: Template, output_dir: Path, base_url: str) -> None:
    """Generate HTML page for a single session."""
    # Render description with markdown
    description_html = render_markdown(session.description)
    
    # Check if session-specific social image exists
    social_image_path = Path("../images/social") / f"{session.id}.png"
    if social_image_path.exists():
        social_image_url = f"{base_url}/images/social/{session.id}.png"
    else:
        # Fallback to default social image
        social_image_url = f"{base_url}/images/social/social_card_default.png"
    
    # Render template
    html_content = template.render(
        session=session,
        speakers=speakers,
        description_html=description_html,
        base_url=base_url,
        social_image_url=social_image_url
    )
    
    # Write to file
    output_file = output_dir / f"{session.id}.html"
    output_file.write_text(html_content, encoding='utf-8')
    print(f"Generated: {output_file}")


def generate_index_page(sessions: list[Session], output_dir: Path, base_url: str) -> None:
    """Generate the index page listing all sessions."""
    # Load index template
    with open('index_template.html', 'r') as f:
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
    # Configuration
    base_url = "https://berlin.pydata.org"  # Base URL for social media meta tags
    
    # Load data
    print("Loading session data...")
    sessions = load_sessions('../../_data/berlin2025_sessions.json')
    print(f"Loaded {len(sessions)} sessions")
    
    print("Loading speaker data...")
    speakers_dict = load_speakers('../../_data/berlin2025_speakers.json')
    print(f"Loaded {len(speakers_dict)} speakers")
    
    # Load template
    print("Loading template...")
    with open('session_template.html', 'r') as f:
        template = Template(f.read())
    
    # Create output directory
    output_dir = Path('../conferences/2025')
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
        generate_session_page(session, session_speakers, template, output_dir, base_url)
    
    # Generate index page
    print("\nGenerating index page...")
    generate_index_page(sessions, output_dir, base_url)
    
    print(f"\nDone! Generated {len(sessions)} session pages and index.")


if __name__ == "__main__":
    main()