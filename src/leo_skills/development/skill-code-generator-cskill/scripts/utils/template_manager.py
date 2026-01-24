"""
Template manager for Skill Code Generator.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Template:
    """Data class for skill templates."""
    name: str
    description: str
    category: str
    complexity: str
    dependencies: List[str]
    features: List[str]
    configuration: Dict[str, Any]
    parameters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert Template to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'complexity': self.complexity,
            'dependencies': self.dependencies,
            'features': self.features,
            'configuration': self.configuration,
            'parameters': self.parameters
        }


class TemplateManager:
    """Template management utilities for skill generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Template Manager.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.templates_dir = config.get('templates_dir', 'templates')
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load all available templates."""
        templates = {}
        
        # Built-in templates
        builtin_templates = self._get_builtin_templates()
        for name, template_data in builtin_templates.items():
            templates[name] = Template(**template_data)
        
        # Load external templates if directory exists
        if os.path.exists(self.templates_dir):
            for file_name in os.listdir(self.templates_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.templates_dir, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                        
                        template = Template(**template_data)
                        templates[template.name] = template
                    except Exception as e:
                        logger.warning(f"Failed to load template {file_name}: {e}")
        
        return templates
    
    def _get_builtin_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in skill templates."""
        return {
            'web-scraper': {
                'name': 'web-scraper',
                'description': 'A web scraping skill for extracting data from websites',
                'category': 'utilities',
                'complexity': 'medium',
                'dependencies': ['requests', 'beautifulsoup4', 'lxml'],
                'features': [
                    'HTTP request handling',
                    'HTML parsing',
                    'Data extraction',
                    'Error handling',
                    'Rate limiting'
                ],
                'configuration': {
                    'max_requests_per_minute': 60,
                    'timeout': 30,
                    'user_agent': 'Mozilla/5.0',
                    'retry_attempts': 3
                },
                'parameters': {
                    'target_urls': ['list', 'List of URLs to scrape'],
                    'selectors': ['dict', 'CSS selectors for data extraction'],
                    'output_format': ['string', 'Output format (json, csv, xml)']
                }
            },
            'api-connector': {
                'name': 'api-connector',
                'description': 'A generic API connector for integrating with external services',
                'category': 'integration',
                'complexity': 'low',
                'dependencies': ['requests', 'pyyaml', 'python-dotenv'],
                'features': [
                    'REST API integration',
                    'Authentication handling',
                    'Request/response validation',
                    'Error handling',
                    'Rate limiting'
                ],
                'configuration': {
                    'base_url': '',
                    'auth_type': 'none',
                    'timeout': 30,
                    'retry_attempts': 3
                },
                'parameters': {
                    'api_endpoints': ['list', 'List of API endpoints'],
                    'auth_config': ['dict', 'Authentication configuration'],
                    'headers': ['dict', 'Default HTTP headers']
                }
            },
            'data-processor': {
                'name': 'data-processor',
                'description': 'A data processing skill for transforming and analyzing data',
                'category': 'data-analysis',
                'complexity': 'medium',
                'dependencies': ['pandas', 'numpy', 'openpyxl'],
                'features': [
                    'CSV/Excel file processing',
                    'Data transformation',
                    'Statistical analysis',
                    'Data validation',
                    'Report generation'
                ],
                'configuration': {
                    'chunk_size': 1000,
                    'max_memory_usage': '1GB',
                    'output_format': 'json'
                },
                'parameters': {
                    'input_files': ['list', 'List of input files'],
                    'transformations': ['list', 'Data transformation rules'],
                    'output_path': ['string', 'Output file path']
                }
            },
            'notification-sender': {
                'name': 'notification-sender',
                'description': 'A notification sender for various communication channels',
                'category': 'automation',
                'complexity': 'low',
                'dependencies': ['requests', 'smtplib', 'jinja2'],
                'features': [
                    'Email notifications',
                    'Slack integration',
                    'Webhook support',
                    'Template rendering',
                    'Batch sending'
                ],
                'configuration': {
                    'smtp_server': '',
                    'smtp_port': 587,
                    'default_from': '',
                    'timeout': 30
                },
                'parameters': {
                    'recipients': ['list', 'List of recipients'],
                    'message_template': ['string', 'Message template'],
                    'channels': ['list', 'Notification channels']
                }
            },
            'file-monitor': {
                'name': 'file-monitor',
                'description': 'A file system monitor for tracking changes and events',
                'category': 'monitoring',
                'complexity': 'medium',
                'dependencies': ['watchdog', 'pathlib', 'schedule'],
                'features': [
                    'File system watching',
                    'Pattern matching',
                    'Event filtering',
                    'Automated actions',
                    'Logging'
                ],
                'configuration': {
                    'watch_recursive': True,
                    'ignore_patterns': ['*.tmp', '*.log'],
                    'event_handlers': []
                },
                'parameters': {
                    'watch_paths': ['list', 'Paths to monitor'],
                    'event_types': ['list', 'Types of events to watch'],
                    'actions': ['dict', 'Actions for different events']
                }
            },
            'text-analyzer': {
                'name': 'text-analyzer',
                'description': 'A text analysis skill for natural language processing',
                'category': 'content-creation',
                'complexity': 'high',
                'dependencies': ['nltk', 'textblob', 'scikit-learn'],
                'features': [
                    'Sentiment analysis',
                    'Keyword extraction',
                    'Text classification',
                    'Language detection',
                    'Summarization'
                ],
                'configuration': {
                    'language': 'english',
                    'model_path': '',
                    'cache_enabled': True
                },
                'parameters': {
                    'input_text': ['string', 'Text to analyze'],
                    'analysis_types': ['list', 'Types of analysis to perform'],
                    'output_format': ['string', 'Output format']
                }
            },
            'task-scheduler': {
                'name': 'task-scheduler',
                'description': 'A task scheduler for automating recurring tasks',
                'category': 'automation',
                'complexity': 'medium',
                'dependencies': ['schedule', 'apscheduler', 'croniter'],
                'features': [
                    'Cron scheduling',
                    'Task management',
                    'Concurrent execution',
                    'Failure handling',
                    'Logging and monitoring'
                ],
                'configuration': {
                    'max_concurrent_tasks': 5,
                    'default_timezone': 'UTC',
                    'retry_policy': 'exponential'
                },
                'parameters': {
                    'tasks': ['list', 'List of tasks to schedule'],
                    'schedules': ['dict', 'Schedule configurations'],
                    'handlers': ['dict', 'Task handlers']
                }
            },
            'database-connector': {
                'name': 'database-connector',
                'description': 'A database connector for various database systems',
                'category': 'integration',
                'complexity': 'high',
                'dependencies': ['sqlalchemy', 'psycopg2', 'pymongo'],
                'features': [
                    'Multiple database support',
                    'Connection pooling',
                    'Query execution',
                    'Transaction management',
                    'Migration support'
                ],
                'configuration': {
                    'pool_size': 5,
                    'max_overflow': 10,
                    'pool_timeout': 30
                },
                'parameters': {
                    'database_url': ['string', 'Database connection URL'],
                    'queries': ['dict', 'SQL queries or operations'],
                    'connection_config': ['dict', 'Connection configuration']
                }
            }
        }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            List of template information dictionaries.
        """
        return [template.to_dict() for template in self.templates.values()]
    
    def get_template(self, template_name: str) -> Optional[Template]:
        """
        Get a specific template by name.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Template object or None if not found.
        """
        return self.templates.get(template_name)
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load template specification for skill generation.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Template specification dictionary.
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        return {
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'author': self.config.get('default_author', 'Claude Code'),
            'version': self.config.get('default_version', '1.0.0'),
            'dependencies': template.dependencies,
            'features': template.features,
            'configuration': template.configuration,
            'inputs': self._generate_inputs_from_parameters(template.parameters),
            'outputs': [
                {'name': 'result', 'type': 'dict', 'description': 'Processing result'},
                {'name': 'status', 'type': 'string', 'description': 'Operation status'}
            ]
        }
    
    def _generate_inputs_from_parameters(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate input specifications from template parameters."""
        inputs = []
        for param_name, param_info in parameters.items():
            inputs.append({
                'name': param_name,
                'type': param_info[0],
                'description': param_info[1],
                'required': True
            })
        return inputs
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a template.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Template information dictionary.
        """
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'complexity': template.complexity,
            'dependencies': template.dependencies,
            'features': template.features,
            'parameters': template.parameters,
            'configuration': template.configuration,
            'estimated_development_time': self._estimate_dev_time(template.complexity),
            'difficulty_level': self._map_complexity_to_difficulty(template.complexity)
        }
    
    def _estimate_dev_time(self, complexity: str) -> str:
        """Estimate development time based on complexity."""
        time_map = {
            'low': '1-2 hours',
            'medium': '3-6 hours',
            'high': '1-2 days'
        }
        return time_map.get(complexity, '2-4 hours')
    
    def _map_complexity_to_difficulty(self, complexity: str) -> str:
        """Map complexity to difficulty level."""
        difficulty_map = {
            'low': 'Beginner',
            'medium': 'Intermediate',
            'high': 'Advanced'
        }
        return difficulty_map.get(complexity, 'Intermediate')
    
    def create_custom_template(self, 
                            name: str,
                            description: str,
                            category: str,
                            complexity: str,
                            dependencies: List[str],
                            features: List[str],
                            configuration: Dict[str, Any],
                            parameters: Dict[str, Any]) -> Template:
        """
        Create a custom template.
        
        Args:
            name: Template name.
            description: Template description.
            category: Template category.
            complexity: Template complexity level.
            dependencies: List of dependencies.
            features: List of features.
            configuration: Configuration dictionary.
            parameters: Parameters dictionary.
            
        Returns:
            Created Template object.
        """
        template = Template(
            name=name,
            description=description,
            category=category,
            complexity=complexity,
            dependencies=dependencies,
            features=features,
            configuration=configuration,
            parameters=parameters
        )
        
        self.templates[name] = template
        return template
    
    def save_template(self, template: Template, file_path: str):
        """
        Save a template to file.
        
        Args:
            template: Template object to save.
            file_path: Path to save the template.
        """
        template_data = template.to_dict()
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Template saved to: {file_path}")
    
    def filter_templates(self, 
                       category: Optional[str] = None,
                       complexity: Optional[str] = None,
                       features: Optional[List[str]] = None) -> List[Template]:
        """
        Filter templates based on criteria.
        
        Args:
            category: Optional category filter.
            complexity: Optional complexity filter.
            features: Optional required features filter.
            
        Returns:
            List of filtered Template objects.
        """
        filtered = list(self.templates.values())
        
        if category:
            filtered = [t for t in filtered if t.category == category]
        
        if complexity:
            filtered = [t for t in filtered if t.complexity == complexity]
        
        if features:
            filtered = [t for t in filtered if all(f in t.features for f in features)]
        
        return filtered