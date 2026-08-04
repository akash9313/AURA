"""
DOM Intelligence & Content Extraction Engine Unit & Integration Tests.
Tests real-world website HTML patterns: News, Blogs, Documentation, Wikipedia, GitHub, and E-commerce.
Validates malformed HTML handling, clutter pruning, metadata, links, forms, tables, media, headings, accessibility, and performance.
"""

import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from browser.extraction.models import (
    FieldType,
    LinkType,
    StructuredPageContent,
)
from browser.extraction.events import ExtractionEvent
from browser.extraction.dom_parser import DOMParser
from browser.extraction.metadata import MetadataExtractor
from browser.extraction.readability import ReadabilityExtractor
from browser.extraction.headings import HeadingsExtractor
from browser.extraction.links import LinkExtractor
from browser.extraction.media import MediaExtractor
from browser.extraction.tables import TableExtractor
from browser.extraction.forms import FormExtractor
from browser.extraction.accessibility import AccessibilityExtractor
from browser.extraction.content_extractor import ContentExtractor
from browser.extraction.service import DOMExtractionService


# ==============================================================================
# Test Fixtures for Real-World Sites
# ==============================================================================

NEWS_SITE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Breakthrough in Quantum Computing - Tech News</title>
    <meta name="description" content="Scientists achieve quantum supremacy milestone.">
    <meta name="author" content="Jane Doe">
    <meta property="og:title" content="Quantum Breakthrough 2026">
    <meta property="og:type" content="article">
</head>
<body>
    <header class="header-nav">
        <nav><a href="/home">Home</a> | <a href="/news">News</a></nav>
    </header>

    <aside class="sidebar-ad">
        <div class="ad-banner">Buy Super Computer Now!</div>
    </aside>

    <main>
        <article>
            <h1>Breakthrough in Quantum Computing</h1>
            <p class="byline">By Jane Doe | Published August 2026</p>
            
            <p>Researchers at AURA Labs have unveiled a 10,000-qubit fault-tolerant quantum processor, marking a monumental shift in computational capability.</p>

            <h2>Performance Metrics</h2>
            <p>The new chip executes complex optimization algorithms in milliseconds compared to traditional supercomputers requiring centuries.</p>
            
            <blockquote class="quote">"This is the transistors moment for quantum processing," said Dr. Smith.</blockquote>

            <ul>
                <li>10,000 Logical Qubits</li>
                <li>99.99% Gate Fidelity</li>
                <li>Cryogenic Control Module</li>
            </ul>

            <figure>
                <img src="/images/quantum_chip.jpg" alt="Quantum Processor Chip" width="800" height="600">
                <figcaption>AURA 10,000 Qubit Quantum Processor in Dilution Refrigerator</figcaption>
            </figure>

            <pre><code class="python"># Sample Quantum Gate Execution
import aura_quantum as aq
circuit = aq.Circuit(qubits=10000)
circuit.h(0)
result = circuit.measure_all()
</code></pre>
        </article>
    </main>

    <footer class="footer-banner">
        <p>&copy; 2026 Tech News Inc. All rights reserved.</p>
        <div class="cookie-notice">We use cookies for tracking.</div>
    </footer>
</body>
</html>
"""

BLOG_SITE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>10 Best Python Best Practices for 2026</title>
    <meta name="description" content="Boost python code quality with these tips.">
</head>
<body>
    <article>
        <h1>10 Best Python Best Practices for 2026</h1>
        <p>Python continues to evolve as the dominant language for AI systems. Here are essential patterns for modern Python 3.14 development.</p>

        <h2>1. Strict Type Annotations</h2>
        <p>Always annotate function signatures to enable static analysis with mypy and IDE Intellisense.</p>

        <h2>2. AsyncIO Task Supervision</h2>
        <p>Use structured concurrency and TaskGroups to avoid unhandled background task exceptions.</p>

        <a href="https://docs.python.org" rel="nofollow" target="_blank">Official Python Documentation</a>
        <a href="/downloads/cheat_sheet.pdf" download>Download PDF Cheat Sheet</a>
    </article>
</body>
</html>
"""

