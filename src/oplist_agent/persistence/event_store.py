from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.oplist_agent.domain.events import EventBase

"""Event store abstractions and in-memory implementation.

This module defines:
- EventStore: protocol for appending and loading case events.
- InMemoryEventStore: simple process-local store for MVP development/tests.

Storage model:
- Key: case_id (UUID)
- Value: ordered list of events for that case
"""


class EventStore(Protocol):
    """Contract for persisting and retrieving case events."""

    def append(self, event: EventBase) -> None:
        """Persist one event for its case.

        Implementations should preserve append order because replay depends on it.
        """

        ...

    def load(self, case_id: UUID) -> list[EventBase]:
        """Return all events for a case in append order.

        Returns an empty list when the case has no events.
        """

        ...


class InMemoryEventStore:
    """In-memory event store backed by a dict of event lists.

    Suitable for local development and tests. Data is lost when the process exits.
    """

    def __init__(self) -> None:
        """Initialize an empty store mapping case_id -> list[EventBase]."""
        self._events_by_case: dict[UUID, list[EventBase]] = {}

    def append(self, event: EventBase) -> None:
        """Append an event to the list for its case_id."""
        case_id = event.case_id
        if case_id not in self._events_by_case:
            self._events_by_case[case_id] = []
        self._events_by_case[case_id].append(event)

    def load(self, case_id: UUID) -> list[EventBase]:
        """Return a copy of the events for case_id, or [] if none exist."""
        return list(self._events_by_case.get(case_id, []))
