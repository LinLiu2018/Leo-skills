"""
Pattern matching utilities for Tech Extractor.
"""

import re
import ast
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """Data class for extracted dependency."""
    name: str
    category: str
    version: Optional[str] = None
    scope: Optional[str] = None
    source: str = ""
    line_number: Optional[int] = None


class PatternMatcher:
    """Pattern matching utilities for code analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Pattern Matcher.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.patterns = self._load_patterns()
        self.language_detectors = self._load_language_detectors()
    
    def _load_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load patterns for different languages and package managers."""
        return {
            'python': {
                'imports': [
                    r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
                ],
                'requirements': [
                    r'^([a-zA-Z0-9_-]+)([><=!]+[0-9\.]+)?',
                    r'^([a-zA-Z0-9_-]+)(?:\s*\[.*?\])?(?:[><=!]+[0-9\.]+)?'
                ],
                'setup_py': [
                    r'install_requires\s*=\s*\[(.*?)\]',
                    r'requires\s*=\s*\[(.*?)\]'
                ],
                'pyproject': [
                    r'"([^"]+)":\s*"[^"]*"',
                    r'\'([^\']+)\':\s*\'[^\']*\''
                ]
            },
            'javascript': {
                'imports': [
                    r'^import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'^import\s+[\'"]([^\'"]+)[\'"]',
                    r'const\s+.*?\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
                    r'require\([\'"]([^\'"]+)[\'"]\)'
                ],
                'package_json': [
                    r'"([^"]+)":\s*"[^"]*"',
                    r'"dependencies":\s*{([^}]+)}',
                    r'"devDependencies":\s*{([^}]+)}'
                ],
                'yarn_lock': [
                    r'^([a-zA-Z0-9@/_-]+)@[^:]+:',
                    r'^([a-zA-Z0-9@/_-]+)@npm:'
                ]
            },
            'typescript': {
                'imports': [
                    r'^import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'^import\s+[\'"]([^\'"]+)[\'"]',
                    r'^import\s+type\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
                ],
                'package_json': [
                    r'"([^"]+)":\s*"[^"]*"',
                    r'"dependencies":\s*{([^}]+)}',
                    r'"devDependencies":\s*{([^}]+)}'
                ]
            },
            'java': {
                'imports': [
                    r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^import\s+static\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
                ],
                'maven': [
                    r'<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?</dependency>',
                    r'<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>'
                ],
                'gradle': [
                    r'implementation\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                    r'compile\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                    r'testImplementation\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]'
                ]
            },
            'go': {
                'imports': [
                    r'^import\s+[\'"]([^\'"]+)[\'"]',
                    r'^import\s*\(\s*[\'"]([^\'"]+)[\'"]'
                ],
                'go_mod': [
                    r'^([a-zA-Z0-9_\-./]+)\s+v[0-9\.]+',
                    r'^require\s+([a-zA-Z0-9_\-./]+)\s+v[0-9\.]+'
                ]
            },
            'rust': {
                'dependencies': [
                    r'^([a-zA-Z0-9_-]+)\s*=\s*[\'"]([^\'"]+)[\'"]',
                    r'^([a-zA-Z0-9_-]+)\s*=\s*\{[^}]*version\s*=\s*[\'"]([^\'"]+)[\'"][^}]*\}'
                ],
                'use_statements': [
                    r'^use\s+([a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^extern\s+crate\s+([a-zA-Z_][a-zA-Z0-9_]*)'
                ]
            },
            'php': {
                'imports': [
                    r'^use\s+([a-zA-Z_][a-zA-Z0-9_\\\\]*(?:\\[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^require_once\s+[\'"]([^\'"]+)[\'"]',
                    r'^include_once\s+[\'"]([^\'"]+)[\'"]'
                ],
                'composer': [
                    r'"([^"]+)":\s*"[^"]*"',
                    r'"require":\s*{([^}]+)}',
                    r'"require-dev":\s*{([^}]+)}'
                ]
            },
            'ruby': {
                'requires': [
                    r'^require\s+[\'"]([^\'"]+)[\'"]',
                    r'^require_relative\s+[\'"]([^\'"]+)[\'"]'
                ],
                'gemfile': [
                    r'gem\s+[\'"]([^\'"]+)[\'"]',
                    r'gem\s+[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]'
                ]
            },
            'cpp': {
                'includes': [
                    r'^#include\s*[<"]([^>"]+)[>"]',
                    r'^#import\s*[<"]([^>"]+)[>"]'
                ],
                'cmake': [
                    r'find_package\(([^\s]+)',
                    r'target_link_libraries\([^)]+\s+([^\s)]+)',
                    r'add_dependencies\([^)]+\s+([^\s)]+)'
                ]
            },
            'csharp': {
                'usings': [
                    r'^using\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                    r'^using\s+static\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
                ],
                'project': [
                    r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"',
                    r'<Reference\s+Include="([^"]+)"'
                ]
            }
        }
    
    def _load_language_detectors(self) -> Dict[str, List[str]]:
        """Load language detection patterns."""
        return {
            'python': [
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'def\s+\w+\s*\(',
                r'class\s+\w+\s*:',
                r'if\s+__name__\s*==\s*["\']__main__["\']'
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'console\.\w+',
                r'require\s*\(',
                r'export\s+(default\s+)?\w+'
            ],
            'typescript': [
                r'interface\s+\w+',
                r'type\s+\w+\s*=',
                r'as\s+\w+',
                r':\s*\w+\[\]',
                r'<\w+>',
                r'private\s+\w+',
                r'public\s+\w+'
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'import\s+java\.',
                r'public\s+static\s+void\s+main',
                r'System\.out\.print',
                r'@\w+',
                r'implements\s+\w+'
            ],
            'go': [
                r'package\s+\w+',
                r'import\s*\(',
                r'func\s+\w+\s*\(',
                r'go\s+\w+\s*\(',
                r'make\s*\(',
                r'chan\s+\w+'
            ],
            'rust': [
                r'use\s+\w+::',
                r'fn\s+\w+\s*\(',
                r'let\s+mut\s+\w+',
                r'impl\s+\w+',
                r'Trait',
                r'match\s+\w+',
                r'->\s+\w+'
            ],
            'php': [
                r'<\?php',
                r'\$\w+',
                r'function\s+\w+\s*\(',
                r'public\s+function',
                r'echo\s+',
                r'include\s+',
                r'require\s+'
            ],
            'ruby': [
                r'require\s+[\'"]',
                r'def\s+\w+',
                r'class\s+\w+',
                r'module\s+\w+',
                r'@\w+',
                r'end\s*$'
            ],
            'cpp': [
                r'#include\s*<',
                r'using\s+namespace',
                r'int\s+main\s*\(',
                r'std::',
                r'->',
                r'::\w+'
            ],
            'csharp': [
                r'using\s+\w+;',
                r'namespace\s+\w+',
                r'public\s+class\s+\w+',
                r'public\s+void\s+\w+',
                r'@\w+',
                r'var\s+\w+\s*='
            ]
        }
    
    def extract_dependencies(self, code: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract dependencies from source code.
        
        Args:
            code: Source code string.
            language: Programming language.
            
        Returns:
            List of dependency dictionaries.
        """
        if language not in self.patterns:
            logger.warning(f"Unsupported language: {language}")
            return []
        
        dependencies = []
        patterns = self.patterns[language]
        lines = code.split('\n')
        
        # Extract based on language-specific patterns
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                try:
                    matches = self._extract_with_pattern(code, pattern, pattern_type, language)
                    dependencies.extend(matches)
                except Exception as e:
                    logger.warning(f"Pattern extraction failed for {pattern_type}: {e}")
        
        # Post-process dependencies
        processed_deps = self._post_process_dependencies(dependencies, language)
        
        return processed_deps
    
    def _extract_with_pattern(self, 
                            code: str, 
                            pattern: str, 
                            pattern_type: str, 
                            language: str) -> List[Dict[str, Any]]:
        """Extract dependencies using a specific pattern."""
        dependencies = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//') or line.startswith('/*'):
                continue
            
            match = re.search(pattern, line, re.MULTILINE | re.DOTALL)
            if match:
                dep = self._create_dependency_from_match(
                    match, pattern_type, language, line, line_num
                )
                if dep:
                    dependencies.append(dep)
        
        return dependencies
    
    def _create_dependency_from_match(self, 
                                    match, 
                                    pattern_type: str, 
                                    language: str, 
                                    line: str, 
                                    line_num: int) -> Optional[Dict[str, Any]]:
        """Create dependency dictionary from regex match."""
        try:
            if language == 'python':
                return self._create_python_dependency(match, pattern_type, line, line_num)
            elif language in ['javascript', 'typescript']:
                return self._create_js_dependency(match, pattern_type, line, line_num)
            elif language == 'java':
                return self._create_java_dependency(match, pattern_type, line, line_num)
            elif language == 'go':
                return self._create_go_dependency(match, pattern_type, line, line_num)
            elif language == 'rust':
                return self._create_rust_dependency(match, pattern_type, line, line_num)
            elif language == 'php':
                return self._create_php_dependency(match, pattern_type, line, line_num)
            elif language == 'ruby':
                return self._create_ruby_dependency(match, pattern_type, line, line_num)
            elif language == 'cpp':
                return self._create_cpp_dependency(match, pattern_type, line, line_num)
            elif language == 'csharp':
                return self._create_csharp_dependency(match, pattern_type, line, line_num)
        except Exception as e:
            logger.warning(f"Failed to create dependency from match: {e}")
        
        return None
    
    def _create_python_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create Python dependency from match."""
        if pattern_type == 'imports':
            name = match.group(1).split('.')[0]
            return {
                'name': name,
                'category': 'library',
                'source': 'import',
                'line_number': line_num,
                'full_match': match.group(0)
            }
        elif pattern_type == 'requirements':
            name = match.group(1)
            version = match.group(2) if len(match.groups()) > 1 else None
            return {
                'name': name,
                'category': 'library',
                'version': version,
                'source': 'requirements',
                'line_number': line_num
            }
        else:
            name = match.group(1)
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _create_js_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create JavaScript/TypeScript dependency from match."""
        if pattern_type == 'imports':
            name = match.group(1)
            # Handle scoped packages
            if name.startswith('@'):
                parts = name.split('/')
                name = parts[0] + '/' + parts[1] if len(parts) > 1 else parts[0]
            else:
                name = name.split('/')[0]
            
            return {
                'name': name,
                'category': 'library',
                'source': 'import',
                'line_number': line_num,
                'full_match': match.group(0)
            }
        else:
            name = match.group(1)
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _create_java_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create Java dependency from match."""
        if pattern_type == 'imports':
            full_name = match.group(1)
            name = full_name.split('.')[-1]
            return {
                'name': name,
                'category': 'library',
                'source': 'import',
                'line_number': line_num,
                'full_match': full_name
            }
        elif pattern_type == 'maven':
            group_id = match.group(1)
            artifact_id = match.group(2)
            name = f"{group_id}:{artifact_id}"
            return {
                'name': name,
                'category': 'library',
                'source': 'maven',
                'line_number': line_num,
                'group_id': group_id,
                'artifact_id': artifact_id
            }
        elif pattern_type == 'gradle':
            group = match.group(1)
            artifact = match.group(2)
            version = match.group(3)
            name = f"{group}:{artifact}"
            return {
                'name': name,
                'category': 'library',
                'version': version,
                'source': 'gradle',
                'line_number': line_num,
                'group_id': group,
                'artifact_id': artifact
            }
        else:
            name = match.group(1)
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _create_go_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create Go dependency from match."""
        name = match.group(1)
        # Extract package name from full path
        parts = name.split('/')
        package_name = parts[-1] if parts else name
        
        return {
            'name': package_name,
            'category': 'library',
            'source': pattern_type,
            'line_number': line_num,
            'full_path': name
        }
    
    def _create_rust_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create Rust dependency from match."""
        if pattern_type == 'dependencies':
            name = match.group(1)
            version = match.group(2) if len(match.groups()) > 1 else None
            return {
                'name': name,
                'category': 'library',
                'version': version,
                'source': 'cargo',
                'line_number': line_num
            }
        else:
            name = match.group(1).split('::')[-1]
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _create_php_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create PHP dependency from match."""
        if pattern_type == 'imports':
            full_name = match.group(1)
            name = full_name.split('\\')[-1]
            return {
                'name': name,
                'category': 'library',
                'source': 'use',
                'line_number': line_num,
                'full_match': full_name
            }
        else:
            name = match.group(1)
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _create_ruby_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create Ruby dependency from match."""
        name = match.group(1)
        version = match.group(2) if len(match.groups()) > 1 else None
        
        return {
            'name': name,
            'category': 'library',
            'version': version,
            'source': pattern_type,
            'line_number': line_num
        }
    
    def _create_cpp_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create C++ dependency from match."""
        name = match.group(1)
        
        # Remove .h, .hpp, etc. extensions
        if name.endswith(('.h', '.hpp', '.hxx')):
            name = name[:-2] if name.endswith('.h') else name[:-4]
        
        return {
            'name': name,
            'category': 'library',
            'source': pattern_type,
            'line_number': line_num
        }
    
    def _create_csharp_dependency(self, match, pattern_type: str, line: str, line_num: int) -> Dict[str, Any]:
        """Create C# dependency from match."""
        if pattern_type == 'usings':
            full_name = match.group(1)
            name = full_name.split('.')[-1]
            return {
                'name': name,
                'category': 'library',
                'source': 'using',
                'line_number': line_num,
                'full_match': full_name
            }
        elif pattern_type == 'project':
            name = match.group(1)
            version = match.group(2) if len(match.groups()) > 1 else None
            return {
                'name': name,
                'category': 'library',
                'version': version,
                'source': 'nuget',
                'line_number': line_num
            }
        else:
            name = match.group(1)
            return {
                'name': name,
                'category': 'library',
                'source': pattern_type,
                'line_number': line_num
            }
    
    def _post_process_dependencies(self, dependencies: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Post-process dependencies to remove duplicates and categorize."""
        # Remove duplicates
        seen = set()
        unique_deps = []
        
        for dep in dependencies:
            key = (dep['name'], dep['category'])
            if key not in seen:
                seen.add(key)
                unique_deps.append(dep)
        
        # Categorize dependencies
        for dep in unique_deps:
            dep['category'] = self._categorize_dependency(dep['name'], language)
        
        return unique_deps
    
    def _categorize_dependency(self, name: str, language: str) -> str:
        """Categorize dependency by name and language."""
        # Standard library categories
        std_libs = {
            'python': ['os', 'sys', 'json', 're', 'datetime', 'collections', 'itertools', 'functools'],
            'javascript': ['fs', 'path', 'http', 'https', 'url', 'util', 'events'],
            'java': ['java.lang', 'java.util', 'java.io', 'java.net', 'java.math'],
            'cpp': ['iostream', 'vector', 'string', 'algorithm', 'memory', 'functional']
        }
        
        if language in std_libs and name in std_libs[language]:
            return 'standard_library'
        
        # Framework detection
        frameworks = {
            'python': ['django', 'flask', 'fastapi', 'requests', 'numpy', 'pandas'],
            'javascript': ['react', 'vue', 'angular', 'express', 'lodash', 'axios'],
            'java': ['spring', 'hibernate', 'junit', 'mockito'],
            'cpp': ['boost', 'qt', 'opencv']
        }
        
        if language in frameworks and name in frameworks[language]:
            return 'framework'
        
        # Default to library
        return 'library'
    
    def detect_language_from_code(self, code: str) -> str:
        """
        Detect programming language from code content.
        
        Args:
            code: Source code string.
            
        Returns:
            Detected programming language.
        """
        scores = {}
        
        for language, patterns in self.language_detectors.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, code, re.MULTILINE | re.IGNORECASE)
                score += len(matches)
            scores[language] = score
        
        if max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)
    
    def extract_file_patterns(self, file_path: str) -> Dict[str, Any]:
        """
        Extract patterns from file path and name.
        
        Args:
            file_path: File path string.
            
        Returns:
            Dictionary with extracted patterns.
        """
        patterns = {
            'file_name': '',
            'extension': '',
            'directory': '',
            'is_config': False,
            'is_test': False,
            'is_doc': False,
            'file_type': 'unknown'
        }
        
        # Extract file name and extension
        import os
        patterns['file_name'] = os.path.basename(file_path)
        patterns['extension'] = os.path.splitext(file_path)[1].lower()
        patterns['directory'] = os.path.dirname(file_path)
        
        # Detect file types
        config_patterns = [
            r'package\.json', r'pom\.xml', r'build\.gradle', r'cargo\.toml',
            r'composer\.json', r'gemfile', r'cmakelists\.txt', r'\.csproj$'
        ]
        
        test_patterns = [
            r'test_', r'_test\.', r'spec_', r'_spec\.', r'\.test\.',
            r'tests?/', r'/tests?/'
        ]
        
        doc_patterns = [
            r'readme', r'changes?', r'license', r'contributing',
            r'doc/', r'docs/', r'md$', r'txt$'
        ]
        
        file_name_lower = patterns['file_name'].lower()
        file_path_lower = file_path.lower()
        
        patterns['is_config'] = any(re.search(pattern, file_name_lower) for pattern in config_patterns)
        patterns['is_test'] = any(re.search(pattern, file_path_lower) for pattern in test_patterns)
        patterns['is_doc'] = any(re.search(pattern, file_path_lower) for pattern in doc_patterns)
        
        # Determine file type
        if patterns['is_config']:
            patterns['file_type'] = 'config'
        elif patterns['is_test']:
            patterns['file_type'] = 'test'
        elif patterns['is_doc']:
            patterns['file_type'] = 'documentation'
        elif patterns['extension'] in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
            patterns['file_type'] = 'source'
        else:
            patterns['file_type'] = 'other'
        
        return patterns