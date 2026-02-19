"""
Domain models for the Surgical Op-List Agent.

Purpose
- Provide a small, stable set of nouns (types) that every layer can share:
  API, agents, persistence, and UI.

Key ideas
- A Case is the unit of work.
- Artifacts are uploaded documents belonging to a Case and can be globally toggled.
- EvidenceRef points to an exact snippet inside an Artifact via chunk_id + offsets.
- Items are represented as a mapping from ItemKey to ItemState.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class ItemKey(str, Enum):
    """Canonical checklist item identifiers used as keys in CaseState.items."""

    ALLERGIES = "allergies"
    BLOOD_LOSS_RISK = "blood_loss_risk"
    NUMBER_BUNITS_AVAILABLE = "number_bunits_available"
    ABX_PROPHYLAXIS_TIMING = "abx_prophylaxis_timing"


class ItemStatus(str, Enum):
    """Lifecycle status for an item.

    Notes
    - pending: not yet evaluated (pipeline has not produced a result)
    - unknown: evaluated, but insufficient/uncertain evidence
    - confirmed: evaluated and supported by evidence or user confirmation
    - conflict: evaluated and conflicting evidence exists
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


class Artifact(BaseModel):
    """An uploaded source document belonging to a case.

    included controls global participation of this artifact in evidence mapping.
    """

    model_config = ConfigDict(extra="forbid")

    artifact_id: UUID = Field(description="Stable identifier of this artifact.")
    filename: str = Field(description="Original filename as uploaded.")
    mime_type: str = Field(description="MIME type of the uploaded file.")
    included: bool = Field(
        default=True, description="Global include/exclude toggle for this artifact."
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the artifact was added.",
    )


class EvidenceRef(BaseModel):
    """A precise reference to a snippet of evidence inside an artifact.

    Offsets are 0-based and end-exclusive,
    relative to the chunk text identified by chunk_id.
    """

    model_config = ConfigDict(extra="forbid")

    artifact_id: UUID = Field(description="Artifact that contains the evidence.")
    evidence_id: UUID = Field(
        description="Stable identifier for this evidence reference."
    )
    page: int = Field(ge=1, description="1-based page number in the source document")
    chunk_id: UUID = Field(
        description="Identifier of the stored/indexed chunk containing the snippet."
    )
    start_offset: int = Field(
        ge=0, description="0-based start index (inclusive) relative to the chunk text."
    )
    end_offset: int = Field(
        ge=0, description="0-based end index (exclusive) relative to the chunk text."
    )

    @model_validator(mode="after")
    def check_offset(self) -> EvidenceRef:
        """Ensure offsets form a valid, non-empty span."""
        if self.end_offset <= self.start_offset:
            raise ValueError(
                f"end_offset ({self.end_offset}) "
                f"must be > start_offset ({self.start_offset})"
            )
        return self


class ItemState(BaseModel):
    """Current state of one checklist item."""

    model_config = ConfigDict(extra="forbid")

    status: ItemStatus = Field(
        default=ItemStatus.PENDING, description="Current status for this item."
    )
    evidence_refs: list[EvidenceRef] = Field(
        default_factory=list,
        description="Evidence references supporting the current status/value.",
    )


def default_items() -> dict[ItemKey, ItemState]:
    """Create a fresh, fully-populated item map for a new case."""
    return {
        ItemKey.ALLERGIES: ItemState(),
        ItemKey.BLOOD_LOSS_RISK: ItemState(),
        ItemKey.NUMBER_BUNITS_AVAILABLE: ItemState(),
        ItemKey.ABX_PROPHYLAXIS_TIMING: ItemState(),
    }


class CaseState(BaseModel):
    """Aggregate state for a case.

    items is always pre-populated with all ItemKey entries via default_items().
    """

    model_config = ConfigDict(extra="forbid")

    case_id: UUID = Field(description="Stable identifier of this case.")
    artifacts: list[Artifact] = Field(
        default_factory=list, description="All artifacts uploaded to this case."
    )
    items: dict[ItemKey, ItemState] = Field(
        default_factory=default_items, description="Item states keyed by ItemKey."
    )
