from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.oplist_agent.domain.entities import Artifact


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    """Enumeration of event types."""

    CASE_CREATED = "case_created"
    ARTIFACT_ADDED = "artifact_added"
    ARTIFACT_TOGGLED = "artifact_toggled"
    #EVIDENCE_MAPPED = "evidence_mapped"
    ITEM_STATE_UPDATED = "item_state_updated"


class EventBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(description="Stable identifier of this event.")
    case_id: UUID = Field(
        description="Stable identifier of the case this event belongs to."
    )
    event_type: EventType = Field(description="Type of the event.")
    timestamp: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the event occurred.",
    )
    actor: Literal["user", "system"] = Field(description="Originator of the event.")
    correlation_id: UUID | None = Field(
        default=None,
        description=(
            "Identifier to correlate related events, e.g. events belonging "
            "to the same pipeline run."
        ),
    )


class CaseCreated(EventBase):
    """Event emitted when a new case is initialized."""

    event_type: Literal[EventType.CASE_CREATED] = Field(default=EventType.CASE_CREATED)


class ArtifactAdded(EventBase):
    """Event emitted when a new artifact is added to a case."""

    event_type: Literal[EventType.ARTIFACT_ADDED] = Field(
        default=EventType.ARTIFACT_ADDED
    )
    artifact_id: UUID = Field(description="Identifier of the artifact that was added.")
    artifact: Artifact = Field(description="Details of the artifact that was added.")


class ArtifactToggled(EventBase):

    event_type: Literal[EventType.ARTIFACT_TOGGLED] = Field(
        default=EventType.ARTIFACT_TOGGLED
    )
    artifact_id: UUID = Field(
        description="Identifier of the artifact that was toggled."
    )
    included: bool = Field(description="New inclusion status of the artifact.")
