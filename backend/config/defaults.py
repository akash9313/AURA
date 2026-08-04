from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Dict[str, Any]] = {
    "speech": {
        "sample_rate": 16000,
        "channels": 1,
        "frame_duration_ms": 10,
    },
    "microphone": {
        "device_index": None,
        "buffer_size": 1024,
    },
    "vad": {
        "energy_threshold": 300.0,
        "sensitivity": 0.5,
        "min_speech_duration_ms": 100.0,
        "min_silence_duration_ms": 400.0,
        "adaptive_noise_floor": True,
    },
    "stt": {
        "model_name": "base",
        "language": "en",
        "beam_size": 5,
        "partial_latency_target_ms": 300.0,
        "final_latency_target_ms": 700.0,
    },
    "llm": {
        "model_name": "gemini-2.5-flash",
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 2048,
        "first_token_target_ms": 800.0,
    },
    "tts": {
        "voice_name": "en-US-AvaNeural",
        "speaking_rate": 1.0,
        "volume": 1.0,
        "playback_start_latency_target_ms": 1000.0,
    },
    "memory": {
        "max_history_turns": 20,
        "vector_search_top_k": 5,
    },
    "workflow": {
        "max_concurrent_tasks": 10,
        "task_timeout_seconds": 60.0,
    },
    "browser": {
        "headless": True,
        "user_agent": "AURA-BrowserAgent/1.0",
    },
    "desktop": {
        "automation_enabled": True,
        "screen_capture_interval_ms": 500,
    },
    "vision": {
        "enabled": True,
        "max_image_resolution": [1920, 1080],
    },
    "logging": {
        "level": "INFO",
        "structured_json": True,
    },
    "monitoring": {
        "collection_interval_seconds": 5.0,
        "exporter_format": "json",
    },
    "security": {
        "auth_enabled": True,
        "rate_limit_per_minute": 60,
    },
    "plugins": {
        "sandbox_enabled": True,
        "plugin_directory": "plugins",
    },
    "cloud": {
        "sync_enabled": True,
        "endpoint": "https://cloud.aura.ai",
    },
    "developer_mode": {
        "enabled": True,
        "hot_reload": True,
    },
}

DEFAULT_FEATURE_FLAGS: Dict[str, Dict[str, Any]] = {
    "streaming_voice": {"enabled": True, "description": "Streaming audio pipeline"},
    "interruptions": {"enabled": True, "description": "Full duplex conversational interruption"},
    "browser_agent": {"enabled": True, "description": "Autonomous browser agent"},
    "developer_mode": {"enabled": True, "description": "Developer platform capabilities"},
    "knowledge_engine": {"enabled": True, "description": "Knowledge graph and ingestion"},
    "plugin_sdk": {"enabled": True, "description": "Third party plugin ecosystem"},
    "cloud_sync": {"enabled": True, "description": "Multi-device cloud synchronization"},
    "vision": {"enabled": True, "description": "Computer vision capabilities"},
    "memory": {"enabled": True, "description": "Long-term episodic and semantic memory"},
    "workflow_engine": {"enabled": True, "description": "DAG workflow task engine"},
}
