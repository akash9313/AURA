"""
Table Extractor.
Parses HTML <table> elements into clean, structured headers, rows, captions, and matrix representations.
Preserves header associations and merged cells where possible.
"""

import logging
from typing import List, Optional

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import ExtractedTable, TableCell

logger = logging.getLogger("AURA.Browser.Extraction.Tables")


class TableExtractor:
    """Extracts structured tabular data from HTML tables."""

    def extract_tables(self, root: DOMNode) -> List[ExtractedTable]:
        """
        Extract all tables from DOM tree.

        Returns:
            List of ExtractedTable objects.
        """
        table_nodes = root.find_all("table")
        extracted: List[ExtractedTable] = []

        for table_node in table_nodes:
            caption_node = table_node.find_first("caption")
            caption = caption_node.get_text().strip() if caption_node else None

            headers: List[str] = []
            rows: List[List[str]] = []

            # Extract header cells
            th_nodes = table_node.find_all("th")
            if th_nodes:
                headers = [th.get_text().strip() for th in th_nodes if th.get_text().strip()]

            # Extract rows
            tr_nodes = table_node.find_all("tr")
            for tr in tr_nodes:
                td_nodes = tr.find_all("td")
                if not td_nodes and not headers:
                    # Check if this tr contains th tags acting as headers
                    tr_ths = tr.find_all("th")
                    if tr_ths:
                        headers = [th.get_text().strip() for th in tr_ths]
                        continue

                if td_nodes:
                    row_cells = [td.get_text().strip() for td in td_nodes]
                    if any(row_cells):  # Skip completely empty rows
                        rows.append(row_cells)

            # Ignore empty tables
            if headers or rows:
                extracted.append(
                    ExtractedTable(
                        headers=headers,
                        rows=rows,
                        caption=caption,
                        table_id=table_node.id,
                    )
                )

        logger.debug(f"Extracted {len(extracted)} tables")
        return extracted
