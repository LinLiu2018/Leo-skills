#!/usr/bin/env python3
"""
Paper Analyzer Module

Analyzes academic papers to extract:
- Key findings
- Methodology
- Research questions
- Contributions
- Limitations
- Future work suggestions

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import aiohttp
except ImportError:
    aiohttp = None


logger = logging.getLogger(__name__)


class PaperAnalyzer:
    """
    Analyzer for academic papers.

    Extracts structured information from papers including:
    - Abstract and summary
    - Key findings
    - Methodology
    - Research questions/objectives
    - Contributions
    - Limitations and future work
    - References
    """

    def __init__(self, config: Dict = None, cache = None):
        """
        Initialize the paper analyzer.

        Args:
            config: Configuration dictionary.
            cache: Optional cache manager.
        """
        self.config = config or {}
        self.cache = cache
        self.session = None

        # Extraction patterns
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for extraction."""
        # Section headers
        self.section_patterns = {
            'abstract': re.compile(
                r'(?i)(?:^|\n)\s*(?:ABSTRACT|Abstract)\s*[:\-]?\s*(.+?)(?=\n\s*(?:INTRO|INTRODUCTION|Keywords?|1\.|\n)|$)',
                re.DOTALL
            ),
            'introduction': re.compile(
                r'(?i)(?:^|\n)\s*(?:1\.?\s*)?(?:INTRODUCTION|Intro(?:duction)?)\s*[:\-]?\s*(.+?)(?=\n\s*(?:2\.?\s*(?:RELATED|METHOD|APPROACH|BACKGROUND)|CONCL|FUTURE)|\Z)',
                re.DOTALL
            ),
            'methodology': re.compile(
                r'(?i)(?:^|\n)\s*(?:2\.?\s*)?(?:METHODOLOGY|METHODS|APPROACH|Materials?\s*(?:and|&)\s*Methods?|Experimental)\s*[:\-]?\s*(.+?)(?=\n\s*(?:3\.?\s*(?:RESULT|DISCUSS)|CONCLUSION|FUTURE)|\Z)',
                re.DOTALL
            ),
            'results': re.compile(
                r'(?i)(?:^|\n)\s*(?:3\.?\s*)?(?:RESULTS?|FINDINGS?|EXPERIMENTS?)\s*[:\-]?\s*(.+?)(?=\n\s*(?:4\.?\s*DISCUSSION|DISCUSSION|CONCLUSION|FUTURE)|\Z)',
                re.DOTALL
            ),
            'discussion': re.compile(
                r'(?i)(?:^|\n)\s*(?:4\.?\s*)?(?:DISCUSSION|Discussi(?:on|ng))\s*[:\-]?\s*(.+?)(?=\n\s*(?:5\.?\s*CONCLUSION|CONCLUSION|FUTURE|REFERENCES?)|\Z)',
                re.DOTALL
            ),
            'conclusion': re.compile(
                r'(?i)(?:^|\n)\s*(?:5\.?\s*)?(?:CONCLUSION|CONCLUSIONS?|SUMMARY)\s*[:\-]?\s*(.+?)(?=\n\s*(?:REFERENCES?|FUTURE WORK|ACKNOWLEDGMENTS?)|\Z)',
                re.DOTALL
            ),
            'references': re.compile(
                r'(?i)(?:^|\n)\s*(?:REFERENCES|BIBLIOGRAPHY|WORKS\s*CITED)\s*[:\-]?\s*(.+)$',
                re.DOTALL
            ),
        }

        # Key finding indicators
        self.finding_patterns = [
            re.compile(r'(?i)(?:we\s+find|our\s+results?\s+(?:show|demonstrate|indicate|suggest)|found\s+that|results?\s+indicate)'),
            re.compile(r'(?i)(?:significant|notably|interestingly|surprisingly|importantly)'),
            re.compile(r'(?i)(?:this\s+suggests|imply|reveal|confirm|provide\s+evidence)'),
            re.compile(r'(?i)(?:we\s+observe|observed\s+that|shown\s+in)'),
        ]

        # Methodology indicators
        self.method_patterns = [
            re.compile(r'(?i)(?:we\s+(?:use|employ|apply|utilize|conduct|perform))'),
            re.compile(r'(?i)(?:using|employing|applying|utilizing|via|through)'),
            re.compile(r'(?i)(?:method(?:ology)?|approach|technique|algorithm|model)'),
            re.compile(r'(?i)(?:dataset|corpus|collection|sample|participants?)'),
        ]

        # Limitation indicators
        self.limitation_patterns = [
            re.compile(r'(?i)(?:limitat|weakness|drawback)'),
            re.compile(r'(?i)(?:future\s+work|future\s+research|future\s+directions)'),
            re.compile(r'(?i)(?:however|nevertheless|nonetheless)\s+.*\b(limitat|restrict|局限)'),
        ]

    def _init_session(self):
        """Initialize HTTP session."""
        if self.session is None:
            try:
                import requests
                self.session = requests.Session()
                self.session.headers.update({
                    'User-Agent': 'ResearchAssistant/1.0',
                })
            except ImportError:
                pass

    def analyze(
        self,
        identifier: str,
        source: str = "auto"
    ) -> 'Paper':
        """
        Analyze a paper by its identifier.

        Args:
            identifier: DOI, arXiv ID, or URL.
            source: Source database hint.

        Returns:
            Paper object with analyzed data.
        """
        from search.literature_search import LiteratureSearch

        search = LiteratureSearch(config=self.config, cache=self.cache)

        # Get paper details
        paper_data = search.get_paper(identifier, source)

        if paper_data is None:
            raise ValueError(f"Could not find paper: {identifier}")

        # Create Paper object with analysis
        return self.analyze_paper_data(paper_data)

    def analyze_paper_data(self, paper_data) -> 'Paper':
        """
        Analyze paper data and extract structured information.

        Args:
            paper_data: SearchResult or Paper object.

        Returns:
            Paper with extracted analysis.
        """
        # Convert to Paper if needed
        if not hasattr(paper_data, 'key_findings'):
            paper = self._create_paper_from_result(paper_data)
        else:
            paper = paper_data

        # Extract additional information from abstract
        if paper.abstract:
            analysis = self._analyze_text(paper.abstract, section="abstract")
            paper.methodology = analysis.get('methodology', '')
            paper.topics.extend(analysis.get('topics', []))

        # If full text available, do deeper analysis
        if paper.full_text:
            self._extract_full_text_analysis(paper)

        return paper

    def _create_paper_from_result(self, result) -> 'Paper':
        """Create a Paper object from SearchResult."""
        from main import Paper

        return Paper(
            paper_id=result.paper_id,
            title=result.title,
            authors=result.authors,
            year=result.year,
            venue=result.venue,
            abstract=result.abstract,
            citation_count=result.citation_count,
            url=result.url,
            doi=result.doi,
            topics=result.topics,
        )

    def _analyze_text(
        self,
        text: str,
        section: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze text to extract key information.

        Args:
            text: Text to analyze.
            section: Section name for context.

        Returns:
            Dictionary with extracted information.
        """
        analysis = {
            'key_findings': [],
            'methodology': '',
            'research_questions': [],
            'contributions': [],
            'limitations': [],
            'topics': [],
        }

        if not text:
            return analysis

        # Extract key findings
        analysis['key_findings'] = self._extract_key_findings(text)

        # Extract methodology
        analysis['methodology'] = self._extract_methodology(text)

        # Extract research questions
        analysis['research_questions'] = self._extract_research_questions(text)

        # Extract contributions
        analysis['contributions'] = self._extract_contributions(text)

        # Extract limitations
        analysis['limitations'] = self._extract_limitations(text)

        return analysis

    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from text."""
        findings = []

        # Split into sentences
        sentences = re.split(r'[.!?\n]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

        for sentence in sentences:
            # Check if sentence indicates a finding
            for pattern in self.finding_patterns:
                if pattern.search(sentence):
                    findings.append(sentence)
                    break

        # Deduplicate and limit
        unique_findings = list(dict.fromkeys(findings))
        return unique_findings[:10]

    def _extract_methodology(self, text: str) -> str:
        """Extract methodology description."""
        methodology_text = []

        # Find sentences with methodology indicators
        sentences = re.split(r'[.!?\n]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        for sentence in sentences:
            for pattern in self.method_patterns:
                if pattern.search(sentence):
                    methodology_text.append(sentence)
                    break

        return ' '.join(methodology_text[:5])

    def _extract_research_questions(self, text: str) -> List[str]:
        """Extract research questions from text."""
        questions = []

        # Pattern for research questions
        question_pattern = re.compile(
            r'(?i)(?:we\s+(?:investigate|examine|explore|address|study|analyze|answer|seek)|'
            r'(?:research\s+question|hypothesi|study\s+(?:aim|objective|goal))s?\s*[:\-]?\s*)'
            r'([^.?!\n]+[.?!\n])'
        )

        matches = question_pattern.findall(text)
        for match in matches:
            question = match.strip()
            if len(question) > 20 and len(question) < 300:
                questions.append(question)

        return questions[:5]

    def _extract_contributions(self, text: str) -> List[str]:
        """Extract contributions from text."""
        contributions = []

        # Look for explicit contribution statements
        contribution_patterns = [
            re.compile(r'(?i)(?:our\s+(?:main\s+)?(?:contribution|contributions)\s+(?:is|are|involve|include)'),
            re.compile(r'(?i)(?:this\s+(?:paper|study|work)\s+(?:makes?|provides?|offers?|presents?|introduces?|proposes?)\s+(?:a\s+)?(?:novel|new|significant|important|first)?\s*(?:contribution|approach|method|model|framework))'),
            re.compile(r'(?i)(?:key\s+(?:contribution|contributions)\s+(?:include|are))'),
        ]

        for pattern in contribution_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if len(match) > 20:
                    contributions.append(match.strip())

        return contributions[:5]

    def _extract_limitations(self, text: str) -> List[str]:
        """Extract limitations from text."""
        limitations = []

        # Look for limitation statements
        limitation_patterns = [
            re.compile(r'(?i)(?:(?:this|our)\s+(?:study|work|approach|method)\s+(?:is\s+)?(?:limited|has\s+limitations?|suffers?\s+from)\s*([^.?!\n]+[.?!\n])'),
            re.compile(r'(?i)(?:limitat\w+\s+(?:include|are|of\s+this\s+study)\s*([^.?!\n]+[.?!\n])'),
            re.compile(r'(?i)(?:future\s+work\s+should\s+(?:address|investigate|explore|consider)\s+([^.?!\n]+[.?!\n])'),
        ]

        for pattern in limitation_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if len(match) > 15:
                    limitations.append(match.strip())

        return limitations[:5]

    def _extract_full_text_analysis(self, paper: 'Paper'):
        """Perform deeper analysis if full text is available."""
        text = paper.full_text

        # Extract sections
        for section_name, pattern in self.section_patterns.items():
            match = pattern.search(text)
            if match:
                section_text = match.group(1).strip()
                analysis = self._analyze_text(section_text, section=section_name)

                if section_name == 'methodology':
                    paper.methodology = analysis.get('methodology', section_text[:500])
                elif section_name == 'conclusion':
                    paper.key_findings.extend(analysis.get('key_findings', []))

        # Extract references
        paper.references = self._extract_references(text)

    def _extract_references(self, text: str) -> List[Dict]:
        """Extract references from paper."""
        references = []

        # Find reference section
        ref_match = self.section_patterns['references'].search(text)
        if not ref_match:
            return references

        ref_text = ref_match.group(1)

        # Parse individual references
        # Common patterns: [1] Author, Title, Venue, Year
        ref_patterns = [
            re.compile(r'\[(\d+)\]\s*([^\[\n]+)'),  # [1] Author et al.
            re.compile(r'(\d+)\.\s*([^\n]+)'),  # 1. Author et al.
        ]

        for pattern in ref_patterns:
            matches = pattern.findall(ref_text)
            for match in matches:
                ref_num, ref_text_content = match
                references.append({
                    'number': ref_num,
                    'text': ref_text_content.strip()[:300]
                })

        return references[:50]

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using simple heuristics."""
        keywords = []

        # Look for keywords section
        keyword_pattern = re.compile(
            r'(?i)(?:keywords?|subject\s+terms?|index\s+terms?)\s*[:\-]?\s*([^\n.;]+)',
            re.IGNORECASE
        )

        match = keyword_pattern.search(text)
        if match:
            keywords_text = match.group(1)
            keywords = [kw.strip().lower() for kw in keywords_text.split(',')]
            keywords = [kw for kw in keywords if len(kw) > 2]

        return keywords

    def summarize_paper_structure(self, paper: 'Paper') -> Dict[str, Any]:
        """
        Summarize the structure of a paper.

        Args:
            paper: Paper object.

        Returns:
            Dictionary with structure summary.
        """
        return {
            'title': paper.title,
            'authors': len(paper.authors),
            'year': paper.year,
            'has_abstract': bool(paper.abstract),
            'has_methodology': bool(paper.methodology),
            'num_key_findings': len(paper.key_findings),
            'num_references': len(paper.references),
            'topics': paper.topics[:5],
            'citation_count': paper.citation_count,
        }

    def compare_papers(
        self,
        papers: List['Paper']
    ) -> Dict[str, Any]:
        """
        Compare multiple papers.

        Args:
            papers: List of Paper objects.

        Returns:
            Comparison dictionary.
        """
        if not papers:
            return {'error': 'No papers provided'}

        comparison = {
            'count': len(papers),
            'year_range': {
                'min': min(p.year for p in papers if p.year),
                'max': max(p.year for p in papers if p.year),
            },
            'total_citations': sum(p.citation_count for p in papers),
            'common_topics': [],
            'papers_by_citations': [],
        }

        # Find common topics
        all_topics = {}
        for paper in papers:
            for topic in paper.topics:
                all_topics[topic] = all_topics.get(topic, 0) + 1

        comparison['common_topics'] = sorted(
            all_topics.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Sort papers by citations
        comparison['papers_by_citations'] = sorted(
            papers,
            key=lambda x: x.citation_count,
            reverse=True
        )

        return comparison


# Make Paper available to this module
if __name__ == "__main__":
    # Test the analyzer
    print("Paper Analyzer Module")
    print("=" * 50)
    print("This module analyzes academic papers.")
    print("\nFeatures:")
    print("- Extract key findings")
    print("- Identify methodology")
    print("- Find research questions")
    print("- Extract contributions")
    print("- Parse references")
    print("\nImport and use with ResearchAssistant class.")
