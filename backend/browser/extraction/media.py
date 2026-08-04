"""
Media Asset Extractor.
Extracts images, alt text, captions, video embeds, and audio sources from DOM tree.
"""

import logging
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import ExtractedImage, ExtractedVideo

logger = logging.getLogger("AURA.Browser.Extraction.Media")


class MediaExtractor:
    """Extracts images and videos from DOM tree."""

    VIDEO_EMBED_DOMAINS = ("youtube.com", "youtu.be", "vimeo.com", "dailymotion.com", "wistia.com")

    def extract_media(
        self, root: DOMNode, base_url: str = ""
    ) -> Tuple[List[ExtractedImage], List[ExtractedVideo]]:
        """
        Extract all images and video elements.

        Returns:
            Tuple of (List[ExtractedImage], List[ExtractedVideo])
        """
        images = self._extract_images(root, base_url)
        videos = self._extract_videos(root, base_url)
        return images, videos

    def _extract_images(self, root: DOMNode, base_url: str) -> List[ExtractedImage]:
        img_nodes = root.find_all("img")
        extracted: List[ExtractedImage] = []
        seen_srcs = set()

        for img in img_nodes:
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if not src or src.startswith("data:image"):  # Skip tiny inline base64 icons
                continue

            full_src = urljoin(base_url, src) if base_url else src
            if full_src in seen_srcs:
                continue
            seen_srcs.add(full_src)

            alt = img.get_attribute("alt") or ""
            title = img.get_attribute("title")
            caption = self._find_figure_caption(img)

            # Dimensions if specified
            width = self._parse_dim(img.get_attribute("width"))
            height = self._parse_dim(img.get_attribute("height"))

            extracted.append(
                ExtractedImage(
                    src=full_src,
                    alt=alt.strip(),
                    caption=caption,
                    title=title,
                    width=width,
                    height=height,
                )
            )

        logger.debug(f"Extracted {len(extracted)} images")
        return extracted

    def _extract_videos(self, root: DOMNode, base_url: str) -> List[ExtractedVideo]:
        extracted: List[ExtractedVideo] = []
        seen_srcs = set()

        # HTML5 <video> tags
        video_nodes = root.find_all("video")
        for v in video_nodes:
            src = v.get_attribute("src")
            poster = v.get_attribute("poster")
            if poster and base_url:
                poster = urljoin(base_url, poster)

            if not src:
                # Check <source> children
                sources = v.find_all("source")
                if sources:
                    src = sources[0].get_attribute("src")

            if src:
                full_src = urljoin(base_url, src) if base_url else src
                if full_src not in seen_srcs:
                    seen_srcs.add(full_src)
                    extracted.append(
                        ExtractedVideo(
                            src=full_src,
                            poster=poster,
                            title=v.get_attribute("title"),
                            provider="html5",
                        )
                    )

        # <iframe> video embeds (e.g. YouTube, Vimeo)
        iframe_nodes = root.find_all("iframe")
        for iframe in iframe_nodes:
            src = iframe.get_attribute("src")
            if not src:
                continue

            parsed = urlparse(src)
            domain = parsed.netloc.lower()

            if any(embed_domain in domain for embed_domain in self.VIDEO_EMBED_DOMAINS):
                full_src = urljoin(base_url, src) if base_url else src
                if full_src not in seen_srcs:
                    seen_srcs.add(full_src)
                    provider = "youtube" if "youtube" in domain or "youtu.be" in domain else "vimeo"
                    extracted.append(
                        ExtractedVideo(
                            src=full_src,
                            title=iframe.get_attribute("title"),
                            provider=provider,
                        )
                    )

        logger.debug(f"Extracted {len(extracted)} videos")
        return extracted

    def _find_figure_caption(self, node: DOMNode) -> Optional[str]:
        """Find <figcaption> if image is inside a <figure> tag."""
        parent = node.parent
        while parent and parent.tag != "root":
            if parent.tag == "figure":
                caption_node = parent.find_first("figcaption")
                if caption_node:
                    return caption_node.get_text().strip()
                break
            parent = parent.parent
        return None

    def _parse_dim(self, val: Optional[str]) -> Optional[int]:
        if not val:
            return None
        try:
            return int("".join(filter(str.isdigit, val)))
        except ValueError:
            return None
