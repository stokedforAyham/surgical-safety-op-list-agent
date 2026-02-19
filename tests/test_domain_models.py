from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.oplist_agent.domain.models import Artifact, CaseState, EvidenceRef, ItemKey


def test_evidence_ref_offset_happy_path():
    """Create an EvidenceRef with a valid offset span and verify fields are preserved.

    This test ensures that:
    - EvidenceRef accepts a valid (start_offset, end_offset) 
        pair where end_offset > start_offset.
    - Parsed fields match the input values.
    - Offsets are typed as integers after validation.
    """

    art_id = uuid4()
    ev_id = uuid4()
    ch_id = uuid4()

    valid_data = {
        "artifact_id": art_id,
        "evidence_id": ev_id,
        "page": 1,
        "chunk_id": ch_id,
        "start_offset": 10,
        "end_offset": 20
    }

    ref = EvidenceRef(**valid_data)

    assert ref.artifact_id == art_id
    assert ref.evidence_id == ev_id
    assert ref.start_offset == 10
    assert isinstance(ref.start_offset, int)

def test_evidence_ref_flase_offset():
    """Reject an EvidenceRef where end_offset is not greater than start_offset.

    EvidenceRef enforces a non-empty, forward span for offsets. 
    This test validates that:
    - Providing end_offset <= start_offset raises a Pydantic ValidationError.
    - The error message includes the expected invariant explanation.
    """
    invalid_data = {
        "artifact_id": uuid4(),
        "evidence_id": uuid4(),
        "page": 1,
        "chunk_id": uuid4(),
        "start_offset": 30,
        "end_offset": 20
    }

    with pytest.raises(ValidationError) as exc_info:
        EvidenceRef(**invalid_data)

    assert "end_offset (20) must be > start_offset (30)" in str(exc_info.value)

def test_artifact_created_at_is_utc_aware():
    """Ensure Artifact.created_at is timezone-aware and in UTC.

    This test checks that the created_at field:
    - Is a datetime instance.
    - Includes tzinfo.
    - Uses the UTC timezone.
    """
    expected_time = datetime.now(timezone.utc)

    artifact = Artifact(
        artifact_id=uuid4(),
        filename="test.pdf",
        mime_type="application/pdf",
        created_at=expected_time
    )
    
    # This proves to the linter it is a datetime
    assert isinstance(artifact.created_at, datetime)

    assert artifact.created_at is not None
    assert artifact.created_at.tzinfo is not None # type: ignore
    assert artifact.created_at.tzinfo == timezone.utc # type: ignore

def test_case_state_prepopulates_all_items():
    """Verify CaseState.items is initialized with all ItemKey entries.

    The model uses a default factory to prepopulate the item map. This test ensures:
    - items is non-empty on a new CaseState.
    - Every ItemKey exists as a key in the items dictionary.
    - The number of entries equals the number of defined ItemKeys.
    """
    case = CaseState(case_id=uuid4())
    
    assert len(case.items) > 0

    for key in ItemKey:
        assert key in case.items

    assert len(case.items) == len(ItemKey)
