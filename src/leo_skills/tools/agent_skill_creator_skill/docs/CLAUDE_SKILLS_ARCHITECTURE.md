# Claude Skills Architecture: Complete Guide

## 🎯 **Purpose**

This document eliminates confusion between different types of Claude Code Skills and establishes consistent terminology.

## 📚 **Standard Terminology**

### **Skill**

A **Skill** is a complete Claude Code capability implemented as a folder containing:

- `SKILL.md` file (required)
- Optional resources (scripts/, references/, assets/)
- Domain-specific functionality

**Example:** `my-skill/` containing financial data analysis

### **Component Skill**

A **Component Skill** is a specialized sub-skill that is part of a larger Skill Suite.

- Has its own `SKILL.md`
- Focuses on specific functionality
- Shares resources with other component skills

**Example:** `data-acquisition/SKILL.md` within a financial analysis suite

### **Skill Suite**

A **Skill Suite** is an integrated collection of Component Skills that work together.

- Has `marketplace.json` as manifest
- Multiple specialized component skills
- Shared resources between skills

**Example:** Complete financial analysis suite with skills for data acquisition, analysis, and reporting.

### **Marketplace Plugin**

A **Marketplace Plugin** is the `marketplace.json` file that hosts and organizes one or more Skills.

- **NOT a skill** - it's an organizational manifest
- Defines how skills should be loaded
- Can host simple skills or complex suites

## 🏗️ **Architecture Types**

### **Architecture 1: Simple Skill**

```
my-skill/
├── SKILL.md              ← Single skill file
├── scripts/              ← Optional supporting code
├── references/           ← Optional documentation
└── assets/               ← Optional templates/resources
```

**When to use:**

- Focused, single functionality
- Simple workflow
- Less than 1000 lines of total code
- One main objective

**Examples:**

- Business proposal generator
- PDF data extractor
- ROI calculator

### **Architecture 2: Complex Skill Suite**

```
my-suite/                       ← Complete Skill Suite
├── .claude-plugin/
│   └── marketplace.json        ← Skills manifest
├── component-1/                ← Component Skill 1
│   ├── SKILL.md
│   └── scripts/
├── component-2/                ← Component Skill 2
│   ├── SKILL.md
│   └── references/
├── component-3/                ← Component Skill 3
│   ├── SKILL.md
│   └── assets/
└── shared/                     ← Shared resources
    ├── utils/
    ├── config/
    └── templates/
```

**When to use:**

- Multiple related workflows
- Complex functionalities that need separation
- More than 2000 lines of total code
- Multiple interconnected objectives

**Examples:**

- Complete financial analysis suite
- Project management system
- E-commerce analytics platform

### **Architecture 3: Hybrid (Simple + Components)**

```
my-hybrid-skill/               ← Main simple skill
├── SKILL.md                   ← Main orchestration
├── scripts/
│   ├── main.py               ← Main logic
│   └── components/           ← Specialized components
├── references/
└── assets/
```

**When to use:**

- Main functionality with sub-components
- Moderate complexity
- Centralized orchestration required

## 🔍 **Deciding Which Architecture to Use**

### **Use Simple Skill when:**

- ✅ Clear main objective
- ✅ Linear and sequential workflow
- ✅ Less than 3 distinct subprocesses
- ✅ Code < 1000 lines
- ✅ One person can easily maintain

### **Use Complex Skill Suite when:**

- ✅ Multiple related objectives
- ✅ Independent but connected workflows
- ✅ More than 3 distinct subprocesses
- ✅ Code > 2000 lines
- ✅ Team or complex maintenance

### **Use Hybrid when:**

- ✅ Central orchestration is critical
- ✅ Components are optional/configurable
- ✅ Main workflow with specialized sub-tasks

## 📋 **Marketplace.json Explained**

The `marketplace.json` **IS NOT** a skill. It's an **organizational manifest**:

```json
{
  "name": "my-suite",
  "plugins": [
    {
      "name": "component-1",
      "source": "./component-1/",
      "skills": ["./SKILL.md"]     ← Points to the actual skill
    },
    {
      "name": "component-2",
      "source": "./component-2/",
      "skills": ["./SKILL.md"]     ← Points to another skill
    }
  ]
}
```

