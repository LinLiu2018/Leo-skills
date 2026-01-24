#!/usr/bin/env python3
"""
Skill Code Generator - Automated Skill Generation Tool

A comprehensive system for generating Leo AI skills with:
- Template-based skill generation
- Custom skill scaffolding
- Code pattern implementation
- Configuration file generation
- Documentation generation
- Testing framework setup

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import logging
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.template_manager import TemplateManager
from utils.skill_analyzer import SkillAnalyzer
from utils.code_generator import CodeGenerator
from utils.config_builder import ConfigBuilder
from utils.doc_generator import DocumentationGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SkillSpec:
    """Data class representing a skill specification."""
    name: str
    description: str
    category: str
    author: str = "Claude Code"
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)
    testing_framework: str = "pytest"
    documentation_level: str = "basic"

    def to_dict(self) -> Dict[str, Any]:
        """Convert SkillSpec to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'author': self.author,
            'version': self.version,
            'dependencies': self.dependencies,
            'features': self.features,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'configuration': self.configuration,
            'templates': self.templates,
            'testing_framework': self.testing_framework,
            'documentation_level': self.documentation_level
        }


@dataclass
class GeneratedSkill:
    """Data class representing a generated skill."""
    spec: SkillSpec
    files: Dict[str, str]
    structure: Dict[str, Any]
    tests: List[str]
    documentation: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert GeneratedSkill to dictionary."""
        return {
            'spec': self.spec.to_dict(),
            'files': self.files,
            'structure': self.structure,
            'tests': self.tests,
            'documentation': self.documentation,
            'metadata': self.metadata
        }


class SkillCodeGenerator:
    """
    Main Skill Code Generator class for automated skill creation.

    This class provides a unified interface for:
    - Skill specification analysis
    - Template-based code generation
    - Configuration management
    - Documentation generation
    - Testing setup
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Skill Code Generator.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.template_manager = TemplateManager(config=self.config)
        self.skill_analyzer = SkillAnalyzer(config=self.config)
        self.code_generator = CodeGenerator(config=self.config)
        self.config_builder = ConfigBuilder(config=self.config)
        self.doc_generator = DocumentationGenerator(config=self.config)

        logger.info("Skill Code Generator initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'templates_dir': 'templates',
            'output_dir': 'output',
            'default_author': 'Claude Code',
            'default_version': '1.0.0',
            'supported_categories': [
                'utilities', 'content-creation', 'development', 'data-analysis',
                'monitoring', 'integration', 'automation', 'research'
            ],
            'default_dependencies': {
                'python': ['requests', 'pyyaml', 'jinja2'],
                'javascript': ['axios', 'lodash'],
                'typescript': ['axios', '@types/node']
            },
            'code_style': 'pep8',
            'include_tests': True,
            'include_docs': True,
            'include_examples': True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config

    def generate_from_spec(self, spec: SkillSpec, output_path: Optional[str] = None) -> GeneratedSkill:
        """
        Generate a skill from specification.

        Args:
            spec: Skill specification object.
            output_path: Optional output directory path.

        Returns:
            GeneratedSkill object.
        """
        logger.info(f"Generating skill: {spec.name}")

        # Validate specification
        validation_errors = self._validate_spec(spec)
        if validation_errors:
            raise ValueError(f"Invalid specification: {', '.join(validation_errors)}")

        # Determine output path
        if not output_path:
            output_path = os.path.join(self.config['output_dir'], f"{spec.name}-cskill")

        # Analyze skill requirements
        analysis = self.skill_analyzer.analyze_requirements(spec)

        # Generate code structure
        structure = self._generate_structure(spec, analysis)

        # Generate files
        files = self._generate_files(spec, structure)

        # Generate tests
        tests = self._generate_tests(spec, structure)

        # Generate documentation
        documentation = self._generate_documentation(spec, structure)

        # Create metadata
        metadata = self._generate_metadata(spec, analysis)

        # Write files to disk
        self._write_skill_files(files, output_path)

        generated_skill = GeneratedSkill(
            spec=spec,
            files=files,
            structure=structure,
            tests=tests,
            documentation=documentation,
            metadata=metadata
        )

        logger.info(f"Skill generated successfully at: {output_path}")
        return generated_skill

    def generate_from_prompt(self, 
                           prompt: str, 
                           category: Optional[str] = None,
                           output_path: Optional[str] = None) -> GeneratedSkill:
        """
        Generate a skill from natural language prompt.

        Args:
            prompt: Natural language description of the skill.
            category: Optional category override.
            output_path: Optional output directory path.

        Returns:
            GeneratedSkill object.
        """
        logger.info(f"Generating skill from prompt: {prompt[:100]}...")

        # Parse prompt into specification
        spec = self.skill_analyzer.parse_prompt_to_spec(prompt, category)
        
        return self.generate_from_spec(spec, output_path)

    def generate_from_template(self, 
                            template_name: str, 
                            parameters: Dict[str, Any],
                            output_path: Optional[str] = None) -> GeneratedSkill:
        """
        Generate a skill from a predefined template.

        Args:
            template_name: Name of the template to use.
            parameters: Template parameters.
            output_path: Optional output directory path.

        Returns:
            GeneratedSkill object.
        """
        logger.info(f"Generating skill from template: {template_name}")

        # Load template
        template_spec = self.template_manager.load_template(template_name)
        
        # Merge parameters with template
        spec_dict = template_spec.copy()
        spec_dict.update(parameters)
        
        # Create SkillSpec object
        spec = SkillSpec(**spec_dict)
        
        return self.generate_from_spec(spec, output_path)

    def generate_skill_variation(self, 
                               base_spec: SkillSpec, 
                               variation_type: str,
                               variation_params: Dict[str, Any]) -> GeneratedSkill:
        """
        Generate a variation of an existing skill.

        Args:
            base_spec: Base skill specification.
            variation_type: Type of variation ('extended', 'simplified', 'optimized').
            variation_params: Parameters for the variation.

        Returns:
            GeneratedSkill object.
        """
        logger.info(f"Generating {variation_type} variation of {base_spec.name}")

        # Create variation spec
        if variation_type == 'extended':
            spec = self._create_extended_variation(base_spec, variation_params)
        elif variation_type == 'simplified':
            spec = self._create_simplified_variation(base_spec, variation_params)
        elif variation_type == 'optimized':
            spec = self._create_optimized_variation(base_spec, variation_params)
        else:
            raise ValueError(f"Unsupported variation type: {variation_type}")

        return self.generate_from_spec(spec)

    def _validate_spec(self, spec: SkillSpec) -> List[str]:
        """Validate skill specification."""
        errors = []
        
        if not spec.name or not spec.name.strip():
            errors.append("Skill name is required")
        
        if not spec.description or not spec.description.strip():
            errors.append("Skill description is required")
        
        if not spec.category or spec.category not in self.config['supported_categories']:
            errors.append(f"Invalid category. Must be one of: {', '.join(self.config['supported_categories'])}")
        
        if not re.match(r'^[a-z0-9-]+$', spec.name):
            errors.append("Skill name must contain only lowercase letters, numbers, and hyphens")
        
        return errors

    def _generate_structure(self, spec: SkillSpec, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate skill directory structure."""
        structure = {
            'name': spec.name,
            'type': 'cskill',
            'version': spec.version,
            'directories': [
                'scripts',
                'scripts/utils',
                'config',
                'docs',
                'tests',
                'examples'
            ],
            'main_files': [
                'scripts/main.py',
                'scripts/__init__.py',
                'config.yaml',
                'README.md'
            ],
            'utility_files': [],
            'test_files': [],
            'doc_files': []
        }

        # Add utility files based on complexity
        if analysis['complexity'] > 0.5:
            structure['utility_files'].extend([
                'scripts/utils/data_processor.py',
                'scripts/utils/api_client.py',
                'scripts/utils/validator.py'
            ])

        # Add test files
        if self.config['include_tests']:
            structure['test_files'].extend([
                'tests/test_main.py',
                'tests/test_utils.py',
                'tests/conftest.py'
            ])

        # Add documentation files
        if self.config['include_docs']:
            structure['doc_files'].extend([
                'docs/api.md',
                'docs/usage.md',
                'docs/configuration.md'
            ])

        return structure

    def _generate_files(self, spec: SkillSpec, structure: Dict[str, Any]) -> Dict[str, str]:
        """Generate all skill files."""
        files = {}

        # Main script
        files['scripts/main.py'] = self.code_generator.generate_main_script(spec)
        files['scripts/__init__.py'] = self.code_generator.generate_init_file(spec)

        # Utility files
        for util_file in structure['utility_files']:
            files[util_file] = self.code_generator.generate_utility_file(util_file, spec)

        # Configuration
        files['config.yaml'] = self.config_builder.build_config(spec)

        # README
        files['README.md'] = self.doc_generator.generate_readme(spec)

        # Examples
        if self.config['include_examples']:
            files['examples/basic_usage.py'] = self.code_generator.generate_example(spec)

        return files

    def _generate_tests(self, spec: SkillSpec, structure: Dict[str, Any]) -> List[str]:
        """Generate test files."""
        tests = []

        if self.config['include_tests']:
            # Main test file
            main_test = self.code_generator.generate_main_test(spec)
            tests.append(('tests/test_main.py', main_test))

            # Utility tests
            for util_file in structure['utility_files']:
                util_test = self.code_generator.generate_utility_test(util_file, spec)
                tests.append((f'tests/test_{Path(util_file).stem}.py', util_test))

            # Configuration file
            conftest = self.code_generator.generate_conftest()
            tests.append(('tests/conftest.py', conftest))

        return tests

    def _generate_documentation(self, spec: SkillSpec, structure: Dict[str, Any]) -> List[str]:
        """Generate documentation files."""
        docs = []

        if self.config['include_docs']:
            # API documentation
            api_doc = self.doc_generator.generate_api_doc(spec)
            docs.append(('docs/api.md', api_doc))

            # Usage guide
            usage_doc = self.doc_generator.generate_usage_guide(spec)
            docs.append(('docs/usage.md', usage_doc))

            # Configuration guide
            config_doc = self.doc_generator.generate_config_guide(spec)
            docs.append(('docs/configuration.md', config_doc))

        return docs

    def _generate_metadata(self, spec: SkillSpec, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate skill metadata."""
        return {
            'generated_at': datetime.now().isoformat(),
            'generator_version': self.config.get('generator_version', '1.0.0'),
            'complexity_score': analysis.get('complexity', 0),
            'estimated_development_time': analysis.get('dev_time', '1-2 hours'),
            'skill_dependencies': spec.dependencies,
            'external_apis': analysis.get('external_apis', []),
            'data_requirements': analysis.get('data_requirements', []),
            'performance_considerations': analysis.get('performance', {}),
            'security_considerations': analysis.get('security', [])
        }

    def _write_skill_files(self, files: Dict[str, str], output_path: str):
        """Write generated files to disk."""
        # Create output directory
        os.makedirs(output_path, exist_ok=True)

        # Write each file
        for file_path, content in files.items():
            full_path = os.path.join(output_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"Written: {full_path}")

    def _create_extended_variation(self, base_spec: SkillSpec, params: Dict[str, Any]) -> SkillSpec:
        """Create an extended version of a skill."""
        new_features = params.get('features', [])
        new_deps = params.get('dependencies', [])
        
        return SkillSpec(
            name=f"{base_spec.name}-extended",
            description=f"{base_spec.description} (Extended Version)",
            category=base_spec.category,
            author=base_spec.author,
            version=base_spec.version,
            dependencies=base_spec.dependencies + new_deps,
            features=base_spec.features + new_features,
            inputs=base_spec.inputs,
            outputs=base_spec.outputs,
            configuration=base_spec.configuration,
            templates=base_spec.templates,
            testing_framework=base_spec.testing_framework,
            documentation_level=base_spec.documentation_level
        )

    def _create_simplified_variation(self, base_spec: SkillSpec, params: Dict[str, Any]) -> SkillSpec:
        """Create a simplified version of a skill."""
        return SkillSpec(
            name=f"{base_spec.name}-simple",
            description=f"{base_spec.description} (Simplified Version)",
            category=base_spec.category,
            author=base_spec.author,
            version=base_spec.version,
            dependencies=[],  # Remove dependencies for simplicity
            features=base_spec.features[:2],  # Keep only first 2 features
            inputs=base_spec.inputs[:2],  # Limit inputs
            outputs=base_spec.outputs[:1],  # Limit outputs
            configuration={},
            templates=base_spec.templates,
            testing_framework=base_spec.testing_framework,
            documentation_level="minimal"
        )

    def _create_optimized_variation(self, base_spec: SkillSpec, params: Dict[str, Any]) -> SkillSpec:
        """Create an optimized version of a skill."""
        optimizations = params.get('optimizations', ['caching', 'async', 'error_handling'])
        
        return SkillSpec(
            name=f"{base_spec.name}-optimized",
            description=f"{base_spec.description} (Optimized Version)",
            category=base_spec.category,
            author=base_spec.author,
            version=f"{base_spec.version}-opt",
            dependencies=base_spec.dependencies + ['asyncio', 'functools'],
            features=base_spec.features + [f"Optimized with {opt}" for opt in optimizations],
            inputs=base_spec.inputs,
            outputs=base_spec.outputs,
            configuration={**base_spec.configuration, 'optimizations': optimizations},
            templates=base_spec.templates,
            testing_framework=base_spec.testing_framework,
            documentation_level=base_spec.documentation_level
        )

    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List available skill templates."""
        return self.template_manager.list_templates()

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template."""
        return self.template_manager.get_template_info(template_name)

    def validate_generated_skill(self, skill_path: str) -> Dict[str, Any]:
        """Validate a generated skill."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # Check file structure
        required_files = ['scripts/main.py', 'config.yaml', 'README.md']
        for file_path in required_files:
            full_path = os.path.join(skill_path, file_path)
            if not os.path.exists(full_path):
                validation_results['errors'].append(f"Missing required file: {file_path}")

        # Check Python syntax
        main_script = os.path.join(skill_path, 'scripts/main.py')
        if os.path.exists(main_script):
            try:
                with open(main_script, 'r') as f:
                    compile(f.read(), main_script, 'exec')
            except SyntaxError as e:
                validation_results['errors'].append(f"Syntax error in main.py: {e}")

        # Check dependencies
        config_file = os.path.join(skill_path, 'config.yaml')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    import yaml
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                validation_results['errors'].append(f"Invalid YAML in config.yaml: {e}")

        validation_results['valid'] = len(validation_results['errors']) == 0
        return validation_results


def main():
    """Main entry point for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Skill Code Generator CLI")
    parser.add_argument(
        "command",
        choices=["generate", "list-templates", "validate"],
        help="Command to execute"
    )
    parser.add_argument("--prompt", help="Natural language prompt for skill generation")
    parser.add_argument("--template", help="Template name to use")
    parser.add_argument("--spec", help="Path to skill specification file")
    parser.add_argument("--category", help="Skill category")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--name", help="Skill name")
    parser.add_argument("--description", help="Skill description")

    args = parser.parse_args()

    generator = SkillCodeGenerator()

    if args.command == "generate":
        if args.prompt:
            # Generate from prompt
            skill = generator.generate_from_prompt(
                args.prompt, 
                args.category, 
                args.output
            )
            print(f"Generated skill: {skill.spec.name}")
        elif args.template:
            # Generate from template
            params = {}
            if args.name:
                params['name'] = args.name
            if args.description:
                params['description'] = args.description
            
            skill = generator.generate_from_template(
                args.template, 
                params, 
                args.output
            )
            print(f"Generated skill from template: {skill.spec.name}")
        elif args.spec:
            # Generate from specification file
            with open(args.spec, 'r') as f:
                spec_data = json.load(f)
            
            spec = SkillSpec(**spec_data)
            skill = generator.generate_from_spec(spec, args.output)
            print(f"Generated skill from spec: {skill.spec.name}")
        else:
            print("Error: Must provide --prompt, --template, or --spec")
            return 1

    elif args.command == "list-templates":
        templates = generator.list_available_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template['name']}: {template['description']}")

    elif args.command == "validate":
        if not args.output:
            print("Error: --output is required for validation")
            return 1
        
        results = generator.validate_generated_skill(args.output)
        if results['valid']:
            print("[SUCCESS] Skill is valid")
        else:
            print("[ERROR] Skill has errors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        if results['warnings']:
            print("[WARNING]  Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")

    return 0


if __name__ == "__main__":
    exit(main())