#!/usr/bin/env python3
"""
Citation Manager Module

Handles citation generation and formatting in multiple styles:
- APA (7th edition)
- MLA (9th edition)
- Chicago (17th edition)
- Harvard
- IEEE
- BibTeX

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = logging.getLogger(__name__)


class CitationStyle(ABC):
    """Abstract base class for citation styles."""

    @abstractmethod
    def format(self, paper: 'Paper') -> str:
        """Format a citation in this style."""
        pass


class APACitation(CitationStyle):
    """APA 7th Edition citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate APA citation."""
        parts = []

        # Authors
        authors = self._format_authors(paper.authors)
        if authors:
            parts.append(authors)

        # Year
        if paper.year:
            parts.append(f"({paper.year})")

        # Title
        if paper.title:
            title = paper.title.rstrip('.')
            parts.append(title)

        # Venue (in italics)
        if paper.venue:
            parts.append(f"*{paper.venue}*")

        # DOI/URL
        if paper.doi:
            parts.append(f"https://doi.org/{paper.doi}")
        elif paper.url:
            parts.append(paper.url)

        return ' '.join(parts)

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors in APA style."""
        if not authors:
            return ""

        # Clean author names
        clean_names = []
        for author in authors:
            name = self._parse_author_name(author)
            clean_names.append(name)

        if len(clean_names) == 1:
            return clean_names[0]
        elif len(clean_names) == 2:
            return f"{clean_names[0]} & {clean_names[1]}"
        elif len(clean_names) <= 20:
            # Use et al. after first 19
            if len(clean_names) > 20:
                return f"{clean_names[0]} et al."
            else:
                # Join all with commas, add & before last
                return ', '.join(clean_names[:-1]) + ', & ' + clean_names[-1]
        else:
            return f"{clean_names[0]} et al."

    def _parse_author_name(self, name: str) -> str:
        """Parse and format author name."""
        # Handle "First Last" format
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initials = ' '.join([p[0] + '.' for p in parts[:-1] if p])
            return f"{last}, {first_initials}"
        return name


class MLACitation(CitationStyle):
    """MLA 9th Edition citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate MLA citation."""
        parts = []

        # Authors
        authors = self._format_authors(paper.authors)
        if authors:
            parts.append(authors)

        # Title
        if paper.title:
            title = f'"{paper.title.rstrip(".")}."'
            parts.append(title)

        # Venue
        if paper.venue:
            parts.append(f"*{paper.venue}*")

        # Year
        if paper.year:
            parts.append(str(paper.year))

        # DOI/URL
        if paper.doi:
            parts.append(f"doi:{paper.doi}")
        elif paper.url:
            parts.append(paper.url)

        return ', '.join(parts)

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors in MLA style."""
        if not authors:
            return ""

        clean_names = []
        for author in authors:
            name = self._parse_author_name(author)
            clean_names.append(name)

        if len(clean_names) == 1:
            return clean_names[0]
        elif len(clean_names) == 2:
            return f"{clean_names[0]} and {clean_names[1]}"
        elif len(clean_names) == 3:
            return f"{clean_names[0]}, {clean_names[1]}, and {clean_names[2]}"
        else:
            return f"{clean_names[0]} et al."

    def _parse_author_name(self, name: str) -> str:
        """Parse and format author name."""
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first = ' '.join(parts[:-1])
            return f"{last}, {first}"
        return name


class ChicagoCitation(CitationStyle):
    """Chicago 17th Edition citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate Chicago citation."""
        parts = []

        # Authors
        authors = self._format_authors(paper.authors)
        if authors:
            parts.append(authors)

        # Title
        if paper.title:
            title = f'"{paper.title.rstrip(".")}."'
            parts.append(title)

        # Venue
        if paper.venue:
            parts.append(f"*{paper.venue}*")

        # Year
        if paper.year:
            parts.append(f"({paper.year})")

        # DOI/URL
        if paper.doi:
            parts.append(f"https://doi.org/{paper.doi}")
        elif paper.url:
            parts.append(paper.url)

        return '. '.join(parts)

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors in Chicago style."""
        if not authors:
            return ""

        clean_names = []
        for author in authors:
            name = self._parse_author_name(author)
            clean_names.append(name)

        if len(clean_names) == 1:
            return clean_names[0]
        elif len(clean_names) <= 10:
            # List all with commas
            if len(clean_names) == 2:
                return f"{clean_names[0]} and {clean_names[1]}"
            elif len(clean_names) == 3:
                return f"{clean_names[0]}, {clean_names[1]}, and {clean_names[2]}"
            else:
                return ', '.join(clean_names[:-1]) + ', and ' + clean_names[-1]
        else:
            return f"{clean_names[0]} et al."

    def _parse_author_name(self, name: str) -> str:
        """Parse and format author name."""
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initials = ' '.join([p[0] + '.' for p in parts[:-1] if p])
            return f"{last}, {first_initials}"
        return name


