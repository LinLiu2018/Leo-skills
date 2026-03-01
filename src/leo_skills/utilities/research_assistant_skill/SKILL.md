# Research Assistant Skill

执行学术研究任务的技能。

## Research

```python
from leo_skills.utilities.research_assistant_skill import ResearchAssistant

researcher = ResearchAssistant()
results = researcher.execute("research", topic="量子计算", depth=2)
```

## Search Papers

```python
results = researcher.execute("search", query="machine learning healthcare", max_results=10)
```

## Analyze

```python
analysis = researcher.execute("analyze", paper_doi="10.48550/arXiv.2301.07041")
```

---
**Version:** 1.0.0
