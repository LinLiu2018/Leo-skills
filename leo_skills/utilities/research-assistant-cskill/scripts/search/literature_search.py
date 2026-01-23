#!/usr/bin/env python3
"""
Literature Search Module

Handles searching across multiple academic databases including:
- Semantic Scholar
- arXiv
- PubMed
- Crossref
- OpenAlex

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
except ImportError:
    requests = None

from utils.helpers import (
    handle_rate_limit, retry_on_failure, clean_text,
    parse_author_string, format_author_name
)


logger = logging.getLogger(__name__)


class SearchResult:
    """Data class for search results."""
    def __init__(
        self,
        paper_id: str,
        title: str,
        authors: List[str],
        year: int,
        abstract: str = "",
        citation_count: int = 0,
        url: str = "",
        doi: str = "",
        venue: str = "",
        topics: List[str] = None,
        source: str = ""
    ):
        self.paper_id = paper_id
        self.title = title
        self.authors = authors
        self.year = year
        self.abstract = abstract
        self.citation_count = citation_count
        self.url = url
        self.doi = doi
        self.venue = venue
        self.topics = topics or []
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'abstract': self.abstract,
            'citation_count': self.citation_count,
            'url': self.url,
            'doi': self.doi,
            'venue': self.venue,
            'topics': self.topics,
            'source': self.source,
        }


class BaseSearchEngine(ABC):
    """Abstract base class for search engines."""

    def __init__(self, config: Dict = None, cache = None):
        self.config = config or {}
        self.cache = cache
        self.session = None

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """Perform search and return results."""
        pass

    @abstractmethod
    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get detailed information for a specific paper."""
        pass

    def _init_session(self):
        """Initialize HTTP session."""
        if self.session is None and requests:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'ResearchAssistant/1.0',
                'Accept': 'application/json'
            })


class SemanticScholarSearch(BaseSearchEngine):
    """
    Search engine for Semantic Scholar API.
    https://www.semanticscholar.org/product/api
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, config: Dict = None, cache = None):
        super().__init__(config, cache)
        self.api_key = config.get('semantic_scholar_api_key')
        self._init_session()

    def _get_headers(self) -> Dict:
        headers = {
            'User-Agent': 'ResearchAssistant/1.0',
        }
        if self.api_key:
            headers['x-api-key'] = self.api_key
        return headers

    @handle_rate_limit
    @retry_on_failure(max_attempts=3)
    def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: Optional[tuple] = None,
        author: Optional[str] = None,
        venue: Optional[str] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search Semantic Scholar."""
        if not requests:
            logger.error("requests library not installed")
            return []

        # Build query parameters
        params = {
            'query': query,
            'limit': min(max_results, 100),
            'fields': 'paperId,title,authors,year,abstract,citationCount,url,doi,venue,topics',
            'offset': 0
        }

        if year_range:
            params['year'] = f"{year_range[0]}-{year_range[1]}"

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('data', []):
                result = self._parse_paper(item, source="Semantic Scholar")
                results.append(result)

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Semantic Scholar search error: {e}")
            return []

    def _parse_paper(self, item: Dict, source: str = "Semantic Scholar") -> SearchResult:
        """Parse Semantic Scholar paper response."""
        authors = []
        for author in item.get('authors', []):
            name = author.get('name', '')
            if name:
                authors.append(name)

        topics = [t.get('term', '') for t in item.get('topics', []) if t.get('term')]

        return SearchResult(
            paper_id=item.get('paperId', ''),
            title=item.get('title', ''),
            authors=authors,
            year=item.get('year', 0),
            abstract=item.get('abstract', ''),
            citation_count=item.get('citationCount', 0),
            url=item.get('url', ''),
            doi=item.get('doi', ''),
            venue=item.get('venue', ''),
            topics=topics,
            source=source
        )

    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get detailed paper information from Semantic Scholar."""
        if not requests:
            return None

        params = {
            'fields': 'paperId,title,authors,year,abstract,citationCount,url,doi,venue,topics,referenceCount'
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}",
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return self._parse_paper(data, source="Semantic Scholar")

        except requests.exceptions.RequestException as e:
            logger.error(f"Semantic Scholar get paper error: {e}")
            return None


class ArxivSearch(BaseSearchEngine):
    """
    Search engine for arXiv API.
    http://arxiv.org/help/api
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, config: Dict = None, cache = None):
        super().__init__(config, cache)
        self._init_session()

    @handle_rate_limit
    @retry_on_failure(max_attempts=3)
    def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: Optional[tuple] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search arXiv."""
        if not requests:
            logger.error("requests library not installed")
            return []

        # Build search query
        search_query = f'all:{query}'

        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': min(max_results, 50),
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}

            results = []
            for entry in root.findall('atom:entry', ns):
                result = self._parse_entry(entry, ns)
                results.append(result)

                if len(results) >= max_results:
                    break

            return results

        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []

    def _parse_entry(self, entry, ns) -> SearchResult:
        """Parse arXiv entry."""
        # Title
        title_elem = entry.find('atom:title', ns)
        title = clean_text(title_elem.text) if title_elem is not None else ""

        # Abstract
        summary_elem = entry.find('atom:summary', ns)
        abstract = clean_text(summary_elem.text) if summary_elem is not None else ""

        # Published date
        published_elem = entry.find('atom:published', ns)
        year = 0
        if published_elem is not None and published_elem.text:
            try:
                year = datetime.fromisoformat(
                    published_elem.text.replace('Z', '+00:00')
                ).year
            except ValueError:
                pass

        # Authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text)

        # Categories
        topics = []
        for category in entry.findall('arxiv:primary_category', ns):
            term = category.get('term', '')
            if term:
                topics.append(term)

        # ID and URL
        id_elem = entry.find('atom:id', ns)
        url = id_elem.text if id_elem is not None else ""

        # Extract arXiv ID
        arxiv_id = ""
        if url:
            arxiv_id = url.split('/')[-1]

        return SearchResult(
            paper_id=arxiv_id,
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            citation_count=0,  # arXiv doesn't provide citation count
            url=url,
            doi="",  # arXiv doesn't have DOI by default
            venue="arXiv",
            topics=topics,
            source="arXiv"
        )

    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get paper details by arXiv ID."""
        results = self.search(f"id:{paper_id}", max_results=1)
        return results[0] if results else None


