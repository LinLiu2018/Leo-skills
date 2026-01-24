#!/usr/bin/env python3
"""
Tech Extractor - Technical Information Extraction Skill

A comprehensive technical information extraction system for:
- Technology trend analysis
- Technical document processing
- API documentation extraction
- Code pattern analysis
- Technology stack identification

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import logging
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.text_processor import TextProcessor
from utils.tech_classifier import TechClassifier
from utils.pattern_matcher import PatternMatcher
from utils.trend_analyzer import TrendAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Technology:
    """Data class representing a technology or tool."""
    name: str
    category: str  # programming_language, framework, library, tool, platform
    description: str = ""
    version: str = ""
    url: str = ""
    documentation_url: str = ""
    github_url: str = ""
    license: str = ""
    popularity_score: float = 0.0
    related_tech: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert Technology to dictionary."""
        return {
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'version': self.version,
            'url': self.url,
            'documentation_url': self.documentation_url,
            'github_url': self.github_url,
            'license': self.license,
            'popularity_score': self.popularity_score,
            'related_tech': self.related_tech,
            'features': self.features,
            'use_cases': self.use_cases,
            'pros': self.pros,
            'cons': self.cons,
            'alternatives': self.alternatives,
            'last_updated': self.last_updated
        }


@dataclass
class TechTrend:
    """Data class representing a technology trend."""
    technology: str
    trend_type: str  # rising, falling, stable, emerging
    growth_rate: float
    mentions: int
    sentiment: float  # -1 to 1
    time_period: str
    sources: List[str] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    market_impact: str = ""
    prediction: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert TechTrend to dictionary."""
        return {
            'technology': self.technology,
            'trend_type': self.trend_type,
            'growth_rate': self.growth_rate,
            'mentions': self.mentions,
            'sentiment': self.sentiment,
            'time_period': self.time_period,
            'sources': self.sources,
            'related_keywords': self.related_keywords,
            'market_impact': self.market_impact,
            'prediction': self.prediction
        }


class TechExtractor:
    """
    Main Tech Extractor class for technical information extraction.

    This class provides a unified interface for:
    - Technology identification and classification
    - Trend analysis from various sources
    - Technical document processing
    - API documentation extraction
    - Code pattern analysis
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Tech Extractor.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.text_processor = TextProcessor(config=self.config)
        self.tech_classifier = TechClassifier(config=self.config)
        self.pattern_matcher = PatternMatcher(config=self.config)
        self.trend_analyzer = TrendAnalyzer(config=self.config)

        logger.info("Tech Extractor initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'enable_cache': True,
            'cache_days': 7,
            'trend_sources': ['github', 'stackoverflow', 'reddit', 'news'],
            'min_confidence': 0.7,
            'max_results': 50,
            'languages': ['en', 'zh', 'ja', 'ko']
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config

    def extract_from_text(self, text: str, source_type: str = "auto") -> List[Technology]:
        """
        Extract technologies from text.

        Args:
            text: Input text to analyze.
            source_type: Type of source ('article', 'documentation', 'code', 'auto').

        Returns:
            List of Technology objects.
        """
        logger.info(f"Extracting technologies from text ({len(text)} chars)")

        # Preprocess text
        processed_text = self.text_processor.preprocess(text)
        
        # Classify source type if auto
        if source_type == "auto":
            source_type = self.text_processor.classify_source(text)
        
        # Extract technology mentions
        mentions = self.tech_classifier.extract_mentions(processed_text.cleaned, source_type)
        
        # Convert to Technology objects
        technologies = []
        for mention in mentions:
            if mention['confidence'] >= self.config['min_confidence']:
                tech = Technology(
                    name=mention['name'],
                    category=mention['category'],
                    version=mention.get('version', ''),
                    description=mention.get('description', '')
                )
                technologies.append(tech)

        logger.info(f"Extracted {len(technologies)} technologies")
        return technologies

    def extract_from_documentation(self, doc_url: str) -> List[Technology]:
        """
        Extract technologies from API documentation.

        Args:
            doc_url: URL of the documentation.

        Returns:
            List of Technology objects.
        """
        logger.info(f"Extracting technologies from documentation: {doc_url}")

        # Fetch documentation content
        content = self.text_processor.fetch_web_content(doc_url)
        if not content:
            logger.error(f"Could not fetch content from {doc_url}")
            return []

        # Extract technologies with documentation-specific processing
        technologies = self.extract_from_text(content, source_type="documentation")
        
        # Enhance with documentation-specific information
        for tech in technologies:
            if not tech.documentation_url:
                tech.documentation_url = doc_url
            
            # Extract additional info from documentation
            additional_info = self._extract_doc_info(content, tech.name)
            tech.features.extend(additional_info.get('features', []))
            tech.use_cases.extend(additional_info.get('use_cases', []))

        return technologies

    def extract_from_code(self, code: str, language: str = "auto") -> List[Technology]:
        """
        Extract technologies from source code.

        Args:
            code: Source code to analyze.
            language: Programming language ('auto' for detection).

        Returns:
            List of Technology objects.
        """
        logger.info(f"Extracting technologies from code ({len(code)} chars)")

        # Detect language if auto
        if language == "auto":
            language = self.text_processor.detect_language(code)
        
        # Extract imports, dependencies, etc.
        dependencies = self.pattern_matcher.extract_dependencies(code, language)
        
        # Convert to Technology objects
        technologies = []
        for dep in dependencies:
            tech = Technology(
                name=dep['name'],
                category=dep['category'],
                version=dep.get('version', ''),
                description=dep.get('description', '')
            )
            technologies.append(tech)

        return technologies

    def analyze_trends(self, 
                       technologies: List[str],
                       time_period: str = "1y",
                       sources: Optional[List[str]] = None) -> List[TechTrend]:
        """
        Analyze trends for specified technologies.

        Args:
            technologies: List of technology names to analyze.
            time_period: Time period ('1m', '3m', '6m', '1y', '2y').
            sources: List of sources to analyze.

        Returns:
            List of TechTrend objects.
        """
        logger.info(f"Analyzing trends for {len(technologies)} technologies")

        if sources is None:
            sources = self.config['trend_sources']

        trends = []
        for tech in technologies:
            try:
                trend_data = self.trend_analyzer.analyze_trend(
                    technology=tech,
                    time_period=time_period,
                    sources=sources
                )
                
                trend = TechTrend(
                    technology=tech,
                    trend_type=trend_data['trend_type'],
                    growth_rate=trend_data['growth_rate'],
                    mentions=trend_data['mentions'],
                    sentiment=trend_data['sentiment'],
                    time_period=time_period,
                    sources=trend_data['sources'],
                    related_keywords=trend_data['related_keywords'],
                    market_impact=trend_data['market_impact'],
                    prediction=trend_data['prediction']
                )
                trends.append(trend)
                
            except Exception as e:
                logger.warning(f"Could not analyze trend for {tech}: {e}")

        return trends

    def extract_from_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Extract comprehensive tech information from a repository.

        Args:
            repo_url: URL of the repository (GitHub, GitLab, etc.).

        Returns:
            Dictionary containing extracted information.
        """
        logger.info(f"Extracting tech info from repository: {repo_url}")

        # Fetch repository information
        repo_info = self._fetch_repository_info(repo_url)
        
        # Extract from README
        readme_tech = []
        if repo_info.get('readme'):
            readme_tech = self.extract_from_text(repo_info['readme'], source_type="documentation")
        
        # Extract from package files
        package_tech = []
        for file_path, content in repo_info.get('package_files', {}).items():
            package_tech.extend(self.extract_from_code(content, language="json"))
        
        # Extract from source code
        source_tech = []
        for file_path, content in repo_info.get('source_files', {}).items():
            language = self._get_language_from_path(file_path)
            source_tech.extend(self.extract_from_code(content, language=language))
        
        # Merge and deduplicate
        all_technologies = readme_tech + package_tech + source_tech
        merged_tech = self._merge_technologies(all_technologies)
        
        return {
            'repository': repo_info,
            'technologies': [tech.to_dict() for tech in merged_tech],
            'tech_stack': self._categorize_tech_stack(merged_tech),
            'summary': self._generate_repo_summary(repo_info, merged_tech)
        }

    def _extract_doc_info(self, content: str, tech_name: str) -> Dict[str, List[str]]:
        """Extract additional information from documentation."""
        info = {'features': [], 'use_cases': []}
        
        # Look for specific patterns
        feature_patterns = [
            r'features?:\s*([^\n]+)',
            r'capabilities?:\s*([^\n]+)',
            r'what.*can.*do:\s*([^\n]+)'
        ]
        
        use_case_patterns = [
            r'use cases?:\s*([^\n]+)',
            r'examples?:\s*([^\n]+)',
            r'when to use:\s*([^\n]+)'
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            info['features'].extend(matches)
        
        for pattern in use_case_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            info['use_cases'].extend(matches)
        
        return info

    def _fetch_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Fetch repository information from URL."""
        # This would integrate with GitHub API, GitLab API, etc.
        # For now, return placeholder
        return {
            'url': repo_url,
            'name': 'example-repo',
            'description': 'Example repository',
            'readme': '',
            'package_files': {},
            'source_files': {}
        }

    def _get_language_from_path(self, file_path: str) -> str:
        """Determine programming language from file path."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        return language_map.get(ext, 'unknown')

    def _merge_technologies(self, technologies: List[Technology]) -> List[Technology]:
        """Merge duplicate technologies and combine information."""
        tech_map = {}
        
        for tech in technologies:
            key = tech.name.lower()
            if key not in tech_map:
                tech_map[key] = tech
            else:
                existing = tech_map[key]
                # Merge information
                existing.features.extend(tech.features)
                existing.use_cases.extend(tech.use_cases)
                existing.pros.extend(tech.pros)
                existing.cons.extend(tech.cons)
                existing.alternatives.extend(tech.alternatives)
                
                # Remove duplicates
                for attr in ['features', 'use_cases', 'pros', 'cons', 'alternatives']:
                    setattr(existing, attr, list(set(getattr(existing, attr))))
        
        return list(tech_map.values())

    def _categorize_tech_stack(self, technologies: List[Technology]) -> Dict[str, List[str]]:
        """Categorize technologies into stack categories."""
        stack = {
            'languages': [],
            'frameworks': [],
            'libraries': [],
            'tools': [],
            'platforms': [],
            'databases': []
        }
        
        for tech in technologies:
            if tech.category == 'programming_language':
                stack['languages'].append(tech.name)
            elif tech.category == 'framework':
                stack['frameworks'].append(tech.name)
            elif tech.category == 'library':
                stack['libraries'].append(tech.name)
            elif tech.category == 'tool':
                stack['tools'].append(tech.name)
            elif tech.category == 'platform':
                stack['platforms'].append(tech.name)
            elif tech.category == 'database':
                stack['databases'].append(tech.name)
        
        return stack

    def _generate_repo_summary(self, repo_info: Dict, technologies: List[Technology]) -> str:
        """Generate a summary of the repository tech stack."""
        tech_names = [tech.name for tech in technologies]
        stack = self._categorize_tech_stack(technologies)
        
        summary_parts = [
            f"Repository: {repo_info.get('name', 'Unknown')}",
            f"Description: {repo_info.get('description', 'No description')}",
            "",
            "Technology Stack:",
        ]
        
        for category, tech_list in stack.items():
            if tech_list:
                summary_parts.append(f"- {category.title()}: {', '.join(tech_list)}")
        
        return "\n".join(summary_parts)

    def export_technologies(self, 
                           technologies: List[Technology],
                           format: str = "json",
                           output_path: str = "technologies") -> str:
        """
        Export technologies to file.

        Args:
            technologies: List of Technology objects.
            format: Export format ('json', 'csv', 'yaml').
            output_path: Base path for output file.

        Returns:
            Path to exported file.
        """
        logger.info(f"Exporting {len(technologies)} technologies to {format}")

        if format == "json":
            content = json.dumps([tech.to_dict() for tech in technologies], indent=2)
            ext = "json"
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['name', 'category', 'description', 'version', 'license'])
            
            for tech in technologies:
                writer.writerow([
                    tech.name, tech.category, tech.description, 
                    tech.version, tech.license
                ])
            
            content = output.getvalue()
            ext = "csv"
        elif format == "yaml":
            import yaml
            content = yaml.dump([tech.to_dict() for tech in technologies])
            ext = "yaml"
        else:
            raise ValueError(f"Unsupported format: {format}")

        file_path = f"{output_path}.{ext}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Technologies exported to: {file_path}")
        return file_path


def main():
    """Main entry point for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Tech Extractor CLI")
    parser.add_argument(
        "command",
        choices=["extract-text", "extract-doc", "extract-code", "analyze-trends", "extract-repo"],
        help="Command to execute"
    )
    parser.add_argument("input", help="Input text, URL, or file path")
    parser.add_argument("--format", default="json", help="Output format")
    parser.add_argument("--output", default="output", help="Output file path")
    parser.add_argument("--language", help="Programming language for code extraction")
    parser.add_argument("--period", default="1y", help="Time period for trend analysis")

    args = parser.parse_args()

    extractor = TechExtractor()

    if args.command == "extract-text":
        if os.path.exists(args.input):
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.input
        
        technologies = extractor.extract_from_text(text)
        file_path = extractor.export_technologies(technologies, args.format, args.output)
        print(f"Extracted {len(technologies)} technologies to {file_path}")

    elif args.command == "extract-doc":
        technologies = extractor.extract_from_documentation(args.input)
        file_path = extractor.export_technologies(technologies, args.format, args.output)
        print(f"Extracted {len(technologies)} technologies to {file_path}")

    elif args.command == "extract-code":
        if os.path.exists(args.input):
            with open(args.input, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            code = args.input
        
        language = args.language or "auto"
        technologies = extractor.extract_from_code(code, language)
        file_path = extractor.export_technologies(technologies, args.format, args.output)
        print(f"Extracted {len(technologies)} technologies to {file_path}")

    elif args.command == "analyze-trends":
        # Parse technologies (comma-separated)
        technologies = [tech.strip() for tech in args.input.split(',')]
        trends = extractor.analyze_trends(technologies, args.period)
        
        if args.format == "json":
            content = json.dumps([trend.to_dict() for trend in trends], indent=2)
        else:
            content = "\n".join([
                f"{trend.technology}: {trend.trend_type} ({trend.growth_rate:+.1f}%)"
                for trend in trends
            ])
        
        file_path = f"{args.output}.{args.format}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Analyzed trends for {len(trends)} technologies to {file_path}")

    elif args.command == "extract-repo":
        repo_info = extractor.extract_from_repository(args.input)
        
        file_path = f"{args.output}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(repo_info, f, indent=2, ensure_ascii=False)
        print(f"Extracted repository info to {file_path}")


if __name__ == "__main__":
    main()