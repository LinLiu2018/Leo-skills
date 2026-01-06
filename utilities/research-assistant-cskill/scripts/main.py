#!/usr/bin/env python3
"""
Research Assistant - Main Entry Point

A comprehensive research assistant for academic literature search,
paper analysis, summarization, and citation management.

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search.literature_search import LiteratureSearch
from analyze.paper_analyzer import PaperAnalyzer
from summarize.summarizer import Summarizer
from citations.citation_manager import CitationManager
from utils.helpers import setup_logging, load_config, CacheManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Data class representing an academic paper."""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    venue: str = ""
    abstract: str = ""
    citation_count: int = 0
    url: str = ""
    doi: str = ""
    topics: List[str] = field(default_factory=list)
    methodology: str = ""
    key_findings: List[str] = field(default_factory=list)
    references: List[Dict] = field(default_factory=list)
    full_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Paper to dictionary."""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'venue': self.venue,
            'abstract': self.abstract,
            'citation_count': self.citation_count,
            'url': self.url,
            'doi': self.doi,
            'topics': self.topics,
            'methodology': self.methodology,
            'key_findings': self.key_findings,
            'references': self.references,
        }


class ResearchAssistant:
    """
    Main Research Assistant class that orchestrates all research workflows.

    This class provides a unified interface for:
    - Literature search across multiple databases
    - Paper analysis and extraction
    - Automatic summarization
    - Citation generation and management
    - Literature review generation
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Research Assistant.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config = load_config(config_path)
        self.cache = CacheManager(
            enabled=self.config.get('enable_cache', True),
            cache_days=self.config.get('cache_days', 7)
        )

        # Initialize components
        self.search = LiteratureSearch(config=self.config, cache=self.cache)
        self.analyzer = PaperAnalyzer(config=self.config, cache=self.cache)
        self.summarizer = Summarizer(config=self.config)
        self.citation_manager = CitationManager(config=self.config)

        logger.info("Research Assistant initialized successfully")

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        databases: Optional[List[str]] = None,
        year_range: Optional[tuple] = None,
        author: Optional[str] = None,
        venue: Optional[str] = None
    ) -> List[Paper]:
        """
        Search for academic papers across multiple databases.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            databases: List of databases to search. Defaults to all.
            year_range: Tuple of (start_year, end_year).
            author: Filter by author name.
            venue: Filter by venue/journal name.

        Returns:
            List of Paper objects.
        """
        logger.info(f"Searching for papers: {query}")

        papers = self.search.search(
            query=query,
            max_results=max_results,
            databases=databases,
            year_range=year_range,
            author=author,
            venue=venue
        )

        logger.info(f"Found {len(papers)} papers")
        return papers

    def analyze_paper(
        self,
        identifier: str,
        source: str = "auto"
    ) -> Paper:
        """
        Analyze a paper and extract structured information.

        Args:
            identifier: DOI, arXiv ID, or URL.
            source: Source database ('doi', 'arxiv', 'url', 'auto').

        Returns:
            Paper object with analyzed data.
        """
        logger.info(f"Analyzing paper: {identifier}")

        paper = self.analyzer.analyze(
            identifier=identifier,
            source=source
        )

        logger.info(f"Analysis complete for: {paper.title}")
        return paper

    def summarize_paper(
        self,
        paper: Paper,
        max_length: int = 200,
        style: str = "concise"
    ) -> str:
        """
        Generate a summary of a paper.

        Args:
            paper: Paper object to summarize.
            max_length: Maximum length of summary in words.
            style: Summary style ('concise', 'detailed', 'bullet_points').

        Returns:
            Summary string.
        """
        logger.info(f"Generating summary for: {paper.title}")

        summary = self.summarizer.summarize(
            paper=paper,
            max_length=max_length,
            style=style
        )

        return summary

    def format_citation(
        self,
        paper: Paper,
        style: str = "apa"
    ) -> str:
        """
        Format a citation in the specified style.

        Args:
            paper: Paper object.
            style: Citation style ('apa', 'mla', 'chicago', 'harvard', 'ieee').

        Returns:
            Formatted citation string.
        """
        logger.info(f"Formatting citation for: {paper.title}")

        citation = self.citation_manager.format_citation(
            paper=paper,
            style=style
        )

        return citation

    def generate_bibtex(self, paper: Paper) -> str:
        """
        Generate a BibTeX entry for a paper.

        Args:
            paper: Paper object.

        Returns:
            BibTeX entry string.
        """
        logger.info(f"Generating BibTeX for: {paper.title}")

        bibtex = self.citation_manager.generate_bibtex(paper=paper)

        return bibtex

    def find_citing_papers(
        self,
        paper_id: str,
        max_results: int = 20
    ) -> List[Paper]:
        """
        Find papers that cite a given paper.

        Args:
            paper_id: DOI or paper identifier.
            max_results: Maximum number of citing papers to return.

        Returns:
            List of Paper objects that cite the given paper.
        """
        logger.info(f"Finding papers citing: {paper_id}")

        papers = self.search.find_citing_papers(
            paper_id=paper_id,
            max_results=max_results
        )

        logger.info(f"Found {len(papers)} citing papers")
        return papers

    def generate_literature_review(
        self,
        topic: str,
        num_papers: int = 20,
        output_format: str = "structured",
        year_range: Optional[tuple] = None
    ) -> str:
        """
        Generate a structured literature review for a topic.

        Args:
            topic: Research topic.
            num_papers: Number of papers to include.
            output_format: Output format ('structured', 'markdown', 'json').
            year_range: Tuple of (start_year, end_year).

        Returns:
            Literature review string in specified format.
        """
        logger.info(f"Generating literature review for: {topic}")

        # Step 1: Search for papers
        papers = self.search_papers(
            query=topic,
            max_results=num_papers,
            year_range=year_range
        )

        if not papers:
            return "No papers found for the given topic."

        # Step 2: Analyze papers
        analyzed_papers = []
        for paper in papers:
            try:
                analyzed = self.analyzer.analyze_paper_data(paper)
                analyzed_papers.append(analyzed)
            except Exception as e:
                logger.warning(f"Could not analyze paper: {paper.title}. Error: {e}")
                analyzed_papers.append(paper)

        # Step 3: Generate review
        review = self._create_review(
            topic=topic,
            papers=analyzed_papers,
            output_format=output_format
        )

        logger.info(f"Literature review generated with {len(papers)} papers")
        return review

    def _create_review(
        self,
        topic: str,
        papers: List[Paper],
        output_format: str = "structured"
    ) -> str:
        """Create a literature review from analyzed papers."""
        current_year = datetime.now().year
        years = [p.year for p in papers if p.year]
        year_range_str = f"{min(years)}-{max(years)}" if years else "Unknown"

        if output_format == "json":
            return self._create_json_review(topic, papers, year_range_str)
        elif output_format == "markdown":
            return self._create_markdown_review(topic, papers, year_range_str)
        else:
            return self._create_structured_review(topic, papers, year_range_str)

    def _create_structured_review(
        self,
        topic: str,
        papers: List[Paper],
        year_range: str
    ) -> str:
        """Create a structured text literature review."""
        review_parts = [
            f"# Literature Review: {topic}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}",
            f"**Papers Reviewed:** {len(papers)}",
            f"**Time Period:** {year_range}",
            "",
            "## Overview",
            f"This review synthesizes {len(papers)} academic papers on {topic}.",
            "",
        ]

        # Sort papers by citation count for prominence
        sorted_papers = sorted(papers, key=lambda x: x.citation_count, reverse=True)

        # Group by themes (simplified - using topics)
        themes = {}
        for paper in sorted_papers:
            for topic in paper.topics[:2]:  # Use top 2 topics
                if topic not in themes:
                    themes[topic] = []
                themes[topic].append(paper)

        if themes:
            review_parts.extend(["## Key Themes", ""])
            for theme, theme_papers in list(themes.items())[:5]:
                review_parts.extend([
                    f"### {theme}",
                    f"*{len(theme_papers)} papers*",
                    ""
                ])
                for paper in theme_papers[:3]:
                    review_parts.extend([
                        f"- **{paper.title}** ({paper.year})",
                        f"  - Authors: {', '.join(paper.authors[:3])}",
                        f"  - Citations: {paper.citation_count}",
                        f"  - Venue: {paper.venue}" if paper.venue else "",
                        ""
                    ])

        # Key findings
        all_findings = []
        for paper in sorted_papers[:5]:
            all_findings.extend(paper.key_findings)

        if all_findings:
            review_parts.extend([
                "## Key Findings",
                ""
            ])
            unique_findings = list(set(all_findings))[:10]
            for i, finding in enumerate(unique_findings, 1):
                review_parts.append(f"{i}. {finding}")
            review_parts.append("")

        # Research gaps
        review_parts.extend([
            "## Identified Research Gaps",
            "",
            "- Limited long-term studies on the topic",
            "- Need for more diverse sample populations",
            "- Gap between theoretical frameworks and practical applications",
            "- Insufficient cross-cultural research",
            "- Lack of reproducibility studies",
            ""
        ])

        # Future directions
        review_parts.extend([
            "## Future Research Directions",
            "",
            "1. Longitudinal studies to assess long-term effects",
            "2. Cross-disciplinary collaborations",
            "3. Development of standardized measurement tools",
            "4. More emphasis on real-world applications",
            "5. Investigation of moderating variables",
            ""
        ])

        # References
        review_parts.extend([
            "## References",
            ""
        ])
        for i, paper in enumerate(sorted_papers[:20], 1):
            citation = self.format_citation(paper, style="apa")
            review_parts.append(f"{i}. {citation}")

        return "\n".join(review_parts)

    def _create_markdown_review(
        self,
        topic: str,
        papers: List[Paper],
        year_range: str
    ) -> str:
        """Create a markdown literature review."""
        review_parts = [
            f"# Research Summary: {topic}",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## Papers Analyzed",
            f"**Total:** {len(papers)} papers",
            f"**Period:** {year_range}",
            "",
            "---",
            ""
        ]

        for paper in papers[:10]:
            review_parts.extend([
                f"### {paper.title}",
                f"**Year:** {paper.year} | **Citations:** {paper.citation_count}",
                f"**Authors:** {', '.join(paper.authors)}",
                "",
                f"**Abstract:** {paper.abstract[:300]}..." if paper.abstract else "",
                f"**Venue:** {paper.venue}" if paper.venue else "",
                f"**Topics:** {', '.join(paper.topics)}" if paper.topics else "",
                "",
                "---",
                ""
            ])

        return "\n".join(review_parts)

    def _create_json_review(
        self,
        topic: str,
        papers: List[Paper],
        year_range: str
    ) -> str:
        """Create a JSON literature review."""
        import json

        review_data = {
            "topic": topic,
            "generated": datetime.now().isoformat(),
            "summary": {
                "total_papers": len(papers),
                "year_range": year_range,
            },
            "papers": [paper.to_dict() for paper in papers],
            "trends": {
                "topics": {},
                "years": {}
            }
        }

        # Aggregate topic frequencies
        topic_counts = {}
        year_counts = {}
        for paper in papers:
            for topic in paper.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            year = paper.year
            if year:
                year_counts[str(year)] = year_counts.get(str(year), 0) + 1

        review_data["trends"]["topics"] = topic_counts
        review_data["trends"]["years"] = year_counts

        return json.dumps(review_data, indent=2, ensure_ascii=False)

    def batch_analyze(
        self,
        identifiers: List[str],
        source: str = "auto"
    ) -> List[Paper]:
        """
        Analyze multiple papers in batch.

        Args:
            identifiers: List of paper identifiers.
            source: Source database.

        Returns:
            List of analyzed Paper objects.
        """
        logger.info(f"Batch analyzing {len(identifiers)} papers")

        papers = []
        for i, identifier in enumerate(identifiers):
            try:
                paper = self.analyze_paper(identifier, source)
                papers.append(paper)
                logger.info(f"Analyzed {i+1}/{len(identifiers)}: {paper.title}")
            except Exception as e:
                logger.error(f"Failed to analyze {identifier}: {e}")

        return papers

    def export_bibliography(
        self,
        papers: List[Paper],
        style: str = "bibtex",
        output_path: str = "bibliography"
    ) -> str:
        """
        Export a bibliography from a list of papers.

        Args:
            papers: List of Paper objects.
            style: Export style ('bibtex', 'apa', 'mla', 'chicago').
            output_path: Base path for output files.

        Returns:
            Path to exported file.
        """
        logger.info(f"Exporting bibliography with {len(papers)} papers")

        if style == "bibtex":
            content = "\n".join([self.generate_bibtex(p) for p in papers])
            ext = "bib"
        else:
            content = "\n\n".join([
                f"{i+1}. {self.format_citation(p, style=style)}"
                for i, p in enumerate(papers)
            ])
            ext = "txt"

        file_path = f"{output_path}.{ext}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Bibliography exported to: {file_path}")
        return file_path


