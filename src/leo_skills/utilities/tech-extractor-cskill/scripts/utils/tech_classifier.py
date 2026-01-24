"""
Technology classification utilities for Tech Extractor.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TechMention:
    """Data class for technology mention."""
    name: str
    category: str
    confidence: float
    context: str
    version: Optional[str] = None
    description: Optional[str] = None


class TechClassifier:
    """Technology classification utilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Tech Classifier.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.tech_database = self._load_tech_database()
        self.patterns = self._load_patterns()
    
    def _load_tech_database(self) -> Dict[str, Dict[str, Any]]:
        """Load technology database with classifications."""
        return {
            # Programming Languages
            'python': {
                'category': 'programming_language',
                'aliases': ['py', 'python3'],
                'patterns': [r'python\s*(\d+\.\d+)?'],
                'description': 'High-level programming language',
                'common_versions': ['3.9', '3.10', '3.11', '3.12']
            },
            'javascript': {
                'category': 'programming_language',
                'aliases': ['js', 'ecmascript'],
                'patterns': [r'javascript\s*(es(\d+))?'],
                'description': 'Dynamic programming language',
                'common_versions': ['es6', 'es2020', 'es2021']
            },
            'typescript': {
                'category': 'programming_language',
                'aliases': ['ts'],
                'patterns': [r'typescript\s*(\d+\.\d+)?'],
                'description': 'Typed superset of JavaScript',
                'common_versions': ['4.9', '5.0']
            },
            'java': {
                'category': 'programming_language',
                'aliases': [],
                'patterns': [r'java\s*(\d+)?'],
                'description': 'Object-oriented programming language',
                'common_versions': ['8', '11', '17', '21']
            },
            'go': {
                'category': 'programming_language',
                'aliases': ['golang'],
                'patterns': [r'go\s*(\d+\.\d+)?'],
                'description': 'Statically typed programming language',
                'common_versions': ['1.20', '1.21']
            },
            'rust': {
                'category': 'programming_language',
                'aliases': [],
                'patterns': [r'rust\s*(\d+\.\d+)?'],
                'description': 'Systems programming language',
                'common_versions': ['1.70', '1.75']
            },
            
            # Frameworks
            'react': {
                'category': 'framework',
                'aliases': ['reactjs'],
                'patterns': [r'react\s*(\d+\.\d+\.\d+)?'],
                'description': 'JavaScript library for building UIs',
                'common_versions': ['18.2', '18.3']
            },
            'vue': {
                'category': 'framework',
                'aliases': ['vuejs'],
                'patterns': [r'vue\s*(\d+\.\d+\.\d+)?'],
                'description': 'Progressive JavaScript framework',
                'common_versions': ['3.3', '3.4']
            },
            'angular': {
                'category': 'framework',
                'aliases': [],
                'patterns': [r'angular\s*(\d+\.\d+\.\d+)?'],
                'description': 'Platform for building mobile and desktop web apps',
                'common_versions': ['16.2', '17.0']
            },
            'django': {
                'category': 'framework',
                'aliases': [],
                'patterns': [r'django\s*(\d+\.\d+)?'],
                'description': 'Python web framework',
                'common_versions': ['4.2', '5.0']
            },
            'flask': {
                'category': 'framework',
                'aliases': [],
                'patterns': [r'flask\s*(\d+\.\d+)?'],
                'description': 'Python web microframework',
                'common_versions': ['2.3', '3.0']
            },
            'fastapi': {
                'category': 'framework',
                'aliases': [],
                'patterns': [r'fastapi\s*(\d+\.\d+)?'],
                'description': 'Modern Python web framework',
                'common_versions': ['0.104', '0.105']
            },
            'express': {
                'category': 'framework',
                'aliases': ['expressjs'],
                'patterns': [r'express\s*(\d+\.\d+)?'],
                'description': 'Node.js web application framework',
                'common_versions': ['4.18']
            },
            'spring': {
                'category': 'framework',
                'aliases': ['spring boot'],
                'patterns': [r'spring\s*(boot)?\s*(\d+\.\d+)?'],
                'description': 'Java application framework',
                'common_versions': ['3.1', '3.2']
            },
            
            # Libraries
            'numpy': {
                'category': 'library',
                'aliases': [],
                'patterns': [r'numpy\s*(\d+\.\d+)?'],
                'description': 'Python numerical computing library',
                'common_versions': ['1.24', '1.25']
            },
            'pandas': {
                'category': 'library',
                'aliases': [],
                'patterns': [r'pandas\s*(\d+\.\d+)?'],
                'description': 'Python data analysis library',
                'common_versions': ['2.0', '2.1']
            },
            'tensorflow': {
                'category': 'library',
                'aliases': ['tf'],
                'patterns': [r'tensorflow\s*(\d+\.\d+)?'],
                'description': 'Machine learning framework',
                'common_versions': ['2.13', '2.14']
            },
            'pytorch': {
                'category': 'library',
                'aliases': [],
                'patterns': [r'pytorch\s*(\d+\.\d+)?'],
                'description': 'Deep learning framework',
                'common_versions': ['2.0', '2.1']
            },
            'scikit-learn': {
                'category': 'library',
                'aliases': ['sklearn'],
                'patterns': [r'scikit-learn\s*(\d+\.\d+)?'],
                'description': 'Machine learning library for Python',
                'common_versions': ['1.3']
            },
            'matplotlib': {
                'category': 'library',
                'aliases': [],
                'patterns': [r'matplotlib\s*(\d+\.\d+)?'],
                'description': 'Python plotting library',
                'common_versions': ['3.7', '3.8']
            },
            
            # Databases
            'mysql': {
                'category': 'database',
                'aliases': [],
                'patterns': [r'mysql\s*(\d+\.\d+)?'],
                'description': 'Open-source relational database',
                'common_versions': ['8.0', '8.1']
            },
            'postgresql': {
                'category': 'database',
                'aliases': ['postgres'],
                'patterns': [r'postgresql\s*(\d+)?'],
                'description': 'Open-source relational database',
                'common_versions': ['14', '15', '16']
            },
            'mongodb': {
                'category': 'database',
                'aliases': ['mongo'],
                'patterns': [r'mongodb\s*(\d+\.\d+)?'],
                'description': 'NoSQL document database',
                'common_versions': ['6.0', '7.0']
            },
            'redis': {
                'category': 'database',
                'aliases': [],
                'patterns': [r'redis\s*(\d+\.\d+)?'],
                'description': 'In-memory data structure store',
                'common_versions': ['7.0', '7.2']
            },
            'sqlite': {
                'category': 'database',
                'aliases': [],
                'patterns': [r'sqlite\s*(\d+)?'],
                'description': 'Embedded SQL database engine',
                'common_versions': ['3']
            },
            
            # Cloud Platforms
            'aws': {
                'category': 'platform',
                'aliases': ['amazon web services'],
                'patterns': [r'aws'],
                'description': 'Amazon Web Services cloud platform',
                'common_versions': []
            },
            'azure': {
                'category': 'platform',
                'aliases': ['microsoft azure'],
                'patterns': [r'azure'],
                'description': 'Microsoft cloud platform',
                'common_versions': []
            },
            'google cloud': {
                'category': 'platform',
                'aliases': ['gcp'],
                'patterns': [r'google cloud|gcp'],
                'description': 'Google Cloud Platform',
                'common_versions': []
            },
            'heroku': {
                'category': 'platform',
                'aliases': [],
                'patterns': [r'heroku'],
                'description': 'Cloud platform as a service',
                'common_versions': []
            },
            'vercel': {
                'category': 'platform',
                'aliases': [],
                'patterns': [r'vercel'],
                'description': 'Cloud platform for frontend frameworks',
                'common_versions': []
            },
            'netlify': {
                'category': 'platform',
                'aliases': [],
                'patterns': [r'netlify'],
                'description': 'Cloud platform for static sites',
                'common_versions': []
            },
            
            # Tools
            'docker': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'docker\s*(\d+\.\d+)?'],
                'description': 'Container platform',
                'common_versions': ['24.0']
            },
            'kubernetes': {
                'category': 'tool',
                'aliases': ['k8s'],
                'patterns': [r'kubernetes\s*(\d+\.\d+)?'],
                'description': 'Container orchestration platform',
                'common_versions': ['1.28', '1.29']
            },
            'git': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'git\s*(\d+\.\d+)?'],
                'description': 'Version control system',
                'common_versions': ['2.40', '2.41']
            },
            'github': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'github'],
                'description': 'Git repository hosting service',
                'common_versions': []
            },
            'gitlab': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'gitlab'],
                'description': 'Git repository management platform',
                'common_versions': []
            },
            'jenkins': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'jenkins'],
                'description': 'Automation server',
                'common_versions': []
            },
            'webpack': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'webpack\s*(\d+\.\d+)?'],
                'description': 'JavaScript module bundler',
                'common_versions': ['5.88']
            },
            'babel': {
                'category': 'tool',
                'aliases': [],
                'patterns': [r'babel\s*(\d+\.\d+)?'],
                'description': 'JavaScript compiler',
                'common_versions': ['7.23']
            }
        }
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load classification patterns."""
        return {
            'version_patterns': [
                r'v?(\d+\.\d+\.\d+)',
                r'v?(\d+\.\d+)',
                r'v?(\d+)',
                r'(\d+\.\d+\.\d+)',
                r'(\d+\.\d+)',
                r'(\d+)'
            ],
            'context_patterns': {
                'programming_language': [
                    r'written\s+in\s+\w+',
                    r'built\s+with\s+\w+',
                    r'using\s+\w+',
                    r'language\s+\w+'
                ],
                'framework': [
                    r'\w+\s+framework',
                    r'based\s+on\s+\w+',
                    r'powered\s+by\s+\w+',
                    r'\w+\s+stack'
                ],
                'library': [
                    r'\w+\s+library',
                    r'import\s+\w+',
                    r'require\s+\w+',
                    r'using\s+\w+'
                ],
                'database': [
                    r'\w+\s+database',
                    r'store\s+in\s+\w+',
                    r'connect\s+to\s+\w+',
                    r'\w+\s+db'
                ],
                'platform': [
                    r'\w+\s+platform',
                    r'deploy\s+to\s+\w+',
                    r'hosted\s+on\s+\w+',
                    r'\w+\s+cloud'
                ],
                'tool': [
                    r'\w+\s+tool',
                    r'built\s+with\s+\w+',
                    r'using\s+\w+',
                    r'\w+\s+cli'
                ]
            }
        }
    
    def extract_mentions(self, text: str, source_type: str = "auto") -> List[Dict[str, Any]]:
        """
        Extract technology mentions from text.
        
        Args:
            text: Input text to analyze.
            source_type: Type of source for context-aware extraction.
            
        Returns:
            List of technology mention dictionaries.
        """
        mentions = []
        text_lower = text.lower()
        
        # Search for each technology in the database
        for tech_name, tech_info in self.tech_database.items():
            # Check main name and aliases
            search_terms = [tech_name.lower()] + [alias.lower() for alias in tech_info['aliases']]
            
            for term in search_terms:
                # Find all occurrences
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    # Extract context
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    # Extract version if present
                    version = self._extract_version(text, match.end())
                    
                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        term, tech_info, context, source_type
                    )
                    
                    if confidence >= self.config.get('min_confidence', 0.7):
                        mention = {
                            'name': tech_name,
                            'category': tech_info['category'],
                            'confidence': confidence,
                            'context': context,
                            'version': version,
                            'description': tech_info['description'],
                            'position': match.start()
                        }
                        mentions.append(mention)
        
        # Remove duplicates and sort by confidence
        unique_mentions = self._deduplicate_mentions(mentions)
        unique_mentions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return unique_mentions
    
    def _extract_version(self, text: str, position: int) -> Optional[str]:
        """Extract version number from text near position."""
        # Look ahead for version patterns
        search_text = text[position:position + 20]
        
        for pattern in self.patterns['version_patterns']:
            match = re.search(pattern, search_text)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_confidence(self, 
                            term: str, 
                            tech_info: Dict[str, Any], 
                            context: str,
                            source_type: str) -> float:
        """Calculate confidence score for technology mention."""
        confidence = 0.5  # Base confidence
        
        # Boost for exact name match
        if term == tech_info.get('name', '').lower():
            confidence += 0.2
        
        # Boost for context relevance
        context_lower = context.lower()
        category = tech_info['category']
        
        # Check category-specific context patterns
        if category in self.patterns['context_patterns']:
            for pattern in self.patterns['context_patterns'][category]:
                if re.search(pattern, context_lower):
                    confidence += 0.15
                    break
        
        # Boost for source type relevance
        if source_type == 'code' and category in ['programming_language', 'library', 'framework']:
            confidence += 0.1
        elif source_type == 'documentation' and category in ['framework', 'library', 'tool']:
            confidence += 0.1
        
        # Boost for version presence
        if re.search(r'\d+\.\d+', context):
            confidence += 0.1
        
        # Ensure confidence is within bounds
        return min(1.0, max(0.0, confidence))
    
    def _deduplicate_mentions(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate mentions of the same technology."""
        seen = set()
        unique_mentions = []
        
        for mention in mentions:
            key = (mention['name'], mention['category'])
            if key not in seen:
                seen.add(key)
                unique_mentions.append(mention)
        
        return unique_mentions
    
    def classify_technology(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Classify a technology by name.
        
        Args:
            name: Technology name to classify.
            
        Returns:
            Technology classification dictionary or None.
        """
        name_lower = name.lower()
        
        # Direct match
        if name_lower in self.tech_database:
            tech_info = self.tech_database[name_lower]
            return {
                'name': name,
                'category': tech_info['category'],
                'description': tech_info['description'],
                'common_versions': tech_info['common_versions']
            }
        
        # Alias match
        for tech_name, tech_info in self.tech_database.items():
            if name_lower in [alias.lower() for alias in tech_info['aliases']]:
                return {
                    'name': tech_name,
                    'category': tech_info['category'],
                    'description': tech_info['description'],
                    'common_versions': tech_info['common_versions']
                }
        
        # Pattern match
        for tech_name, tech_info in self.tech_database.items():
            for pattern in tech_info['patterns']:
                if re.search(pattern, name_lower):
                    return {
                        'name': tech_name,
                        'category': tech_info['category'],
                        'description': tech_info['description'],
                        'common_versions': tech_info['common_versions']
                    }
        
        return None
    
    def get_similar_technologies(self, name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get similar technologies based on category and name similarity.
        
        Args:
            name: Technology name.
            limit: Maximum number of results.
            
        Returns:
            List of similar technology dictionaries.
        """
        classification = self.classify_technology(name)
        if not classification:
            return []
        
        category = classification['category']
        similar = []
        
        for tech_name, tech_info in self.tech_database.items():
            if tech_info['category'] == category and tech_name.lower() != name.lower():
                similar.append({
                    'name': tech_name,
                    'category': tech_info['category'],
                    'description': tech_info['description']
                })
        
        return similar[:limit]