class PubMedSearch(BaseSearchEngine):
    """
    Search engine for PubMed (NCBI E-utilities).
    https://www.ncbi.nlm.nih.gov/books/NBK25497/
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, config: Dict = None, cache = None):
        super().__init__(config, cache)
        self._init_session()

    @handle_rate_limit
    @retry_on_failure(max_attempts=3)
    def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: Optional[tuple] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search PubMed."""
        if not requests:
            logger.error("requests library not installed")
            return []

        try:
            # Step 1: Search for IDs
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': min(max_results, 100),
                'usehistory': 'y',
                'retmode': 'json'
            }

            if year_range:
                date_filter = f'("{year_range[0]}/01/01"[PDAT] : "{year_range[1]}/12/31"[PDAT])'
                search_params['term'] = f"{query} AND {date_filter}"

            response = self.session.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=search_params,
                timeout=30
            )
            response.raise_for_status()
            search_data = response.json()

            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return []

            # Step 2: Fetch summaries
            summary_params = {
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'json',
                'retmax': len(id_list)
            }

            response = self.session.get(
                f"{self.BASE_URL}/esummary.fcgi",
                params=summary_params,
                timeout=30
            )
            response.raise_for_status()
            summary_data = response.json()

            results = []
            for pubmed_id in id_list:
                docsum = summary_data.get('result', {}).get(pubmed_id, {})
                if docsum:
                    result = self._parse_docsum(docsum, pubmed_id)
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []

    def _parse_docsum(self, docsum: Dict, pubmed_id: str) -> SearchResult:
        """Parse PubMed document summary."""
        title = docsum.get('title', '')

        # Authors
        authors = []
        authors_list = docsum.get('authors', [])
        for author in authors_list:
            name = author.get('name', '')
            if name:
                authors.append(name)

        # Year
        pubdate = docsum.get('pubdate', '')
        year = 0
        if pubdate:
            try:
                year = int(pubdate.split()[0])
            except (ValueError, IndexError):
                pass

        # Journal
        source = docsum.get('source', '')

        # DOI
        article_ids = docsum.get('articleids', [])
        doi = ""
        for aid in article_ids:
            if aid.get('idtype') == 'doi':
                doi = aid.get('value', '')
                break

        # URL
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"

        return SearchResult(
            paper_id=pubmed_id,
            title=title,
            authors=authors,
            year=year,
            abstract="",  # PubMed summary doesn't include abstract
            citation_count=docsum.get('pmcrefcount', 0),
            url=url,
            doi=doi,
            venue=source,
            topics=[],  # PubMed uses MeSH terms, not topics
            source="PubMed"
        )

    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get paper details by PubMed ID."""
        results = self.search(f"PMID:{paper_id}", max_results=1)
        return results[0] if results else None


class CrossrefSearch(BaseSearchEngine):
    """
    Search engine for Crossref API.
    https://www.crossref.org/documentation/retrieve-metadata/rest-api/
    """

    BASE_URL = "https://api.crossref.org"

    def __init__(self, config: Dict = None, cache = None):
        super().__init__(config, cache)
        self._init_session()

    @handle_rate_limit
    @retry_on_failure(max_attempts=3)
    def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: Optional[tuple] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search Crossref."""
        if not requests:
            logger.error("requests library not installed")
            return []

        params = {
            'query': query,
            'rows': min(max_results, 100),
            'select': 'DOI,title,author,issued,container-title,abstract,URL,reference-count'
        }

        if year_range:
            params['filter'] = f'from-pub-date:{year_range[0]},until-pub-date:{year_range[1]}'

        try:
            response = self.session.get(
                f"{self.BASE_URL}/works",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('message', {}).get('items', []):
                result = self._parse_work(item)
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Crossref search error: {e}")
            return []

    def _parse_work(self, work: Dict) -> SearchResult:
        """Parse Crossref work."""
        # Title
        title = ""
        title_list = work.get('title', [])
        if title_list:
            title = title_list[0]

        # Authors
        authors = []
        for author in work.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        # Year
        year = 0
        issued = work.get('issued', {})
        date_parts = issued.get('date-parts', [])
        if date_parts:
            year = date_parts[0][0]

        # Journal/Venue
        container = work.get('container-title', [])
        venue = container[0] if container else ""

        # DOI and URL
        doi = work.get('DOI', '')
        url = work.get('URL', '')

        return SearchResult(
            paper_id=doi,
            title=title,
            authors=authors,
            year=year,
            abstract=work.get('abstract', ''),
            citation_count=work.get('reference-count', 0),
            url=url,
            doi=doi,
            venue=venue,
            topics=[],  # Crossref doesn't have topics
            source="Crossref"
        )

    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get paper details by DOI."""
        if not paper_id.startswith('10.'):
            return None

        try:
            response = self.session.get(
                f"{self.BASE_URL}/works/{paper_id}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return self._parse_work(data.get('message', {}))

        except Exception as e:
            logger.error(f"Crossref get paper error: {e}")
            return None


class OpenAlexSearch(BaseSearchEngine):
    """
    Search engine for OpenAlex API.
    https://docs.openalex.org/
    """

    BASE_URL = "https://api.openalex.org"

    def __init__(self, config: Dict = None, cache = None):
        super().__init__(config, cache)
        self.api_key = config.get('openalex_api_key')
        self._init_session()

    @handle_rate_limit
    @retry_on_failure(max_attempts=3)
    def search(
        self,
        query: str,
        max_results: int = 10,
        year_range: Optional[tuple] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search OpenAlex."""
        if not requests:
            logger.error("requests library not installed")
            return []

        # Build filter
        filters = []
        if year_range:
            filters.append(f"publication_year>={year_range[0]}")
            filters.append(f"publication_year<={year_range[1]}")

        filter_str = ",".join(filters) if filters else ""

        params = {
            'search': query,
            'per-page': min(max_results, 200),
            'filter': filter_str,
            'select': 'id,display_name,publication_year,abstract,doi,primary_location,authorships,referenced_works,cited_by_count,concepts'
        }

        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        try:
            response = self.session.get(
                f"{self.BASE_URL}/works",
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('results', []):
                result = self._parse_work(item)
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"OpenAlex search error: {e}")
            return []

    def _parse_work(self, work: Dict) -> SearchResult:
        """Parse OpenAlex work."""
        # Title
        title = work.get('display_name', '')

        # Authors
        authors = []
        for authorship in work.get('authorships', []):
            author = authorship.get('author', {})
            name = author.get('display_name', '')
            if name:
                authors.append(name)

        # Year
        year = work.get('publication_year', 0)

        # Abstract
        abstract = work.get('abstract', '')
        if not abstract:
            # Try to get from indexed location
            indexed = work.get('abstract_inverted_index', {})
            if indexed:
                # Reconstruct abstract (simplified)
                pass

        # DOI and URL
        doi = work.get('doi', '')
        primary_location = work.get('primary_location', {})
        landing_page_url = primary_location.get('landing_page_url', '')

        # Citation count
        cited_by_count = work.get('cited_by_count', 0)

        # Concepts (topics)
        concepts = work.get('concepts', [])
        topics = [c.get('display_name', '') for c in concepts if c.get('display_name')]

        # Venue
        venue = ""
        source = primary_location.get('source', {})
        if source:
            venue = source.get('display_name', '')

        return SearchResult(
            paper_id=work.get('id', '').split('/')[-1] if work.get('id') else '',
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            citation_count=cited_by_count,
            url=landing_page_url,
            doi=doi,
            venue=venue,
            topics=topics,
            source="OpenAlex"
        )

    def get_paper_details(self, paper_id: str) -> Optional[SearchResult]:
        """Get paper details by OpenAlex ID."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/works/{paper_id}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return self._parse_work(data)

        except Exception as e:
            logger.error(f"OpenAlex get paper error: {e}")
            return None


class LiteratureSearch:
    """
    Unified search interface across all databases.
    """

    def __init__(self, config: Dict = None, cache = None):
        self.config = config or {}
        self.cache = cache

        # Initialize search engines
        self.engines = {
            'semantic_scholar': SemanticScholarSearch(config, cache),
            'arxiv': ArxivSearch(config, cache),
            'pubmed': PubMedSearch(config, cache),
            'crossref': CrossrefSearch(config, cache),
            'openalex': OpenAlexSearch(config, cache),
        }

        logger.info(f"Literature search initialized with {len(self.engines)} engines")

    def search(
        self,
        query: str,
        max_results: int = 10,
        databases: Optional[List[str]] = None,
        year_range: Optional[tuple] = None,
        author: Optional[str] = None,
        venue: Optional[str] = None
    ) -> List:
        """
        Search across multiple databases.

        Args:
            query: Search query string.
            max_results: Maximum results per database.
            databases: List of databases to search. Defaults to all.
            year_range: Tuple of (start_year, end_year).
            author: Filter by author name.
            venue: Filter by venue.

        Returns:
            Combined list of search results.
        """
        if databases is None:
            databases = list(self.engines.keys())

        # If author or venue filter, need to filter after
        filter_post = author is not None or venue is not None

        all_results = []

        for db in databases:
            if db.lower() in self.engines:
                try:
                    engine = self.engines[db.lower()]
                    results = engine.search(
                        query=query,
                        max_results=max_results,
                        year_range=year_range,
                        author=author,
                        venue=venue
                    )
                    all_results.extend(results)
                    logger.info(f"{db}: Found {len(results)} results")
                except Exception as e:
                    logger.error(f"Error searching {db}: {e}")

        # Remove duplicates based on title
        unique_results = self._deduplicate_results(all_results)

        # Sort by citation count (if available)
        unique_results.sort(key=lambda x: x.citation_count, reverse=True)

        return unique_results[:max_results * len(databases)]

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on title."""
        seen_titles = set()
        unique = []

        for result in results:
            title_lower = result.title.lower().strip()
            if title_lower and title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique.append(result)

        return unique

    def find_citing_papers(
        self,
        paper_id: str,
        max_results: int = 20
    ) -> List[SearchResult]:
        """Find papers that cite a given paper."""
        # Use Semantic Scholar for citation lookup
        if 'semantic_scholar' in self.engines:
            engine = self.engines['semantic_scholar']
            return engine.search(
                query=f"citations:{paper_id}",
                max_results=max_results
            )

        # Fallback: Try other methods
        logger.warning("Citation lookup not fully implemented for this database")
        return []

    def get_paper(
        self,
        identifier: str,
        source: str = "auto"
    ) -> Optional[SearchResult]:
        """
        Get paper by identifier.

        Args:
            identifier: DOI, arXiv ID, or PubMed ID.
            source: Source database hint ('doi', 'arxiv', 'pubmed', 'auto').

        Returns:
            SearchResult or None.
        """
        # Auto-detect source
        if source == "auto":
            if identifier.startswith('10.'):
                source = "doi"
            elif identifier.startswith('arxiv:') or '/' not in identifier:
                source = "arxiv"
            elif identifier.isdigit():
                source = "pubmed"
            else:
                source = "doi"

        # Try to get from appropriate engine
        if source == "doi" and 'crossref' in self.engines:
            result = self.engines['crossref'].get_paper_details(identifier)
            if result:
                return result

        if source == "arxiv" and 'arxiv' in self.engines:
            result = self.engines['arxiv'].get_paper_details(identifier)
            if result:
                return result

        if source == "pubmed" and 'pubmed' in self.engines:
            result = self.engines['pubmed'].get_paper_details(identifier)
            if result:
                return result

        # Try all engines as fallback
        for engine in self.engines.values():
            result = engine.get_paper_details(identifier)
            if result:
                return result

        return None
