# Research Assistant - Claude Skill

A comprehensive research assistant for academic literature search, paper analysis, summarization, and citation management.

**Version:** 1.0.0
**Created:** 2025-01-06
**Author:** Claude Code with Agent-Skill-Creator

---

## What This Skill Does

The Research Assistant skill automates academic research workflows:

- **🔍 Literature Search** - Search academic databases (Semantic Scholar, arXiv, PubMed, Crossref)
- **📄 Paper Analysis** - Extract key findings, methodology, and contributions from papers
- **📝 Summarization** - Generate concise summaries of research papers
- **📚 Citation Management** - Format citations in multiple styles (APA, MLA, Chicago, BibTeX)
- **📊 Literature Review** - Generate structured literature review summaries
- **🎯 Trend Analysis** - Identify research trends and gaps

---

## When To Use

### Literature Search
```
"Search for papers on machine learning in healthcare"
"Find recent research about transformer models"
"Search for papers by a specific author"
"Look up publications on climate change from 2023"
```

### Paper Analysis
```
"Analyze this paper and extract key findings"
"What methodology does this paper use?"
"Summarize the main contributions of this research"
"Extract the research questions from this paper"
```

### Citation Management
```
"Generate APA citation for this paper"
"Create BibTeX entry for this DOI"
"Format this paper in Chicago style"
"List all citations for a specific author"
```

### Literature Review
```
"Generate a literature review on AI ethics"
"Compare these papers on neural network architectures"
"What are the main research gaps in quantum computing?"
"Summarize the trends in natural language processing"
```

### Research Assistance
```
"Help me write a literature review for my thesis"
"Find papers that cite this specific paper"
"Identify the most influential papers in computer vision"
"Search for open-access papers on my research topic"
```

---

## When NOT To Use

- General coding questions not related to research
- Non-academic writing tasks
- Legal or medical advice
- Financial investment research
- Personal tasks unrelated to academic research

---

## How To Use

### 1. Basic Search
```python
# Search for papers on a topic
search_papers("transformer models attention mechanism", max_results=10)
```

### 2. Analyze a Paper
```python
# Analyze paper from DOI or URL
analyze_paper("10.48550/arXiv.2301.07041")
```

### 3. Generate Summary
```python
# Generate a concise summary
summary = summarize_paper(paper_data, max_length=200)
```

### 4. Manage Citations
```python
# Generate citation in specific format
citation = format_citation(paper_data, style="apa")

# Generate BibTeX entry
bibtex = generate_bibtex(paper_data)
```

### 5. Create Literature Review
```python
# Generate structured literature review
review = generate_literature_review(topic="AI ethics", num_papers=20)
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `search_papers(query, max_results)` | Search academic databases |
| `analyze_paper(identifier)` | Analyze paper structure and content |
| `summarize_paper(paper_data, length)` | Generate concise summary |
| `format_citation(paper, style)` | Format citation in style |
| `generate_bibtex(paper)` | Generate BibTeX entry |
| `find_citing_papers(doi)` | Find papers that cite a paper |
| `generate_literature_review(topic, count)` | Generate structured review |
| `extract_references(paper)` | Extract bibliography from paper |

---

## Supported Databases

- **Semantic Scholar** - Large academic database with AI/ML focus
- **arXiv** - Preprint server for physics, math, CS, and more
- **PubMed** - Biomedical and life sciences literature
- **Crossref** - DOI-based metadata lookup
- **OpenAlex** - Open scholarly knowledge graph
- **Google Scholar** (via web search) - General academic search

---

## Citation Styles Supported

| Style | Description |
|-------|-------------|
| `apa` | American Psychological Association (7th ed.) |
| `mla` | Modern Language Association (9th ed.) |
| `chicago` | Chicago Manual of Style (17th ed.) |
| `harvard` | Harvard referencing style |
| `ieee` | Institute of Electrical and Electronics Engineers |
| `bibtex` | BibTeX format for LaTeX/BibTeX |

---

## Configuration

Create a `.env` file in the skill directory:

```env
# Optional API Keys (some features require)
SEMANTIC_SCHOLAR_API_KEY=your_key_here
OPENALEX_API_KEY=your_key_here