WIKIPEDIA_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Artificial Intelligence - Wikipedia</title>
</head>
<body>
    <div id="content" class="mw-body" role="main">
        <h1 id="firstHeading">Artificial Intelligence</h1>
        <div id="bodyContent">
            <p>Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to intelligence of humans.</p>
            
            <h2>History</h2>
            <p>The field of AI research was founded at a workshop held on the campus of Dartmouth College during the summer of 1956.</p>

            <h3>The Dartmouth Conference</h3>
            <p>Organized by John McCarthy, Marvin Minsky, Nathaniel Rochester, and Claude Shannon.</p>

            <h2>Comparison of Paradigms</h2>
            <table class="wikitable">
                <caption>AI Approach Comparison</caption>
                <tr>
                    <th>Paradigm</th>
                    <th>Strengths</th>
                    <th>Weaknesses</th>
                </tr>
                <tr>
                    <td>Symbolic AI</td>
                    <td>Explainable rules</td>
                    <td>Brittle, non-scalable</td>
                </tr>
                <tr>
                    <td>Deep Learning</td>
                    <td>Pattern recognition</td>
                    <td>Black box, data-hungry</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

GITHUB_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>aura/aura-os: Next-Gen AI Operating System</title>
</head>
<body>
    <div class="repository-content">
        <h1>aura-os</h1>
        <p>Autonomous AI Operating System Kernel and Infrastructure.</p>

        <div class="file-navigation">
            <a href="https://github.com/aura/aura-os/archive/refs/heads/main.zip">Download ZIP</a>
        </div>

        <form id="search-repo" action="/search" method="GET">
            <label for="q">Search Repository</label>
            <input type="text" id="q" name="q" placeholder="Search code..." required>
            <button type="submit">Search</button>
        </form>
    </div>
</body>
</html>
"""

ECOMMERCE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>AURA Neural Headset Pro - Tech Store</title>
    <meta property="og:image" content="https://store.example.com/headset.jpg">
</head>
<body>
    <div class="product-detail">
        <h1>AURA Neural Headset Pro</h1>
        <span class="price">$499.99</span>
        <p>Direct brain-computer interface with ultra-low latency sub-5ms synaptic sync.</p>

        <form id="add-to-cart-form" action="/cart/add" method="POST">
            <input type="hidden" name="product_id" value="sku_99218">
            <label for="color">Choose Color:</label>
            <select id="color" name="color">
                <option value="black">Matte Black</option>
                <option value="silver">Cyber Silver</option>
            </select>

            <label for="qty">Quantity:</label>
            <input type="number" id="qty" name="quantity" value="1" min="1">

            <button type="submit" id="add-btn">Add to Cart</button>
        </form>

        <video src="https://store.example.com/demo.mp4" poster="https://store.example.com/poster.jpg" title="Product Demo">
            <source src="https://store.example.com/demo.mp4" type="video/mp4">
        </video>
    </div>
</body>
</html>
"""

MALFORMED_HTML = """
<html>
<body>
    <h1>Unclosed Header
    <p>Paragraph without proper ending tag
    <div><span>Nested text <b>bold without end
    <a href="https://example.com">Link Text
    <table><tr><td>Cell 1<td>Cell 2</tr></table>
</body>
"""


# ==============================================================================
# Unit Tests
# ==============================================================================

class TestDOMParser(unittest.TestCase):
    """Tests for DOMParser and DOMNode tree construction."""

    def setUp(self):
        self.parser = DOMParser()

    def test_parse_simple_html(self):
        root = self.parser.parse("<div><p>Hello World</p></div>", strip_clutter=False)
        self.assertIsNotNone(root)
        div = root.find_first("div")
        self.assertIsNotNone(div)
        self.assertIn("Hello World", div.get_text())

    def test_prune_clutter_ads_nav_footer(self):
        root = self.parser.parse(NEWS_SITE_HTML, strip_clutter=True)
        # Nav and footer tags should be pruned
        self.assertIsNone(root.find_first("nav"))
        self.assertIsNone(root.find_first("footer"))
        self.assertIsNone(root.find_first("aside"))


class TestMetadataExtractor(unittest.TestCase):
    """Tests for metadata extraction."""

    def setUp(self):
        self.extractor = MetadataExtractor()
        self.parser = DOMParser()

    def test_extract_news_metadata(self):
        root = self.parser.parse(NEWS_SITE_HTML, strip_clutter=False)
        meta = self.extractor.extract_metadata(root, base_url="https://technews.com/article1")
        self.assertEqual(meta.author, "Jane Doe")
        self.assertEqual(meta.description, "Scientists achieve quantum supremacy milestone.")
        self.assertEqual(meta.open_graph.get("title"), "Quantum Breakthrough 2026")
        self.assertEqual(meta.language, "en")