def main():
    """Main entry point for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Research Assistant CLI")
    parser.add_argument(
        "command",
        choices=["search", "analyze", "summarize", "review", "citation"],
        help="Command to execute"
    )
    parser.add_argument("query", help="Query or identifier")
    parser.add_argument("--max-results", type=int, default=10, help="Max results")
    parser.add_argument("--style", default="apa", help="Citation style")
    parser.add_argument("--output", default="review.md", help="Output file")

    args = parser.parse_args()

    assistant = ResearchAssistant()

    if args.command == "search":
        papers = assistant.search_papers(args.query, args.max_results)
        for paper in papers:
            print(f"Title: {paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Year: {paper.year}")
            print(f"Citations: {paper.citation_count}")
            print("---")

    elif args.command == "analyze":
        paper = assistant.analyze_paper(args.query)
        print(f"Title: {paper.title}")
        print(f"Abstract: {paper.abstract}")
        print(f"Key Findings: {paper.key_findings}")

    elif args.command == "summarize":
        paper = assistant.analyze_paper(args.query)
        summary = assistant.summarize_paper(paper)
        print(summary)

    elif args.command == "review":
        review = assistant.generate_literature_review(
            args.query,
            args.max_results,
            output_format="structured"
        )
        print(review)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(review)
        print(f"\nReview saved to: {args.output}")

    elif args.command == "citation":
        paper = assistant.analyze_paper(args.query)
        citation = assistant.format_citation(paper, args.style)
        print(citation)


if __name__ == "__main__":
    main()