# Default settings
DEFAULT_MAX_RESULTS=10
DEFAULT_CITATION_STYLE=apa
ENABLE_CACHE=true
CACHE_DAYS=7
```

---

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

---

## Installation

```bash
cd research-assistant-cskill
pip install -r requirements.txt
```

---

## Examples

### Example 1: Quick Search
```python
from scripts.search.literature_search import search_papers

papers = search_papers("large language models", max_results=5)
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {paper['authors']}")
    print(f"Year: {paper['year']}")
    print(f"Citations: {paper['citation_count']}")
    print("---")
```

### Example 2: Paper Analysis and Citation
```python
from scripts.analyze.paper_analyzer import analyze_paper
from scripts.citations.citation_manager import format_citation

paper = analyze_paper("10.48550/arXiv.2301.07041")
print(f"Title: {paper['title']}")
print(f"Abstract: {paper['abstract']}")
print(f"Key Findings: {paper['key_findings']}")

# Generate citation
apa_citation = format_citation(paper, style="apa")
print(f"APA: {apa_citation}")
```

### Example 3: Literature Review
```python
from scripts.main import ResearchAssistant

assistant = ResearchAssistant()
review = assistant.generate_literature_review(
    topic="artificial intelligence in education",
    num_papers=15,
    output_format="structured"
)
print(review)
```

---

## Output Formats

### Paper Search Results
```json
[
  {
    "paper_id": "...",
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "year": 2024,
    "venue": "Conference/Journal Name",
    "abstract": "...",
    "citation_count": 42,
    "url": "https://...",
    "doi": "10.xxx/xxx",
    "topics": ["AI", "Machine Learning"]
  }
]
```

### Literature Review
```markdown
# Literature Review: [Topic]

## Overview
This review synthesizes X papers on [topic] published between YYYY-ZZZZ.

## Key Themes

### Theme 1: [Name]
Summary of papers addressing this theme...

### Theme 2: [Name]
Summary of papers addressing this theme...

## Research Gaps
Identified gaps in current research...

## Future Directions
Suggested directions for future research...
```

---

## Performance Metrics

| Operation | Expected Time |
|-----------|---------------|
| Paper Search | 2-10 seconds |
| Paper Analysis | 5-15 seconds |
| Summary Generation | 3-8 seconds |
| Citation Formatting | 1-3 seconds |
| Literature Review (10 papers) | 30-60 seconds |

---

## Error Handling

The skill handles common errors gracefully:

- **Rate Limiting**: Automatic backoff and retry
- **API Errors**: Fallback to alternative sources
- **Missing Data**: Uses available fields with warnings
- **Invalid Inputs**: Clear error messages with suggestions
- **Network Issues**: Retry logic with configurable attempts

---

## Rate Limits

Be aware of API rate limits:

| Database | Free Tier Limit |
|----------|----------------|
| Semantic Scholar | 100 requests/5 seconds |
| arXiv | 1 request/3 seconds |
| OpenAlex | 1000 requests/day |
| Crossref | 50 requests/second |

---

## Best Practices

1. **Start with specific queries** - More specific = better results
2. **Use filters** - Year, venue, author constraints improve relevance
3. **Check citations** - Highly cited papers are often influential
4. **Verify sources** - Cross-reference important findings
5. **Use caching** - Enable for repeated searches

---

## Troubleshooting

### No Results Found
- Try broader search terms
- Check spelling of author names
- Try alternative databases
- Use year filters less restrictively

### API Errors
- Check API key validity
- Wait and retry (rate limiting)
- Use alternative data source
- Check network connectivity

### Citation Formatting Issues
- Verify all required fields are present
- Try alternative citation styles
- Manual entry for missing data

---

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
python-dateutil>=2.8.0
pyyaml>=6.0
bibtexparser>=1.4.0
aiohttp>=3.8.0
aiofiles>=22.0.0
tenacity>=8.2.0
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-06 | Initial release |

---

## License

Apache 2.0 - See LICENSE file for details

---

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---

## Support

- GitHub Issues: Report bugs and request features
- Documentation: See `references/` directory
- Examples: See `scripts/examples/` directory

---

## Acknowledgments

- Semantic Scholar API for academic search
- arXiv for open-access preprints
- OpenAlex for open scholarly data
- Crossref for DOI metadata
