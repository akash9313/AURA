"""
Backwards Compatibility Proxy for Browser Subsystem Events.
Redirects to backend/browser/events/browser_events.py.
"""

from browser.events.browser_events import BrowserEvent, BrowserEventType

__all__ = ["BrowserEvent", "BrowserEventType"]
