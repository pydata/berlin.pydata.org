from pydantic import BaseModel, Field
from typing import Optional, Union, List


class SessionType(BaseModel):
    en: str


class Track(BaseModel):
    en: str


class Session(BaseModel):
    id: str = Field(alias="ID")
    title: str = Field(alias="Proposal title")
    session_type: Union[str, SessionType] = Field(alias="Session type")
    track: Optional[Union[str, Track]] = Field(alias="Track", default=None)
    abstract: str = Field(alias="Abstract")
    description: str = Field(alias="Description")
    speaker_ids: List[str] = Field(alias="Speaker IDs")
    speaker_names: List[str] = Field(alias="Speaker names")
    room: Optional[str | dict] = Field(alias="Room", default=None)
    start: Optional[str] = Field(alias="Start", default=None)
    audience_level: str = Field(alias="Expected audience expertise: Domain")
    company: Optional[str] = Field(alias="Company / Institute", default=None)
    prerequisites: Optional[str] = Field(alias="Prerequisites", default=None)

    @property
    def session_type_str(self) -> str:
        """Get session type as string."""
        if isinstance(self.session_type, str):
            return self.session_type
        return self.session_type.en

    @property
    def track_str(self) -> Optional[str]:
        """Get track as string."""
        if self.track is None:
            return None
        if isinstance(self.track, str):
            return self.track
        return self.track.en


class Speaker(BaseModel):
    id: str = Field(alias="ID")
    name: str = Field(alias="Name")
    biography: Optional[str] = Field(alias="Biography", default=None)
    picture: Optional[str] = Field(alias="Picture", default=None)
    proposal_ids: List[str] = Field(alias="Proposal IDs")
    position: Optional[str] = Field(alias="Position / Job", default=None)
    homepage: Optional[str] = Field(alias="Homepage", default=None)
    linkedin: Optional[str] = Field(alias="LinkedIn", default=None)
    github: Optional[str] = Field(alias="Github", default=None)
    mastodon: Optional[str] = Field(alias="Mastodon", default=None)
    bluesky: Optional[str] = Field(alias="Bluesky", default=None)
    twitter: Optional[str] = Field(alias="X / Twitter", default=None)

    @property
    def has_social_links(self) -> bool:
        """Check if speaker has any social media links."""
        return any(
            [
                self.homepage,
                self.linkedin,
                self.github,
                self.mastodon,
                self.bluesky,
                self.twitter,
            ]
        )
