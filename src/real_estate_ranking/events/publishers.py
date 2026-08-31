from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from real_estate_ranking.schemas import InteractionEvent


class EventPublisher(Protocol):
    def publish(self, event: InteractionEvent) -> bool: ...


class LocalEventPublisher:
    """Idempotent JSONL publisher used by local/CI environments."""

    def __init__(self, path: Path):
        self.path = path
        self.seen = self._load_seen_event_ids()

    def _load_seen_event_ids(self) -> set[str]:
        if not self.path.exists():
            return set()
        seen: set[str] = set()
        with self.path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                event_id = record.get("event_id")
                if isinstance(event_id, str):
                    seen.add(event_id)
        return seen

    def publish(self, event: InteractionEvent) -> bool:
        if event.event_id in self.seen:
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event.record(), separators=(",", ":")) + "\n")
        self.seen.add(event.event_id)
        return True


class AzureEventHubPublisher:
    def __init__(self, connection_string: str, hub_name: str):
        from azure.eventhub import EventHubProducerClient
        self.client = EventHubProducerClient.from_connection_string(connection_string, eventhub_name=hub_name)

    def publish(self, event: InteractionEvent) -> bool:
        from azure.eventhub import EventData
        batch = self.client.create_batch()
        batch.add(EventData(json.dumps(event.record())))
        self.client.send_batch(batch)
        return True


class LocalWorkflowQueue:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def enqueue(self, workflow: str, property_id: str, user_id: str) -> str:
        message_id = f"{workflow}:{property_id}:{user_id}"
        if not any(x["message_id"] == message_id for x in self.messages):
            self.messages.append({"message_id": message_id, "workflow": workflow,
                                  "property_id": property_id, "user_id": user_id})
        return message_id
