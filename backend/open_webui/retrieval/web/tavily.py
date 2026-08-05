from __future__ import annotations

import logging
import re

import requests
from open_webui.retrieval.web.main import SearchResult, get_filtered_results

log = logging.getLogger(__name__)


def _requested_domains(query: str) -> list[str]:
    """Treat hostnames in a generated query as explicit source preferences."""
    domains = re.findall(
        r'(?<![\w@])(?:https?://)?(?:www\.)?'
        r'([a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9-]+)*\.[a-z]{2,})',
        query,
        flags=re.IGNORECASE,
    )
    return list(dict.fromkeys(domain.lower() for domain in domains))[:5]


def search_tavily(
    api_key: str,
    query: str,
    count: int,
    filter_list: list[str | None] = None,
    # **kwargs,
) -> list[SearchResult]:
    """Search using Tavily's Search API and return the results as a list of SearchResult objects.

    Args:
        api_key (str): A Tavily Search API key
        query (str): The query to search for
        count (int): The maximum number of results to return

    Returns:
        A list of SearchResult objects.
    """
    url = 'https://api.tavily.com/search'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    data = {
        'query': query,
        'max_results': count,
        'search_depth': 'advanced',
    }
    requested_domains = _requested_domains(query)
    if requested_domains:
        data['include_domains'] = requested_domains
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    json_response = response.json()

    results = json_response.get('results', [])
    if filter_list:
        results = get_filtered_results(results, filter_list)

    return [
        SearchResult(
            link=result['url'],
            title=result.get('title', ''),
            snippet=result.get('content'),
        )
        for result in results
    ]