class TestReadabilityExtractor(unittest.TestCase):
    """Tests for readability article extraction and reading statistics."""

    def setUp(self):
        self.extractor = ReadabilityExtractor()
        self.parser = DOMParser()

    def test_extract_news_article(self):
        root = self.parser.parse(NEWS_SITE_HTML, strip_clutter=True)
        article = self.extractor.extract_article(root, title_hint="Breakthrough in Quantum Computing")
        self.assertIn("10,000-qubit fault-tolerant quantum processor", article.text_content)
        self.assertGreaterEqual(len(article.paragraphs), 2)
        self.assertGreaterEqual(len(article.lists), 1)
        self.assertGreaterEqual(len(article.quotes), 1)
        self.assertGreaterEqual(len(article.code_blocks), 1)

    def test_calculate_reading_stats(self):
        root = self.parser.parse(NEWS_SITE_HTML, strip_clutter=True)
        article = self.extractor.extract_article(root)
        stats = self.extractor.calculate_reading_stats(article)
        self.assertGreater(stats.word_count, 10)
        self.assertGreater(stats.sentence_count, 0)
        self.assertGreaterEqual(stats.estimated_reading_time_minutes, 0.0)


class TestHeadingsExtractor(unittest.TestCase):
    """Tests for document outline hierarchy extraction."""

    def setUp(self):
        self.extractor = HeadingsExtractor()
        self.parser = DOMParser()

    def test_wikipedia_heading_hierarchy(self):
        root = self.parser.parse(WIKIPEDIA_HTML, strip_clutter=False)
        headings = self.extractor.extract_headings(root)
        self.assertEqual(len(headings), 1)  # Top level H1
        h1 = headings[0]
        self.assertEqual(h1.text, "Artificial Intelligence")
        self.assertGreaterEqual(len(h1.children), 2)  # H2: History, Comparison of Paradigms
        history_h2 = h1.children[0]
        self.assertEqual(history_h2.text, "History")
        self.assertEqual(len(history_h2.children), 1)  # H3: The Dartmouth Conference


class TestLinkExtractor(unittest.TestCase):
    """Tests for hyperlink extraction and classification."""

    def setUp(self):
        self.extractor = LinkExtractor()
        self.parser = DOMParser()

    def test_blog_link_classification(self):
        root = self.parser.parse(BLOG_SITE_HTML, strip_clutter=False)
        links = self.extractor.extract_links(root, base_url="https://myblog.com/post-1")
        self.assertEqual(len(links), 2)

        doc_link = next(l for l in links if "docs.python.org" in l.url)
        self.assertEqual(doc_link.link_type, LinkType.NOFOLLOW)
        self.assertTrue(doc_link.is_nofollow)

        pdf_link = next(l for l in links if "cheat_sheet.pdf" in l.url)
        self.assertEqual(pdf_link.link_type, LinkType.DOWNLOAD)


class TestMediaExtractor(unittest.TestCase):
    """Tests for image and video extraction."""

    def setUp(self):
        self.extractor = MediaExtractor()
        self.parser = DOMParser()

    def test_news_image_with_caption(self):
        root = self.parser.parse(NEWS_SITE_HTML, strip_clutter=False)
        images, videos = self.extractor.extract_media(root, base_url="https://technews.com/article1")
        self.assertEqual(len(images), 1)
        img = images[0]
        self.assertEqual(img.alt, "Quantum Processor Chip")
        self.assertIn("Dilution Refrigerator", img.caption)
        self.assertEqual(img.width, 800)
        self.assertEqual(img.height, 600)

    def test_ecommerce_video(self):
        root = self.parser.parse(ECOMMERCE_HTML, strip_clutter=False)
        images, videos = self.extractor.extract_media(root, base_url="https://store.example.com/product/1")
        self.assertEqual(len(videos), 1)
        v = videos[0]
        self.assertIn("demo.mp4", v.src)
        self.assertIn("poster.jpg", v.poster)


