import logging
from core.events import Event
from core.service import Service
from browser.manager import BrowserManager

logger = logging.getLogger("AURA.BrowserService")


class BrowserService(Service):
    """
    BrowserService connects the BrowserManager facade to the AURA EventBus.
    """

    def __init__(self, bus, manager: BrowserManager = None):
        super().__init__(bus)
        self.manager = manager if manager is not None else BrowserManager()

    def start(self) -> None:
        logger.info("Browser Agent Service Started")
        self.bus.publish(Event.BROWSER_STARTED, {"status": "running"})

    def stop(self) -> None:
        logger.info("Browser Agent Service Stopped")

    def open_url(self, url: str):
        res = self.manager.open_url(url)
        if res.success:
            self.bus.publish(Event.PAGE_OPENED, {"url": url, "title": res.title})
        return res

    def search_web(self, query: str):
        res = self.manager.search_web(query)
        if res.success:
            self.bus.publish(Event.PAGE_OPENED, {"query": query, "url": res.url})
        return res

    def extract_page(self, url: str = None):
        res = self.manager.extract_page(url)
        if res.success:
            self.bus.publish(Event.PAGE_EXTRACTED, {"url": res.url, "title": res.title})
        return res

    def fill_form(self, form_data: dict):
        res = self.manager.fill_form(form_data)
        if res.success:
            self.bus.publish(Event.FORM_FILLED, {"form_data": form_data})
        return res

    def click_element(self, selector: str):
        res = self.manager.click_element(selector)
        if res.success:
            self.bus.publish(Event.ELEMENT_CLICKED, {"selector": selector})
        return res

    def download_file(self, url: str, output_path: str = "downloaded_file"):
        res = self.manager.download_file(url, output_path)
        if res.success:
            self.bus.publish(Event.DOWNLOAD_COMPLETED, {"url": url, "files": res.downloads})
        return res
