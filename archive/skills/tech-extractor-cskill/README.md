# Tech Extractor Skill

## Overview

The Tech Extractor Skill is a comprehensive technical information extraction system designed to:

- Extract technologies from text, documentation, and source code
- Analyze technology trends across multiple sources
- Classify and categorize technologies
- Identify technology stacks from repositories
- Generate trend predictions and market impact assessments

## Features

### Core Capabilities

1. **Text Analysis**
   - Extract technology mentions from articles, documentation, and news
   - Classify source types (documentation, code, articles, news)
   - Multi-language support (English, Chinese, Japanese, Korean)

2. **Code Analysis**
   - Extract dependencies from source code
   - Support for 10+ programming languages
   - Identify imports, packages, and framework usage
   - Package file parsing (package.json, requirements.txt, etc.)

3. **Trend Analysis**
   - Multi-source trend data (GitHub, Stack Overflow, Reddit, News)
   - Growth rate calculation and trend classification
   - Sentiment analysis
   - Market impact assessment
   - Future trend predictions

4. **Repository Analysis**
   - Comprehensive tech stack extraction from repositories
   - README analysis
   - Configuration file parsing
   - Source code analysis

## Installation

```bash
# Navigate to the skill directory
cd leo_skills/utilities/tech-extractor-cskill

# Install dependencies (optional - skill is mostly self-contained)
pip install -r requirements.txt  # if needed
```

## Usage

### Command Line Interface

```bash
# Extract technologies from text
python scripts/main.py extract-text "This application is built with React, Node.js, and MongoDB"

# Extract from documentation
python scripts/main.py extract-doc "https://docs.example.com"

# Extract from code
python scripts/main.py extract-code "import pandas as pd\nimport numpy as np" --language python

# Analyze trends
python scripts/main.py analyze-trends "react,vue,angular" --period 1y --format json

# Extract from repository
python scripts/main.py extract-repo "https://github.com/example/repo"
```

### Python API

```python
from scripts.main import TechExtractor

# Initialize extractor
extractor = TechExtractor()

# Extract from text
technologies = extractor.extract_from_text("Built with Django and PostgreSQL")

# Extract from code
tech_from_code = extractor.extract_from_code(code_string, language="python")

# Analyze trends
trends = extractor.analyze_trends(["react", "vue", "angular"])

# Extract from repository
repo_info = extractor.extract_from_repository("https://github.com/example/repo")
```

## Supported Technologies

### Programming Languages
- Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, Ruby, C#

### Frameworks
- React, Vue, Angular, Django, Flask, FastAPI, Express, Spring, Laravel

### Libraries
- NumPy, Pandas, TensorFlow, PyTorch, scikit-learn, Matplotlib, jQuery, Lodash

### Databases
- MySQL, PostgreSQL, MongoDB, Redis, SQLite, Elasticsearch

### Cloud Platforms
- AWS, Azure, Google Cloud, Heroku, Vercel, Netlify

### Tools
- Docker, Kubernetes, Git, Jenkins, Webpack, Babel

## Configuration

Edit `config.yaml` to customize:

- Confidence thresholds
- Trend sources
- API credentials
- Output preferences
- Feature flags

## Output Formats

The skill supports multiple export formats:

- **JSON** - Structured data with all details
- **CSV** - Tabular format for spreadsheets
- **YAML** - Human-readable configuration format

## Data Sources

### Trend Analysis Sources

1. **GitHub**
   - Repository stars, forks, issues
   - Activity trends
   - Community engagement

2. **Stack Overflow**
   - Questions and answers
   - View counts and scores
   - Community participation

3. **Reddit**
   - Post mentions and discussions
   - Comment activity
   - Community sentiment

4. **News & Articles**
   - Media mentions
   - Industry coverage
   - Thought leadership

5. **Package Managers**
   - Download statistics
   - Package usage trends
   - Version adoption

## API Integration

The skill is designed to integrate with external APIs. Configure API credentials in `config.yaml`:

```yaml
apis:
  github:
    token: "your_github_token"
  stackoverflow:
    key: "your_stackoverflow_key"
  reddit:
    client_id: "your_reddit_client_id"
    client_secret: "your_reddit_client_secret"
```

## Examples

### Basic Technology Extraction

```python
extractor = TechExtractor()
text = """
Our microservices architecture uses:
- Backend: Node.js with Express
- Database: MongoDB
- Container: Docker
- Orchestration: Kubernetes
"""

technologies = extractor.extract_from_text(text)
for tech in technologies:
    print(f"{tech.name} ({tech.category}): {tech.description}")
```

### Trend Comparison

```python
trends = extractor.compare_trends(['react', 'vue', 'angular'])
print(f"Top growing: {trends['ranking_by_growth'][0][0]}")
for insight in trends['insights']:
    print(f"- {insight}")
```

### Repository Analysis

```python
repo_data = extractor.extract_from_repository('https://github.com/example/react-app')
print(f"Tech Stack: {repo_data['tech_stack']}")
print(f"Summary: {repo_data['summary']}")
```

## Contributing

1. Add new technology patterns to `utils/tech_classifier.py`
2. Extend language support in `utils/pattern_matcher.py`
3. Add new trend sources in `utils/trend_analyzer.py`
4. Update configuration schema in `config.yaml`

## License

This skill is part of the Leo AI Agent System and follows the same licensing terms.

## Version History

### v1.0.0
- Initial release
- Basic technology extraction
- Multi-language support
- Trend analysis
- Repository analysis
- CLI interface