class TestTableExtractor(unittest.TestCase):
    """Tests for tabular data extraction."""

    def setUp(self):
        self.extractor = TableExtractor()
        self.parser = DOMParser()

    def test_wikipedia_table_extraction(self):
        root = self.parser.parse(WIKIPEDIA_HTML, strip_clutter=False)
        tables = self.extractor.extract_tables(root)
        self.assertEqual(len(tables), 1)
        t = tables[0]
        self.assertEqual(t.caption, "AI Approach Comparison")
        self.assertEqual(t.headers, ["Paradigm", "Strengths", "Weaknesses"])
        self.assertEqual(len(t.rows), 2)
        self.assertEqual(t.rows[0], ["Symbolic AI", "Explainable rules", "Brittle, non-scalable"])


class TestFormExtractor(unittest.TestCase):
    """Tests for form and button extraction."""

    def setUp(self):
        self.extractor = FormExtractor()
        self.parser = DOMParser()

    def test_ecommerce_form_extraction(self):
        root = self.parser.parse(ECOMMERCE_HTML, strip_clutter=False)
        forms, buttons = self.extractor.extract_forms_and_buttons(root)
        self.assertEqual(len(forms), 1)
        f = forms[0]
        self.assertEqual(f.form_id, "add-to-cart-form")
        self.assertEqual(f.method, "POST")
        self.assertGreaterEqual(len(f.fields), 3)  # hidden product_id, select color, number quantity

        color_field = next(field for field in f.fields if field.name == "color")
        self.assertEqual(color_field.field_type, FieldType.SELECT)
        self.assertEqual(color_field.options, ["Matte Black", "Cyber Silver"])
        self.assertEqual(color_field.label, "Choose Color:")

    def test_github_form_extraction(self):
        root = self.parser.parse(GITHUB_HTML, strip_clutter=False)
        forms, buttons = self.extractor.extract_forms_and_buttons(root)
        self.assertEqual(len(forms), 1)
        f = forms[0]
        self.assertEqual(f.action, "/search")
        q_field = f.fields[0]
        self.assertEqual(q_field.name, "q")
        self.assertTrue(q_field.required)
        self.assertEqual(q_field.placeholder, "Search code...")


class TestAccessibilityExtractor(unittest.TestCase):
    """Tests for accessibility auditing."""

    def setUp(self):
        self.extractor = AccessibilityExtractor()
        self.parser = DOMParser()
        self.headings_extractor = HeadingsExtractor()

    def test_accessibility_audit(self):
        root = self.parser.parse(WIKIPEDIA_HTML, strip_clutter=False)
        headings = self.headings_extractor.extract_headings(root)
        acc = self.extractor.extract_accessibility(root, headings)
        self.assertTrue(acc.heading_hierarchy_valid)
        self.assertGreaterEqual(len(acc.landmarks), 1)


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestContentExtractorIntegration(unittest.TestCase):
    """End-to-end integration tests for ContentExtractor and DOMExtractionService."""

    def setUp(self):
        self.extractor = ContentExtractor()

    def test_full_news_extraction(self):
        content = self.extractor.extract(NEWS_SITE_HTML, url="https://technews.com/quantum")
        self.assertIsInstance(content, StructuredPageContent)
        self.assertEqual(content.url, "https://technews.com/quantum")
        self.assertIn("Quantum", content.title)
        self.assertEqual(content.author, "Jane Doe")
        self.assertGreater(content.reading_stats.word_count, 10)
        self.assertEqual(len(content.images), 1)
        self.assertEqual(len(content.headings), 1)

    def test_malformed_html_recovery(self):
        content = self.extractor.extract(MALFORMED_HTML, url="https://example.com/bad")
        self.assertIsInstance(content, StructuredPageContent)
        self.assertTrue(content.title.strip() != "")
        self.assertGreaterEqual(len(content.links), 1)

    def test_extraction_performance_under_300ms(self):
        start = time.time()
        content = self.extractor.extract(NEWS_SITE_HTML, url="https://technews.com/quantum")
        elapsed_ms = (time.time() - start) * 1000
        self.assertLess(elapsed_ms, 300.0)
        self.assertLess(content.extraction_time_ms, 300.0)

    def test_dom_extraction_service_event_publishing(self):
        bus = MagicMock()
        service = DOMExtractionService(bus=bus)
        content = service.extract_from_html(NEWS_SITE_HTML, url="https://technews.com/quantum")
        self.assertIsInstance(content, StructuredPageContent)

        # Check published event names
        event_names = [call[0][0] for call in bus.publish.call_args_list]
        self.assertIn("content_extracted", event_names)
        self.assertIn("article_found", event_names)
        self.assertIn("media_found", event_names)


if __name__ == "__main__":
    unittest.main()
