#!/usr/bin/env python3
"""
Summarizer Module

Generates summaries of academic papers using extractive and
abstractive techniques.

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = logging.getLogger(__name__)


@dataclass
class Summary:
    """Data class for paper summary."""
    text: str
    style: str
    word_count: int
    sentence_count: int
    key_points: List[str] = None

    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []


class Summarizer:
    """
    Summarizer for academic papers.

    Generates summaries in various styles:
    - Concise: Brief overview (100-200 words)
    - Detailed: Comprehensive summary (300-500 words)
    - Bullet Points: Key points as bullets
    - Abstract Style: Like a paper abstract
    - Key Findings: Focus on findings only
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the summarizer.

        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}

        # Sentence scoring weights
        self.position_weight = {
            'first': 1.5,    # First sentences are important
            'middle': 1.0,
            'last': 1.2,     # Last sentences often contain conclusions
        }

    def summarize(
        self,
        paper: 'Paper',
        max_length: int = 200,
        style: str = "concise"
    ) -> str:
        """
        Generate a summary for a paper.

        Args:
            paper: Paper object with title, abstract, etc.
            max_length: Maximum length in words.
            style: Summary style ('concise', 'detailed', 'bullet_points',
                    'abstract_style', 'key_findings').

        Returns:
            Summary string.
        """
        # Combine available text sources
        text_sources = []

        if hasattr(paper, 'abstract') and paper.abstract:
            text_sources.append(paper.abstract)
        if hasattr(paper, 'key_findings') and paper.key_findings:
            text_sources.extend(paper.key_findings)

        if not text_sources:
            return "No content available for summarization."

        # Combine texts
        full_text = ' '.join(text_sources)

        # Generate summary based on style
        if style == "bullet_points":
            return self._generate_bullet_summary(full_text, paper, max_length)
        elif style == "abstract_style":
            return self._generate_abstract_style(full_text, paper, max_length)
        elif style == "key_findings":
            return self._generate_findings_summary(paper, max_length)
        elif style == "detailed":
            return self._generate_detailed_summary(full_text, paper, max_length)
        else:
            return self._generate_concise_summary(full_text, paper, max_length)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences

    def _score_sentence(
        self,
        sentence: str,
        position: int,
        total: int,
        keywords: List[str]
    ) -> float:
        """
        Score a sentence for extractive summarization.

        Args:
            sentence: Sentence text.
            position: Position in document.
            total: Total number of sentences.
            keywords: Keywords to weight.

        Returns:
            Score between 0 and 1.
        """
        score = 0.0

        # Position score
        if position == 0:
            score += self.position_weight['first']
        elif position == total - 1:
            score += self.position_weight['last']
        else:
            score += self.position_weight['middle']

        # Length score (prefer medium-length sentences)
        word_count = len(sentence.split())
        if 10 <= word_count <= 30:
            score += 0.5
        elif word_count < 5 or word_count > 50:
            score -= 0.3

        # Keyword score
        sentence_lower = sentence.lower()
        for keyword in keywords:
            if keyword.lower() in sentence_lower:
                score += 0.3

        # Feature indicators
        if re.search(r'(?i)(we (find|show|demonstrate)|results? (show|suggest)|conclusion)', sentence):
            score += 0.5
        if re.search(r'(?i)(however|although|nevertheless)', sentence):
            score -= 0.2  # Complex sentences might be harder to extract

        return score

    def _extract_key_sentences(
        self,
        text: str,
        max_words: int,
        paper: 'Paper'
    ) -> List[str]:
        """Extract key sentences using extractive summarization."""
        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        # Define keywords from paper
        keywords = []
        if hasattr(paper, 'topics') and paper.topics:
            keywords = paper.topics[:5]
        if hasattr(paper, 'title') and paper.title:
            # Extract words from title
            title_words = [w.lower() for w in re.findall(r'\w+', paper.title) if len(w) > 3]
            keywords.extend(title_words[:5])

        # Score all sentences
        scored = []
        total = len(sentences)
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, total, keywords)
            scored.append((sentence, score, len(sentence.split())))

        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select sentences until word limit
        selected = []
        current_words = 0

        for sentence, score, word_count in scored:
            if current_words + word_count <= max_words:
                selected.append(sentence)
                current_words += word_count

        # Reorder by original position
        selected_with_pos = []
        for i, sentence in enumerate(sentences):
            if sentence in selected:
                selected_with_pos.append((sentence, i))

        selected_with_pos.sort(key=lambda x: x[1])
        return [s[0] for s in selected_with_pos]

    def _generate_concise_summary(
        self,
        text: str,
        paper: 'Paper',
        max_words: int = 200
    ) -> str:
        """Generate a concise summary."""
        # Calculate word allocation
        alloc = self._allocate_words(paper, max_words)

        sentences = self._extract_key_sentences(text, alloc['content'], paper)

        # Build summary
        summary_parts = []

        # Title and year
        if hasattr(paper, 'title') and paper.title:
            summary_parts.append(f"**{paper.title}**")
            if paper.year:
                summary_parts.append(f"({paper.year})")
            summary_parts.append("\n")

        # Authors
        if hasattr(paper, 'authors') and paper.authors:
            authors_str = ', '.join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += ' et al.'
            summary_parts.append(f"*Authors: {authors_str}*\n")

        # Key content
        if sentences:
            # First sentence as hook
            summary_parts.append(sentences[0])

            # Add more if space allows
            if len(sentences) > 1:
                # Add sentences that mention key findings
                for sentence in sentences[1:4]:
                    if re.search(r'(?i)(find|demonstrate|show|suggest|result)', sentence):
                        summary_parts.append(sentence)
                        break

        summary = ' '.join(summary_parts)

        # Truncate if needed
        words = summary.split()
        if len(words) > max_words:
            summary = ' '.join(words[:max_words]) + '...'

        return summary.strip()

    def _generate_detailed_summary(
        self,
        text: str,
        paper: 'Paper',
        max_words: int = 500
    ) -> str:
        """Generate a detailed summary."""
        alloc = self._allocate_words(paper, max_words)

        sentences = self._extract_key_sentences(text, alloc['content'], paper)

        summary_parts = []

        # Header
        if hasattr(paper, 'title') and paper.title:
            summary_parts.append(f"# {paper.title}")
            summary_parts.append(f"\n**Year:** {paper.year}" if paper.year else "")
            summary_parts.append(f"\n**Authors:** {', '.join(paper.authors[:5])}" if paper.authors else "")
            if hasattr(paper, 'citation_count') and paper.citation_count:
                summary_parts.append(f"\n**Citations:** {paper.citation_count}")
            summary_parts.append("\n---\n")

        # Abstract
        if hasattr(paper, 'abstract') and paper.abstract:
            abstract = paper.abstract[:alloc['abstract']]
            summary_parts.append(f"## Abstract\n{abstract}\n\n")

        # Key Findings Section
        if hasattr(paper, 'key_findings') and paper.key_findings:
            summary_parts.append("## Key Findings\n")
            for i, finding in enumerate(paper.key_findings[:5], 1):
                summary_parts.append(f"{i}. {finding}")
            summary_parts.append("\n")

        # Methodology
        if hasattr(paper, 'methodology') and paper.methodology:
            methodology = self._split_into_sentences(paper.methodology)
            if methodology:
                summary_parts.append("## Methodology\n")
                for method in methodology[:3]:
                    summary_parts.append(f"- {method}")
                summary_parts.append("\n")

        return ''.join(summary_parts).strip()

    def _generate_bullet_summary(
        self,
        text: str,
        paper: 'Paper',
        max_words: int = 200
    ) -> str:
        """Generate a bullet point summary."""
        alloc = self._allocate_words(paper, max_words)

        summary_parts = []

        # Title
        if hasattr(paper, 'title') and paper.title:
            summary_parts.append(f"📄 **{paper.title}**")
            if paper.year:
                summary_parts.append(f" ({paper.year})")
            summary_parts.append("\n\n")

        # Paper info
        if hasattr(paper, 'authors') and paper.authors:
            authors_str = ', '.join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += ' et al.'
            summary_parts.append(f"👥 **Authors:** {authors_str}\n")

        if hasattr(paper, 'venue') and paper.venue:
            summary_parts.append(f"📖 **Venue:** {paper.venue}\n")

        if hasattr(paper, 'citation_count') and paper.citation_count:
            summary_parts.append(f"📊 **Citations:** {paper.citation_count}\n")

        summary_parts.append("\n---\n")

        # Key points
        summary_parts.append("📋 **Key Points:**\n")

        # Extract key sentences
        sentences = self._extract_key_sentences(text, alloc['content'], paper)

        for i, sentence in enumerate(sentences[:6], 1):
            # Clean up sentence
            clean = sentence.strip()
            if len(clean) > 10:
                summary_parts.append(f"{i}. {clean}\n")

        # Topics
        if hasattr(paper, 'topics') and paper.topics:
            summary_parts.append("\n🏷️ **Topics:** ")
            summary_parts.append(', '.join(paper.topics[:5]))

        return ''.join(summary_parts).strip()

    def _generate_abstract_style(
        self,
        text: str,
        paper: 'Paper',
        max_words: int = 250
    ) -> str:
        """Generate an abstract-style summary."""
        alloc = self._allocate_words(paper, max_words)

        sentences = self._extract_key_sentences(text, alloc['content'], paper)

        summary_parts = []

        # Title and authors on first line
        if hasattr(paper, 'title') and paper.title:
            summary_parts.append(paper.title)

        if hasattr(paper, 'authors') and paper.authors:
            authors_str = ', '.join(paper.authors[:5])
            if len(paper.authors) > 5:
                authors_str += ' et al.'
            summary_parts.append(f"— {authors_str}")

        if paper.year:
            summary_parts.append(f"({paper.year})")

        summary_parts.append("\n\n")

        # Abstract body
        if sentences:
            # Combine key sentences in abstract style
            abstract_sentences = sentences[:3]

            # Ensure it reads like an abstract
            if abstract_sentences:
                # First sentence context
                if len(abstract_sentences) > 1:
                    # Lead with context
                    summary_parts.append("This study ")
                    summary_parts.append(abstract_sentences[1].lower())

                # Add more content
                for sentence in abstract_sentences[1:]:
                    clean = sentence.strip()
                    if clean and len(summary_parts[0].split()) + len(clean.split()) < max_words:
                        summary_parts.append(f" {clean}")

        # Add keywords
        if hasattr(paper, 'topics') and paper.topics:
            summary_parts.append(f"\n**Keywords:** {', '.join(paper.topics[:5])}")

        return ''.join(summary_parts).strip()

    def _generate_findings_summary(
        self,
        paper: 'Paper',
        max_words: int = 200
    ) -> str:
        """Generate a summary focused on key findings."""
        summary_parts = []

        if hasattr(paper, 'title') and paper.title:
            summary_parts.append(f"**{paper.title}**")
            if paper.year:
                summary_parts.append(f" ({paper.year})")
            summary_parts.append("\n\n")

        # Key findings
        findings = getattr(paper, 'key_findings', [])

        if findings:
            summary_parts.append("## Key Findings\n\n")
            for i, finding in enumerate(findings[:7], 1):
                # Truncate long findings
                words = finding.split()
                if len(words) > 50:
                    finding = ' '.join(words[:50]) + '...'
                summary_parts.append(f"{i}. {finding}\n")
        else:
            # Fallback to abstract
            if hasattr(paper, 'abstract') and paper.abstract:
                summary_parts.append("## Main Result\n")
                abstract_words = paper.abstract.split()[:max_words]
                summary_parts.append(' '.join(abstract_words))

        return ''.join(summary_parts).strip()

    def _allocate_words(
        self,
        paper: 'Paper',
        max_words: int
    ) -> Dict[str, int]:
        """Allocate word count across sections."""
        return {
            'title': min(50, max_words // 10),
            'meta': min(30, max_words // 15),
            'abstract': min(max_words // 2, max_words * 3 // 5),
            'content': max_words - 100,  # Reserve 100 for header
        }

    def generate_comparative_summary(
        self,
        papers: List['Paper'],
        focus: str = "methodology"
    ) -> str:
        """
        Generate a comparative summary across multiple papers.

        Args:
            papers: List of Paper objects.
            focus: Comparison focus ('methodology', 'findings', 'topics').

        Returns:
            Comparative summary string.
        """
        if not papers:
            return "No papers provided."

        summary_parts = [
            f"# Comparative Analysis: {len(papers)} Papers\n\n"
        ]

        # Group by focus
        if focus == 'methodology':
            summary_parts.append("## Methodologies\n\n")
            for i, paper in enumerate(papers, 1):
                summary_parts.append(f"### {i}. {paper.title[:50]}...\n")
                method = getattr(paper, 'methodology', '')[:300]
                summary_parts.append(f"**Method:** {method or 'Not specified'}\n\n")

        elif focus == 'findings':
            summary_parts.append("## Key Findings\n\n")
            for i, paper in enumerate(papers, 1):
                summary_parts.append(f"### {i}. {paper.title[:50]}...\n")
                findings = getattr(paper, 'key_findings', [])
                if findings:
                    for finding in findings[:2]:
                        summary_parts.append(f"- {finding[:200]}...\n")
                else:
                    summary_parts.append("- No findings extracted\n")
                summary_parts.append("\n")

        elif focus == 'topics':
            summary_parts.append("## Topics Coverage\n\n")

            # Collect all topics
            all_topics = {}
            for paper in papers:
                for topic in paper.topics:
                    all_topics[topic] = all_topics.get(topic, 0) + 1

            # Sort by frequency
            sorted_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)

            summary_parts.append("### Common Topics\n")
            for topic, count in sorted_topics[:15]:
                papers_mentioning = [p.title[:30] for p in papers if topic in p.topics]
                summary_parts.append(f"- **{topic}** ({count} papers)\n")

        return ''.join(summary_parts)

    def extract_highlights(self, paper: 'Paper', num_highlights: int = 5) -> List[str]:
        """
        Extract key highlights from a paper.

        Args:
            paper: Paper object.
            num_highlights: Number of highlights to extract.

        Returns:
            List of highlight strings.
        """
        highlights = []

        # Priority order for highlights
        priority_sources = [
            ('key_findings', 'key_findings'),
            ('abstract', 'abstract'),
            ('methodology', 'methodology'),
        ]

        for attr_name, source_type in priority_sources:
            attr = getattr(paper, attr_name, None)
            if attr:
                if isinstance(attr, list):
                    highlights.extend(attr)
                elif isinstance(attr, str) and attr:
                    sentences = self._split_into_sentences(attr)
                    highlights.extend(sentences)

        # Deduplicate and score
        seen = set()
        scored = []

        for highlight in highlights:
            clean = highlight.strip()
            key = clean.lower()[:50]

            if key not in seen and len(clean) > 30:
                seen.add(key)

                # Score based on keywords and features
                score = 0
                if re.search(r'(?i)(we (find|demonstrate|show)|result|conclusion)', clean):
                    score += 2
                if re.search(r'(?i)(significant|important|crucial)', clean):
                    score += 1
                if len(clean) < 200:
                    score += 0.5

                scored.append((clean, score))

        # Sort by score and return top highlights
        scored.sort(key=lambda x: x[1], reverse=True)

        return [h[0] for h in scored[:num_highlights]]


# Make Paper available reference
if __name__ == "__main__":
    print("Summarizer Module")
    print("=" * 50)
    print("This module generates paper summaries.")
    print("\nStyles available:")
    print("- concise: Brief overview (100-200 words)")
    print("- detailed: Comprehensive summary")
    print("- bullet_points: Key points as bullets")
    print("- abstract_style: Like a paper abstract")
    print("- key_findings: Focus on findings only")
    print("\nImport and use with ResearchAssistant class.")
