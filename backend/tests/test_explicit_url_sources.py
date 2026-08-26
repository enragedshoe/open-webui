import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from open_webui.retrieval.utils import get_sources_from_items


class ExplicitUrlSourceTests(unittest.IsolatedAsyncioTestCase):
    @patch('open_webui.retrieval.utils.Config.get', new_callable=AsyncMock, return_value=False)
    @patch('open_webui.retrieval.utils.get_content_from_url', new_callable=AsyncMock)
    async def test_exact_url_content_retains_source_provenance(self, get_content, _config_get):
        url = 'https://example.com/game/'
        get_content.return_value = ('game source', [SimpleNamespace()])

        sources = await get_sources_from_items(
            request=object(),
            items=[{'type': 'url', 'url': url, 'name': url, 'context': 'full'}],
            queries=['extract the game'],
            embedding_function=None,
            k=4,
            reranking_function=None,
            k_reranker=4,
            r=0.0,
            hybrid_bm25_weight=0.0,
            hybrid_search=False,
            full_context=True,
            user=None,
        )

        self.assertEqual(sources[0]['document'], ['game source'])
        self.assertEqual(sources[0]['metadata'][0]['source'], url)
        get_content.assert_awaited_once_with(unittest.mock.ANY, url)

    @patch('open_webui.retrieval.utils.Config.get', new_callable=AsyncMock, return_value=False)
    @patch('open_webui.retrieval.utils.get_content_from_url', new_callable=AsyncMock)
    async def test_bad_exact_url_does_not_discard_other_search_docs(self, get_content, _config_get):
        get_content.side_effect = ValueError('blocked URL')
        docs_item = {
            'type': 'web_search',
            'docs': [
                {
                    'content': 'search fallback',
                    'metadata': {'source': 'https://search.example/result'},
                }
            ],
        }

        sources = await get_sources_from_items(
            request=object(),
            items=[docs_item, {'type': 'url', 'url': 'http://127.0.0.1/', 'name': 'blocked'}],
            queries=['fallback'],
            embedding_function=None,
            k=4,
            reranking_function=None,
            k_reranker=4,
            r=0.0,
            hybrid_bm25_weight=0.0,
            hybrid_search=False,
            full_context=False,
            user=None,
        )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]['document'], ['search fallback'])

    @patch('open_webui.retrieval.utils.Config.get', new_callable=AsyncMock, return_value=False)
    @patch('open_webui.retrieval.utils.get_content_from_url', new_callable=AsyncMock)
    async def test_exact_url_fetch_does_not_hide_cancellation(self, get_content, _config_get):
        get_content.side_effect = asyncio.CancelledError()

        with self.assertRaises(asyncio.CancelledError):
            await get_sources_from_items(
                request=object(),
                items=[{'type': 'url', 'url': 'https://example.com/', 'name': 'cancelled'}],
                queries=['cancel'],
                embedding_function=None,
                k=4,
                reranking_function=None,
                k_reranker=4,
                r=0.0,
                hybrid_bm25_weight=0.0,
                hybrid_search=False,
                full_context=False,
                user=None,
            )


if __name__ == '__main__':
    unittest.main()
