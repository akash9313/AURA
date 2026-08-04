from enum import Enum


class ApplicationEvent(Enum):
    APPLICATION_LAUNCHED = "application_launched"
    APPLICATION_READY = "application_ready"
    APPLICATION_CLOSED = "application_closed"
    APPLICATION_CRASHED = "application_crashed"
    APPLICATION_RESTARTED = "application_restarted"
    APPLICATION_NOT_FOUND = "application_not_found"
    RESOURCE_UPDATED = "resource_updated"
