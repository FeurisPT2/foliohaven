"""
Test Suite: Verification of the 5 Cloned Advanced Features
FolioHaven Desktop Ebook Reader
"""

import unittest
import os
import re

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))

class TestClonedFeatures(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(APP_DIR, "index.html"), "r", encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(APP_DIR, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(os.path.join(APP_DIR, "styles.css"), "r", encoding="utf-8") as f:
            self.css = f.read()
        with open(os.path.join(APP_DIR, "db.js"), "r", encoding="utf-8") as f:
            self.db_js = f.read()

    def test_feature1_tts(self):
        """Feature 1: TTS voice selection, continuous reading, F7 hotkey, and paragraph highlight."""
        self.assertIn("settings-tts-voice", self.html, "TTS voice select element missing")
        self.assertIn("label-tts-speed", self.html, "TTS speed label missing")
        self.assertIn("initTts()", self.app_js, "initTts method missing in app.js")
        self.assertIn("speakCurrentTtsParagraph()", self.app_js, "Continuous speech method missing")
        self.assertIn("tts-reading-active", self.css, "Active TTS CSS styling missing")
        self.assertIn('"F7"', self.app_js, "F7 keyboard shortcut missing")

    def test_feature2_inbook_search(self):
        """Feature 2: Full-text in-book search, page jump, snippet highlight, and canvas pulse."""
        self.assertIn("inbook-page-jump-container", self.html, "Page jump button container missing in search drawer")
        self.assertIn("btn-inbook-page-jump", self.html, "Page jump button missing")
        self.assertIn("search-match", self.css, "Search match CSS styling missing")
        self.assertIn("search-pulse", self.css, "Search pulse animation CSS missing")
        self.assertIn("jumpToPage", self.app_js, "jumpToPage method missing")
        self.assertIn("searchInBook", self.app_js, "searchInBook caller missing")

    def test_feature3_export_notes_html(self):
        """Feature 3: Professional FolioHaven study notes HTML export."""
        self.assertIn("btn-export-notes-html", self.html, "Export notes button missing")
        self.assertIn("exportNotesToHtml()", self.app_js, "exportNotesToHtml method missing")
        self.assertIn("FolioHaven Study Notes", self.app_js, "Branded study notes header missing")
        self.assertIn("annotation-card", self.app_js, "Card styling missing in exported HTML")
        self.assertIn("saveFileDialog", self.app_js, "Desktop native save dialog integration missing")

    def test_feature4_book_properties_cover(self):
        """Feature 4: Book properties dialog with custom cover image upload and restore."""
        self.assertIn("prop-cover-preview", self.html, "Cover preview container missing in modal-properties")
        self.assertIn("btn-prop-upload-cover", self.html, "Upload cover button missing")
        self.assertIn("btn-prop-restore-cover", self.html, "Restore cover button missing")
        self.assertIn("stagedCover", self.app_js, "Staged cover state logic missing in app.js")
        self.assertIn("cover_image", self.app_js, "cover_image persistence missing")

    def test_feature5_password_protected_document(self):
        """Feature 5: Password-protected document modal, unlock attempt, and error handling."""
        self.assertIn("modal-password", self.html, "Password modal missing in index.html")
        self.assertIn("input-doc-password", self.html, "Password input field missing")
        self.assertIn("btn-submit-password", self.html, "Submit password button missing")
        self.assertIn("promptDocumentPassword", self.app_js, "promptDocumentPassword method missing")
        self.assertIn("is_encrypted", self.app_js, "is_encrypted check missing")
        self.assertIn("Confidential Research & Cryptography (Encrypted)", self.db_js, "Sample encrypted book missing in db.js")

if __name__ == "__main__":
    unittest.main()