class HarvardCitation(CitationStyle):
    """Harvard citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate Harvard citation."""
        parts = []

        # Authors
        authors = self._format_authors(paper.authors)
        if authors:
            parts.append(authors)

        # Year
        if paper.year:
            parts.append(f"({paper.year})")

        # Title
        if paper.title:
            parts.append("'" + paper.title.rstrip(".") + "'")

        # Venue
        if paper.venue:
            parts.append(f"*{paper.venue}*")

        # DOI/URL
        if paper.doi:
            parts.append(f"Available at: https://doi.org/{paper.doi}")
        elif paper.url:
            parts.append(f"Available at: {paper.url}")

        return '. '.join(parts)

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors in Harvard style."""
        if not authors:
            return ""

        clean_names = []
        for author in authors:
            name = self._parse_author_name(author)
            clean_names.append(name)

        if len(clean_names) == 1:
            return clean_names[0]
        elif len(clean_names) == 2:
            return f"{clean_names[0]} and {clean_names[1]}"
        else:
            return f"{clean_names[0]} et al."

    def _parse_author_name(self, name: str) -> str:
        """Parse and format author name."""
        parts = name.strip().split()
        if len(parts) >= 2:
            # Return Lastname, F.M.
            last = parts[-1]
            initials = ''.join([p[0] for p in parts[:-1] if p])
            return f"{last}, {initials}"
        return name


class IEEECitation(CitationStyle):
    """IEEE citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate IEEE citation."""
        parts = []

        # Authors (in quotes for IEEE)
        authors = self._format_authors(paper.authors)
        if authors:
            parts.append(authors)

        # Title
        if paper.title:
            parts.append(f'"{paper.title.rstrip(".")},"')

        # Venue
        if paper.venue:
            parts.append(f"*{paper.venue}*")

        # Year
        if paper.year:
            parts.append(f"{paper.year}")

        # DOI if available
        if paper.doi:
            parts.append(f"doi: {paper.doi}")

        return ', '.join(parts)

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors in IEEE style."""
        if not authors:
            return ""

        clean_names = []
        for author in authors:
            name = self._parse_author_name(author)
            clean_names.append(name)

        if len(clean_names) == 1:
            return clean_names[0]
        elif len(clean_names) == 2:
            return f"{clean_names[0]} and {clean_names[1]}"
        elif len(clean_names) == 6:
            # IEEE shows up to 6 authors
            return ', '.join(clean_names[:-1]) + ', and ' + clean_names[-1]
        else:
            return f"{clean_names[0]} et al."

    def _parse_author_name(self, name: str) -> str:
        """Parse and format author name."""
        parts = name.strip().split()
        if len(parts) >= 2:
            initials = ' '.join([p[0] + '.' for p in parts[:-1] if p])
            return f"{initials} {parts[-1]}"
        return name


