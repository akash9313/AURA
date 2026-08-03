import logging
from core.events import Event
from core.service import Service
from memory.manager import MemoryManager

logger = logging.getLogger("AURA.MemoryService")


class MemoryService(Service):
    """
    MemoryService connects the MemoryManager entry point to the AURA EventBus.
    """

    def __init__(self, bus, manager: MemoryManager = None):
        super().__init__(bus)
        self.manager = manager if manager is not None else MemoryManager()

    def start(self) -> None:
        logger.info("Memory Service Started")

        self.bus.subscribe(Event.CONVERSATION_STARTED, self.on_conversation_started)
        self.bus.subscribe(Event.CONVERSATION_FINISHED, self.on_conversation_finished)
        self.bus.subscribe(Event.MEMORY_SAVE, self.on_memory_save)
        self.bus.subscribe(Event.MEMORY_QUERY, self.on_memory_query)
        self.bus.subscribe(Event.MEMORY_GET, self.on_memory_query)
        self.bus.subscribe(Event.MEMORY_DELETE, self.on_memory_delete)
        self.bus.subscribe(Event.MEMORY_UPDATED, self.on_memory_update)

    def stop(self) -> None:
        logger.info("Memory Service Stopped")

    def on_conversation_started(self, data: dict = None) -> None:
        cid = data.get("conversation_id") if isinstance(data, dict) else None
        self.manager.working.start_new_session(cid)
        self.manager.conversation.start_conversation(cid)

    def on_conversation_finished(self, data: dict = None) -> None:
        cid = data.get("conversation_id") if isinstance(data, dict) else None
        record = self.manager.summarize(cid)
        self.manager.working.clear()
        if record:
            self.bus.publish(Event.MEMORY_RESPONSE, {
                "action": "conversation_finished",
                "conversation_id": record.conversation_id,
                "summary": record.summary
            })

    def on_memory_save(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        key = data.get("key")
        value = data.get("value")
        category = data.get("category", "preference")
        if key and value:
            fact = self.manager.remember(key, value, category=category)
            self.bus.publish(Event.MEMORY_UPDATED, {
                "action": "save",
                "key": fact.key,
                "value": fact.value
            })

    def on_memory_query(self, data: Any) -> None:
        key = data.get("key") if isinstance(data, dict) else str(data)
        val = self.manager.recall(key)
        self.bus.publish(Event.MEMORY_RESPONSE, {
            "action": "recall",
            "key": key,
            "value": val
        })

    def on_memory_delete(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        key = data.get("key")
        if key:
            success = self.manager.forget(key)
            self.bus.publish(Event.MEMORY_UPDATED, {
                "action": "delete",
                "key": key,
                "success": success
            })

    def on_memory_update(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        key = data.get("key")
        value = data.get("value")
        if key and value:
            fact = self.manager.merge(key, value)
            self.bus.publish(Event.MEMORY_RESPONSE, {
                "action": "update",
                "key": fact.key,
                "value": fact.value
            })
