# Research Assistant - Claude Skill

A comprehensive research assistant for academic literature search, paper analysis, summarization, and citation management.

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-Apache%202.0-yellow)

---

## What This Skill Does

The Research Assistant automates your academic research workflow:

- **Search** academic databases (Semantic Scholar, arXiv, PubMed, Crossref, OpenAlex)
- **Analyze** papers to extract key findings, methodology, and contributions
- **Summarize** papers in multiple styles (concise, detailed, bullet points)
- **Manage citations** in APA, MLA, Chicago, Harvard, IEEE, and BibTeX formats
- **Generate** structured literature reviews
- **Track** research trends and identify gaps

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install skill in Claude Code
/plugin marketplace add ./research-assistant-cskill
```

### Basic Usage

```python
from scripts.main import ResearchAssistant

# Initialize
assistant = ResearchAssistant()

# Search for papers
papers = assistant.search_papers(
    query="transformer models attention mechanism",
    max_results=10
)

# Analyze a paper
paper = assistant.analyze_paper("10.48550/arXiv.2301.07041")

# Generate summary
summary = assistant.summarize_paper(paper, style="concise")

# Format citation
citation = assistant.format_citation(paper, style="apa")

# Generate literature review
review = assistant.generate_literature_review(
    topic="artificial intelligence in education",
    num_papers=15
)
```

---

## Commands

### Search Papers
```
"Search for papers on machine learning in healthcare"
"Find recent research about transformer models"
"Look up publications on climate change from 2023"
```

### Analyze Papers
```
"Analyze this paper and extract key findings"
"What methodology does this paper use?"
"Summarize the main contributions of this research"
```

### Citations
```
"Generate APA citation for this paper"
"Create BibTeX entry for this DOI"
"Format this paper in Chicago style"
```

### Literature Review
```
"Generate a literature review on AI ethics"
"What are the main research gaps in quantum computing?"
"Summarize the trends in natural language processing"
```

---

## Supported Databases

| Database | Focus | Rate Limit |
|----------|-------|------------|
| Semantic Scholar | AI/ML, General | 100 req/5s |
| arXiv | Physics, Math, CS | 1 req/3s |
| PubMed | Biomedical, Life Sciences | 50 req/s |
| Crossref | DOI lookup | Varies |
| OpenAlex | Open scholarly data | 1000/day |

---

## Citation Styles

| Style | Description |
|-------|-------------|
| `apa` | APA 7th Edition |
| `mla` | MLA 9th Edition |
| `chicago` | Chicago 17th Edition |
| `harvard` | Harvard Style |
| `ieee` | IEEE Format |
| `bibtex` | BibTeX for LaTeX |

---

## File Structure

```
research-assistant-cskill/
├── .claude-plugin/
│   └── marketplace.json      ← Skill activation config
├── scripts/
│   ├── main.py               ← Main entry point
│   ├── search/
│   │   └── literature_search.py  ← Database search
│   ├── analyze/
│   │   └── paper_analyzer.py     ← Paper analysis
│   ├── summarize/
│   │   └── summarizer.py         ← Summarization
│   ├── citations/
│   │   └── citation_manager.py   ← Citation formatting
│   └── utils/
│       └── helpers.py            ← Utilities
├── references/                 ← Documentation
├── assets/                     ← Config/examples
├── SKILL.md                    ← Full skill definition
├── README.md                   ← This file
├── requirements.txt            ← Python dependencies
└── DECISIONS.md               ← Design decisions
```

---

## Configuration

Create a `.env` file or `config.yaml`:

```yaml
# API Keys (optional)
semantic_scholar_api_key: your_key_here
openalex_api_key: your_key_here

# Defaults
default_max_results: 10
default_citation_style: apa
enable_cache: true
cache_days: 7
```

Or use environment variables:

```bash
export SEMANTIC_SCHOLAR_API_KEY="your_key"
export DEFAULT_MAX_RESULTS=10
export DEFAULT_CITATION_STYLE="apa"
```

---

## Examples

### Example 1: Quick Paper Search
```python
papers = assistant.search_papers("large language models", max_results=5)
for paper in papers:
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Citations: {paper.citation_count}")
    print("---")
```

### Example 2: Generate Citation
```python
paper = assistant.analyze_paper("10.1038/nature12373")

# APA citation
apa = assistant.format_citation(paper, style="apa")
print(apa)

# BibTeX entry
bibtex = assistant.generate_bibtex(paper)
print(bibtex)
```

### Example 3: Create Literature Review
```python
review = assistant.generate_literature_review(
    topic="AI ethics",
    num_papers=20,
    output_format="structured"
)
print(review)
```

---

## Performance

| Operation | Time |
|-----------|------|
| Paper Search | 2-10s |
| Paper Analysis | 5-15s |
| Summary | 3-8s |
| Citation | 1-3s |
| Lit Review (10 papers) | 30-60s |

---

## Troubleshooting

### No Results
- Try broader search terms
- Check spelling of author names
- Use year filters less restrictively

### API Errors
- Check API key validity
- Wait and retry (rate limiting)
- Use alternative data source

### Citation Issues
- Verify all required fields present
- Try alternative citation styles
- Manually enter missing data

---

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependencies

---

## License

Apache 2.0 - See LICENSE file for details.

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

---

## Acknowledgments

- Semantic Scholar API
- arXiv
- PubMed (NCBI)
- Crossref
- OpenAlex