class BibTeXGenerator(CitationStyle):
    """BibTeX citation format."""

    def format(self, paper: 'Paper') -> str:
        """Generate BibTeX entry."""
        # Generate citation key
        key = self._generate_citation_key(paper)

        entry = [f"@article{{{key},"]

        # Author
        if paper.authors:
            author_str = ' and '.join(paper.authors)
            entry.append(f"  author = {{{author_str}}},")

        # Title
        if paper.title:
            entry.append(f"  title = {{{paper.title}}},")

        # Journal/Venue
        if paper.venue:
            entry.append(f"  journal = {{{paper.venue}}},")

        # Year
        if paper.year:
            entry.append(f"  year = {{{paper.year}}},")

        # Volume, issue, pages (not typically available from APIs)
        # Abstract
        if paper.abstract:
            abstract = paper.abstract.replace('\n', ' ').replace('{', '\\{').replace('}', '\\}')
            if len(abstract) > 200:
                abstract = abstract[:197] + "..."
            entry.append(f"  abstract = {{{abstract}}},")

        # DOI
        if paper.doi:
            entry.append(f"  doi = {{{paper.doi}}},")

        # URL
        if paper.url:
            entry.append(f"  url = {{{paper.url}}},")

        # Keywords/topics
        if paper.topics:
            topics = ', '.join(paper.topics)
            entry.append(f"  keywords = {{{topics}}},")

        # Citation count
        if paper.citation_count:
            entry.append(f"  note = {{Cited by {paper.citation_count}}},")

        entry.append("}")

        return '\n'.join(entry)

    def _generate_citation_key(self, paper: 'Paper') -> str:
        """Generate a unique BibTeX citation key."""
        # Format: AuthorYearTitle (first word of title)
        parts = []

        if paper.authors:
            # Use first author's last name
            first_author = paper.authors[0].split()[-1]
            # Clean non-alphanumeric
            first_author = re.sub(r'[^a-zA-Z]', '', first_author)
            parts.append(first_author.lower())

        if paper.year:
            parts.append(str(paper.year))

        if paper.title:
            # First meaningful word of title
            title_words = re.findall(r'[a-zA-Z]+', paper.title)
            if title_words:
                # Skip common words
                skip_words = {'a', 'an', 'the', 'of', 'in', 'on', 'for', 'to', 'with', 'by'}
                for word in title_words:
                    if word.lower() not in skip_words:
                        parts.append(word.lower())
                        break

        return ''.join(parts)


