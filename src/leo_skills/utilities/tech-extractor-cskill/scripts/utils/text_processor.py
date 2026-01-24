"""
Text processing utilities for Tech Extractor.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessedText:
    """Data class for processed text information."""
    original: str
    cleaned: str
    sentences: List[str]
    tokens: List[str]
    entities: List[Dict[str, str]]
    language: str
    source_type: str


class TextProcessor:
    """Text processing utilities for technology extraction."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Text Processor.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.tech_keywords = self._load_tech_keywords()
        self.source_patterns = self._load_source_patterns()
    
    def _load_tech_keywords(self) -> Dict[str, List[str]]:
        """Load technology keywords by category."""
        return {
            'programming_languages': [
                'python', 'javascript', 'typescript', 'java', 'c++', 'c', 'go', 'rust',
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'c#', 'dart', 'r', 'matlab'
            ],
            'frameworks': [
                'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring',
                'laravel', 'rails', 'next.js', 'nuxt', 'svelte', 'flutter', 'electron'
            ],
            'libraries': [
                'numpy', 'pandas', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'matplotlib',
                'jquery', 'lodash', 'axios', 'requests', 'beautifulsoup', 'selenium', 'puppeteer'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'elasticsearch', 'cassandra',
                'dynamodb', 'neo4j', 'influxdb', 'firebase', 'supabase'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'vercel', 'netlify', 'digitalocean',
                'alibaba cloud', 'oracle cloud', 'ibm cloud'
            ],
            'tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
                'webpack', 'babel', 'eslint', 'prettier', 'vscode', 'vim', 'emacs'
            ]
        }
    
    def _load_source_patterns(self) -> Dict[str, List[str]]:
        """Load patterns to identify source types."""
        return {
            'documentation': [
                r'api\s+reference', r'documentation', r'getting\s+started', r'installation',
                r'quick\s+start', r'tutorial', r'guide', r'examples?', r'readme\.md'
            ],
            'code': [
                r'import\s+\w+', r'from\s+\w+\s+import', r'require\s*\(', r'function\s+\w+',
                r'class\s+\w+', r'def\s+\w+', r'const\s+\w+', r'let\s+\w+', r'var\s+\w+'
            ],
            'article': [
                r'introduction', r'overview', r'summary', r'conclusion', r'abstract',
                r'background', r'methodology', r'results', r'discussion'
            ],
            'news': [
                r'breaking:', r'announcement', r'release', r'update', r'launch', r'unveiled',
                r'revealed', r'confirmed', r'reported', r'according\s+to'
            ]
        }
    
    def preprocess(self, text: str) -> ProcessedText:
        """
        Preprocess text for analysis.
        
        Args:
            text: Input text to preprocess.
            
        Returns:
            ProcessedText object with processed information.
        """
        # Clean text
        cleaned = self._clean_text(text)
        
        # Split into sentences
        sentences = self._split_sentences(cleaned)
        
        # Tokenize
        tokens = self._tokenize(cleaned)
        
        # Extract entities
        entities = self._extract_entities(cleaned)
        
        # Detect language
        language = self._detect_language(cleaned)
        
        # Classify source type
        source_type = self.classify_source(text)
        
        return ProcessedText(
            original=text,
            cleaned=cleaned,
            sentences=sentences,
            tokens=tokens,
            entities=entities,
            language=language,
            source_type=source_type
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\,\!\?\-\+\=\(\)\[\]\{\}\:\;\/\\]', ' ', text)
        
        # Normalize case
        text = text.strip()
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting based on punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Simple tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        entities = []
        
        # Extract technology mentions
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'type': 'technology',
                        'category': category,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return entities
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        # Simple language detection based on character patterns
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'
        elif re.search(r'[\uac00-\ud7af]', text):
            return 'ko'
        else:
            return 'en'
    
    def classify_source(self, text: str) -> str:
        """
        Classify the type of source text.
        
        Args:
            text: Input text to classify.
            
        Returns:
            Source type string.
        """
        scores = {}
        
        for source_type, patterns in self.source_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            scores[source_type] = score
        
        # Return the type with highest score
        if max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)
    
    def fetch_web_content(self, url: str) -> Optional[str]:
        """
        Fetch content from web URL.
        
        Args:
            url: URL to fetch.
            
        Returns:
            Content string or None if failed.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return None
    
    def detect_language(self, code: str) -> str:
        """
        Detect programming language from code.
        
        Args:
            code: Source code string.
            
        Returns:
            Programming language string.
        """
        language_patterns = {
            'python': [
                r'import\s+\w+', r'from\s+\w+\s+import', r'def\s+\w+\s*\(',
                r'class\s+\w+\s*:', r'if\s+__name__\s*==\s*["\']__main__["\']'
            ],
            'javascript': [
                r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=',
                r'var\s+\w+\s*=', r'console\.\w+', r'require\s*\('
            ],
            'typescript': [
                r'interface\s+\w+', r'type\s+\w+\s*=', r'as\s+\w+',
                r':\s*\w+\[\]', r'<\w+>', r'private\s+\w+'
            ],
            'java': [
                r'public\s+class\s+\w+', r'import\s+java\.', r'public\s+static\s+void\s+main',
                r'System\.out\.print', r'@\w+', r'implements\s+\w+'
            ],
            'cpp': [
                r'#include\s*<\w+>', r'using\s+namespace\s+\w+', r'int\s+main\s*\(',
                r'std::', r'->', r'::\w+'
            ],
            'go': [
                r'package\s+\w+', r'import\s*\(', r'func\s+\w+\s*\(',
                r'go\s+\w+\s*\(', r'make\s*\(', r'chan\s+\w+'
            ],
            'rust': [
                r'use\s+\w+::', r'fn\s+\w+\s*\(', r'let\s+mut\s+\w+',
                r'impl\s+\w+', r'Trait', r'match\s+\w+'
            ],
            'php': [
                r'<\?php', r'\$\w+', r'function\s+\w+\s*\(', r'public\s+function',
                r'echo\s+', r'include\s+', r'require\s+'
            ]
        }
        
        scores = {}
        
        for language, patterns in language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, code, re.IGNORECASE)
                score += len(matches)
            scores[language] = score
        
        if max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)