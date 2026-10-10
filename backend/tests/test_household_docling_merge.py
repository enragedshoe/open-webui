"""Regressions for the household OCR fallback combined with upstream null handling."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from open_webui.retrieval.loaders.main import DoclingLoader


class HouseholdDoclingMergeTests(unittest.TestCase):
    def load_response(self, payload, fallback):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.pdf'
            path.write_bytes(b'%PDF-1.4\n')
            loader = DoclingLoader('http://isolated.invalid', file_path=str(path), mime_type='application/pdf')
            response = Mock(ok=True)
            response.json.return_value = payload
            with patch('open_webui.retrieval.loaders.main.requests.post', return_value=response), patch.object(
                loader, '_load_image_only_pdf_ocr', return_value=fallback
            ):
                return loader.load()

    def test_null_markdown_preserves_full_page_ocr(self):
        docs = self.load_response({'status': 'success', 'document': {'md_content': None}}, 'Synthetic scanned text')
        self.assertIn('Synthetic scanned text', docs[0].page_content)
        self.assertEqual(docs[0].metadata['Content-Type'], 'application/pdf')

    def test_structured_text_is_retained_alongside_ocr(self):
        docs = self.load_response({'status': 'success', 'document': {'md_content': 'Structured table'}}, 'Scanned heading')
        self.assertIn('Structured table', docs[0].page_content)
        self.assertIn('Scanned heading', docs[0].page_content)

    def test_provider_failure_is_not_masked_by_ocr(self):
        with self.assertRaisesRegex(Exception, 'conversion status failure'):
            self.load_response({'status': 'failure', 'errors': [{'error_message': 'synthetic failure'}]}, 'Fallback')