class CitationManager:
    """
    Manager for citation generation and formatting.

    Supports multiple citation styles and formats.
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the citation manager.

        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}

        # Initialize style handlers
        self.styles = {
            'apa': APACitation(),
            'mla': MLACitation(),
            'chicago': ChicagoCitation(),
            'harvard': HarvardCitation(),
            'ieee': IEEECitation(),
            'bibtex': BibTeXGenerator(),
        }

        # Default style
        self.default_style = self.config.get('default_citation_style', 'apa')

        logger.info(f"Citation manager initialized with {len(self.styles)} styles")

    def format_citation(
        self,
        paper: 'Paper',
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
        style = style.lower()

        if style not in self.styles:
            logger.warning(f"Unknown style '{style}', using '{self.default_style}'")
            style = self.default_style

        formatter = self.styles[style]
        return formatter.format(paper)

    def generate_bibtex(self, paper: 'Paper') -> str:
        """
        Generate a BibTeX entry for a paper.

        Args:
            paper: Paper object.

        Returns:
            BibTeX entry string.
        """
        return self.styles['bibtex'].format(paper)

    def format_multiple(
        self,
        papers: List['Paper'],
        style: str = "apa"
    ) -> List[str]:
        """
        Format multiple citations.

        Args:
            papers: List of Paper objects.
            style: Citation style.

        Returns:
            List of formatted citations.
        """
        return [self.format_citation(paper, style) for paper in papers]

    def generate_bibliography(
        self,
        papers: List['Paper'],
        style: str = "apa",
        title: str = "Bibliography"
    ) -> str:
        """
        Generate a complete bibliography.

        Args:
            papers: List of Paper objects.
            style: Citation style.
            title: Bibliography title.

        Returns:
            Formatted bibliography string.
        """
        citations = self.format_multiple(papers, style)

        # Sort by author name
        citations.sort()

        lines = [f"# {title}\n"]
        for i, citation in enumerate(citations, 1):
            # Add hanging indent
            lines.append(f"{i}. {citation}\n")

        return '\n'.join(lines)

    def generate_bibliography_bibtex(
        self,
        papers: List['Paper'],
        title: str = "Bibliography"
    ) -> str:
        """
        Generate a BibTeX bibliography file.

        Args:
            papers: List of Paper objects.
            title: Title for comments.

        Returns:
            BibTeX file content.
        """
        lines = [
            f"% {title}",
            f"% Generated by Research Assistant",
            f"% {datetime.now().strftime('%Y-%m-%d')}",
            "",
        ]

        for paper in papers:
            lines.append(self.generate_bibtex(paper))
            lines.append("")  # Empty line between entries

        return '\n'.join(lines)

    def extract_citations_from_text(
        self,
        text: str,
        style: str = "numeric"
    ) -> List[Dict[str, str]]:
        """
        Extract and parse citations from text.

        Args:
            text: Text containing citations.
            style: Expected citation style.

        Returns:
            List of extracted citation info.
        """
        citations = []

        # Common patterns for in-text citations
        patterns = {
            'apa': re.compile(r'\(([^)]+?, \d{4})\)'),
            'numeric': re.compile(r'\[(\d+(?:,\s*\d+)*)\]'),
            'author_date': re.compile(r'(\w+,\s*\w+?,?\s*\d{4})'),
        }

        pattern = patterns.get(style, patterns['numeric'])
        matches = pattern.findall(text)

        for match in matches:
            citations.append({
                'raw': match,
                'parsed': self._parse_citation(match, style)
            })

        return citations

    def _parse_citation(
        self,
        citation: str,
        style: str
    ) -> Dict[str, str]:
        """Parse a citation string into components."""
        result = {'raw': citation}

        # Try to extract author and year
        if style in ('apa', 'author_date'):
            match = re.match(r'([^,]+),\s*(\d{4})', citation)
            if match:
                result['author'] = match.group(1).strip()
                result['year'] = match.group(2)

        # Try to extract numbers
        if style == 'numeric':
            numbers = re.findall(r'\d+', citation)
            if numbers:
                result['numbers'] = numbers

        return result

    def convert_citation_style(
        self,
        citation: str,
        from_style: str,
        to_style: str,
        paper: 'Paper'
    ) -> str:
        """
        Convert a citation between styles.

        Args:
            citation: Original citation string.
            from_style: Original style.
            to_style: Target style.
            paper: Paper object for reference.

        Returns:
            Citation in new style.
        """
        # Simply regenerate in new style
        return self.format_citation(paper, to_style)

    def validate_citation(self, citation: str, style: str) -> Dict[str, Any]:
        """
        Validate a citation string.

        Args:
            citation: Citation string to validate.
            style: Expected style.

        Returns:
            Validation result dictionary.
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check required components based on style
        required = {
            'apa': ['year', 'author'],
            'mla': ['author', 'title', 'year'],
            'chicago': ['author', 'year', 'title'],
            'harvard': ['author', 'year', 'title'],
            'ieee': ['author', 'title'],
        }

        required_fields = required.get(style, [])

        for field in required_fields:
            if field not in citation.lower():
                result['warnings'].append(f"Missing {field} in citation")

        # Check formatting
        if style == 'apa' and '(' not in citation:
            result['errors'].append("APA style should contain parentheses for year")

        if style == 'ieee' and '"' not in citation:
            result['warnings'].append("IEEE style should have title in quotes")

        result['valid'] = len(result['errors']) == 0

        return result


# Make Paper available
if __name__ == "__main__":
    print("Citation Manager Module")
    print("=" * 50)
    print("This module handles citation generation and formatting.")
    print("\nSupported styles:")
    print("- apa: APA 7th Edition")
    print("- mla: MLA 9th Edition")
    print("- chicago: Chicago 17th Edition")
    print("- harvard: Harvard style")
    print("- ieee: IEEE format")
    print("- bibtex: BibTeX format")
    print("\nImport and use with ResearchAssistant class.")
