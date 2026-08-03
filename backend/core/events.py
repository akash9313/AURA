from enum import Enum


class Event(Enum):
    # System & Core Events
    TEXT_READY = "text_ready"
    INTENT_READY = "intent_ready"
    ACTION_READY = "action_ready"
    AI_RESPONSE_READY = "ai_response_ready"
    SHUTDOWN = "shutdown"

    # Streaming Voice Events
    MIC_STARTED = "mic_started"
    VOICE_STARTED = "voice_started"
    VOICE_ENDED = "voice_ended"
    PARTIAL_TRANSCRIPT = "partial_transcript"
    FINAL_TRANSCRIPT = "final_transcript"
    STREAMING_RESPONSE = "streaming_response"
    SPEECH_STARTED = "speech_started"
    SPEECH_INTERRUPTED = "speech_interrupted"
    SPEECH_COMPLETED = "speech_completed"

    # Memory Engine Events
    MEMORY_SAVE = "memory_save"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_DELETE = "memory_delete"
    MEMORY_QUERY = "memory_query"
    MEMORY_RESPONSE = "memory_response"
    MEMORY_GET = "memory_get"
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_FINISHED = "conversation_finished"

    # Vision Engine Events
    IMAGE_CAPTURED = "image_captured"
    SCREEN_CAPTURED = "screen_captured"
    OCR_COMPLETED = "ocr_completed"
    VISION_COMPLETED = "vision_completed"
    OBJECTS_DETECTED = "objects_detected"
    DOCUMENT_ANALYZED = "document_analyzed"
    SCREEN_CAPTURE_REQUEST = "screen_capture_request"
    CAMERA_CAPTURE_REQUEST = "camera_capture_request"
    IMAGE_ANALYZE_REQUEST = "image_analyze_request"
    DOCUMENT_ANALYZE_REQUEST = "document_analyze_request"

    # Agent Orchestrator & Cognitive Events
    GOAL_CREATED = "goal_created"
    GOAL_UPDATED = "goal_updated"
    WORKFLOW_CREATED = "workflow_created"
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    PLAN_CREATED = "plan_created"
    DECISION_MADE = "decision_made"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_FINISHED = "execution_finished"
    REFLECTION_COMPLETED = "reflection_completed"
    LEARNING_COMPLETED = "learning_completed"

    # Windows Automation Events
    APPLICATION_OPENED = "application_opened"
    APPLICATION_CLOSED = "application_closed"
    WINDOW_FOCUSED = "window_focused"
    TEXT_TYPED = "text_typed"
    SHORTCUT_EXECUTED = "shortcut_executed"

    # Browser Agent Events
    BROWSER_STARTED = "browser_started"
    PAGE_OPENED = "page_opened"
    ELEMENT_CLICKED = "element_clicked"
    FORM_FILLED = "form_filled"
    PAGE_EXTRACTED = "page_extracted"
    DOWNLOAD_COMPLETED = "download_completed"