**Analogy:** Think of `marketplace.json` as a **book index** - it's not the content, just organizes and points to the chapters (skills).

## 🚫 **Terminology to Avoid**

To avoid confusion:

❌ **"Plugin"** to refer to individual skills
✅ **"Component Skill"** or **"Skill Suite"**

❌ **"Multi-plugin architecture"**
✅ **"Multi-skill suite"**

❌ **"Plugin marketplace"**
✅ **"Skill marketplace"** (when hosting skills)

## ✅ **Correct Terms**

| Situation | Correct Term | Example (with -cskill convention) |
|----------|---------------|--------------------------------|
| Single file with capability | **Simple Skill** | `pdf-generator-cskill/SKILL.md` |
| Specialized sub-capability | **Component Skill** | `data-extraction-cskill/SKILL.md` |
| Set of capabilities | **Skill Suite** | `financial-analysis-suite-cskill/` |
| Organizational file | **Marketplace Plugin** | `marketplace.json` |
| Complete system | **Skill Ecosystem** | Suite + Marketplace + Resources |

## 🏷️ **Naming Convention: The "-cskill" Suffix**

### **Purpose of the "-cskill" Suffix**

- **Clear Identification**: Immediately indicates it's a Claude Skill
- **Defined Origin**: Created by Agent-Skill-Creator
- **Consistent Standard**: Professional convention across all documentation
- **Avoids Confusion**: Distinguishes from manual skills or other sources
- **Easy Organization**: Simple identification and grouping

### **Naming Rules**

**1. Standard Format**

```
{descriptive-description}-cskill/
```

**2. Simple Skills**

```
pdf-text-extractor-cskill/
csv-data-cleaner-cskill/
weekly-report-generator-cskill/
image-converter-cskill/
```

**3. Complex Skill Suites**

```
financial-analysis-suite-cskill/
e-commerce-automation-cskill/
research-workflow-cskill/
business-intelligence-cskill/
```

**4. Component Skills (within suites)**

```
data-acquisition-cskill/
technical-analysis-cskill/
reporting-generator-cskill/
user-interface-cskill/
```

**5. Formatting**

- ✅ Always lowercase
- ✅ Use hyphens to separate words
- ✅ Descriptive and clear
- ✅ End with "-cskill"
- ❌ No underscores or spaces
- ❌ No special characters (except hyphens)

### **Transformation Examples**

| User Requirement | Generated Name |
|---------------------|-------------|
| "Extract text from PDF documents" | `pdf-text-extractor-cskill/` |
| "Clean CSV data automatically" | `csv-data-cleaner-cskill/` |
| "Complete financial analysis platform" | `financial-analysis-suite-cskill/` |
| "Generate weekly status reports" | `weekly-report-generator-cskill/` |
| "Automate e-commerce workflows" | `e-commerce-automation-cskill/` |

## 🎯 **Golden Rule**

**If it has `SKILL.md` → It's a Skill (simple or component)
If it has `marketplace.json` → It's a marketplace plugin (organization)**

## 📖 **Real-World Examples**

### **Simple Skill: Business Proposal**

```
business-proposal/
├── SKILL.md              ← "Create business proposals"
├── references/
│   └── template.md
└── assets/
    └── logo.png
```

### **Complex Skill Suite: Financial Analysis**

```
financial-analysis-suite/
├── .claude-plugin/marketplace.json
├── data-acquisition/SKILL.md    ← "Download market data"
├── technical-analysis/SKILL.md  ← "Analyze technical indicators"
├── portfolio-analysis/SKILL.md  ← "Optimize portfolio"
└── reporting/SKILL.md          ← "Generate reports"
```

Both are **legitimate Claude Code Skills** - just with different complexity levels.

---

## 🔄 **How This Document Helps**

1. **Clear terminology** - Everyone uses the same terms
2. **Informed decisions** - Know when to use each architecture
3. **Effective communication** - No ambiguity between skills and plugins
4. **Consistent documentation** - Standard across all agent_skill_creator_skill documentation

**Result:** Less confusion, more clarity, better development!
