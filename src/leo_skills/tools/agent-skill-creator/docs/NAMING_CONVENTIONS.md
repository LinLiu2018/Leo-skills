# Naming Conventions: The "-cskill" Suffix

## 🎯 **Purpose and Overview**

This document establishes the mandatory naming convention for all Claude Skills created by Agent-Skill-Creator, using the "-cskill" suffix to ensure clear identification and professional consistency.

## 🏷️ **The "-cskill" Suffix**

### **Meaning**

- **CSKILL** = **C**laude **SKILL**
- Indicates the skill was automatically created by Agent-Skill-Creator
- Differentiates from manually created skills or other tools

### **Benefits**

✅ **Immediate Identification**

- Anyone sees "-cskill" and immediately knows it's a Claude Skill
- Instant recognition of origin (Agent-Skill-Creator)

✅ **Easy Organization**

- Easy to filter and find skills created by the creator
- Logical grouping in file systems
- Efficient search with consistent pattern

✅ **Professionalism**

- Professional and standardized naming convention
- Clarity in communication about origin and type
- Organized and intentional appearance

✅ **Avoids Confusion**

- No ambiguity about what's a skill vs plugin
- Clear distinction between manual vs automated skills
- Prevention of name conflicts

## 📋 **Naming Rules**

### **1. Mandatory Format**

```
{descriptive-description}-cskill/
```

### **2. Base Name Structure**

#### **Simple Skills (Single Objective)**

```
{action}-{object}-csskill/
```

**Examples:**

- `pdf-text-extractor-cskill/`
- `csv-data-cleaner-cskill/`
- `image-converter-cskill/`
- `email-automation-cskill/`
- `report-generator-cskill/`

#### **Complex Skill Suites (Multiple Components)**

```
{domain}-analysis-suite-cskill/
{domain}-automation-cskill/
{domain}-workflow-cskill/
```

**Examples:**

- `financial-analysis-suite-cskill/`
- `e-commerce-automation-cskill/`
- `research-workflow-cskill/`
- `business-intelligence-cskill/`

#### **Component Skills (Within Suites)**

```
{functionality}-{domain}-cskill/
```

**Examples:**

- `data-acquisition-cskill/`
- `technical-analysis-cskill/`
- `reporting-generator-cskill/`
- `user-interface-cskill/`

### **3. Formatting Rules**

✅ **REQUIRED:**

- Always lowercase
- Use hyphens (-) to separate words
- End with "-cskill"
- Be descriptive and clear
- Use only alphanumeric characters and hyphens

❌ **PROHIBITED:**

- Uppercase letters
- Underscores (_)
- Whitespace
- Special characters (!@#$%&*)
- Numbers at the beginning
- Non-standard abbreviations

### **4. Recommended Length**

- **Minimum:** 10 characters (ex: `pdf-tool-cskill`)
- **Ideal:** 20-40 characters (ex: `financial-analysis-suite-cskill`)
- **Maximum:** 60 characters (justified exceptions)

## 🔧 **Name Generation Process**

### **Agent-Skill-Creator Automatic Logic**

```python
def generate_skill_name(user_requirements, complexity):
    """
    Generates skill name following -cskill convention
    """

    # 1. Extract key concepts from user input
    concepts = extract_key_concepts(user_requirements)

    # 2. Create base name based on complexity
    if complexity == "simple":
        base_name = create_simple_name(concepts)
    elif complexity == "complex_suite":
        base_name = create_suite_name(concepts)
    else:  # hybrid
        base_name = create_hybrid_name(concepts)

    # 3. Sanitize and format
    base_name = sanitize_name(base_name)

    # 4. Apply -cskill convention
    skill_name = f"{base_name}-cskill"

    return skill_name

def create_simple_name(concepts):
    """Creates name for simple skills"""
    if len(concepts) == 1:
        return f"{concepts[0]}-tool"
    elif len(concepts) == 2:
        return f"{concepts[1]}-{concepts[0]}"
    else:
        return "-".join(concepts[:2])

def create_suite_name(concepts):
    """Creates name for complex suites"""
    if len(concepts) <= 2:
        return f"{concepts[0]}-automation"
    else:
        return f"{concepts[0]}-{'-'.join(concepts[1:3])}-suite"

def sanitize_name(name):
    """Sanitizes name to valid format"""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[\s_]+', '-', name)
    # Remove special characters
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Remove multiple hyphens
    name = re.sub(r'-+', '-', name)
    # Remove hyphens at start/end
    name = name.strip('-')
    return name
```

### **Transformation Examples**

| User Input | Type | Extracted Concepts | Generated Name |
|------------------|------|-------------------|-------------|
| "Extract text from PDF" | Simple | ["extract", "text", "pdf"] | `pdf-text-extractor-cskill/` |
| "Clean CSV data automatically" | Simple | ["clean", "csv", "data"] | `csv-data-cleaner-cskill/` |
| "Complete financial analysis platform" | Suite | ["financial", "analysis", "platform"] | `financial-analysis-suite-cskill/` |
| "Automate e-commerce workflows" | Suite | ["automate", "ecommerce", "workflows"] | `ecommerce-automation-cskill/` |
| "Generate weekly status reports" | Simple | ["generate", "weekly", "reports"] | `weekly-report-generator-cskill/` |

## 📚 **Practical Examples by Domain**

### **Finance and Investments**

```
financial-analysis-suite-cskill/
portfolio-optimizer-cskill/
market-data-fetcher-cskill/
risk-calculator-cskill/
trading-signal-generator-cskill/
```

### **Data Analysis**

```
data-visualization-cskill/
statistical-analysis-cskill/
etl-pipeline-cskill/
data-cleaner-cskill/
dashboard-generator-cskill/
```

### **Document Automation**

```
pdf-processor-cskill/
word-automation-cskill/
excel-report-generator-cskill/
presentation-creator-cskill/
document-converter-cskill/
```

### **E-commerce and Sales**

```
inventory-tracker-cskill/
sales-analytics-cskill/
customer-data-processor-cskill/
order-automation-cskill/
price-monitor-cskill/
```

### **Research and Academia**

```
literature-review-cskill/
citation-manager-cskill/
research-data-collector-cskill/
academic-paper-generator-cskill/
survey-analyzer-cskill/
```

### **Productivity and Office**

```
email-automation-cskill/
calendar-manager-cskill/
task-tracker-cskill/
note-organizer-cskill/
meeting-scheduler-cskill/
```

## 🔍 **Validation and Quality**

### **Automatic Verification**

```python
def validate_skill_name(skill_name):
    """
    Validates if name follows -cskill convention
    """

    # 1. Check -cskill suffix
    if not skill_name.endswith("-cskill"):
        return False, "Missing -cskill suffix"

    # 2. Check lowercase format
    if skill_name != skill_name.lower():
        return False, "Must be lowercase"

    # 3. Check valid characters
    if not re.match(r'^[a-z0-9-]+-cskill$', skill_name):
        return False, "Contains invalid characters"

    # 4. Check length
    if len(skill_name) < 10 or len(skill_name) > 60:
        return False, "Invalid length"

    # 5. Check consecutive hyphens
    if '--' in skill_name:
        return False, "Contains consecutive hyphens"

    return True, "Valid naming convention"
```

### **Quality Checklist**

For each generated name, verify:

- [ ] **Ends with "-cskill"** ✓
- [ ] **Is in lowercase** ✓
- [ ] **Uses only hyphens as separators** ✓
- [ ] **Is descriptive and clear** ✓
- [ ] **Has no special characters** ✓
- [ ] **Appropriate length (10-60 characters)** ✓
- [ ] **Easy to pronounce and remember** ✓
- [ ] **Reflects main functionality** ✓
- [ ] **Is unique in ecosystem** ✓

## 🚀 **Best Practices**

### **1. Be Descriptive**

```
✅ good: pdf-text-extractor-cskill
❌ bad: tool-cskill

✅ good: financial-analysis-suite-cskill
❌ bad: finance-cskill
```

### **2. Keep It Simple**

```
✅ good: csv-data-cleaner-cskill
❌ bad: automated-csv-data-validation-and-cleaning-tool-cskill

✅ good: email-automation-cskill
❌ bad: professional-email-marketing-automation-workflow-cskill
```

### **3. Be Consistent**

```
✅ good: data-acquisition-cskill, data-processing-cskill, data-visualization-cskill
❌ bad: get-data-cskill, process-cskill, visualize-cskill
```

### **4. Think About the User**

```
✅ good: weekly-report-generator-cskill (clear what it does)
❌ bad: wrk-gen-cskill (abbreviated, confusing)
```

## 🔄 **Migration and Legacy**

### **Existing Skills Without "-cskill"**

If you have existing skills without the suffix:

1. **Add the suffix immediately**

   ```bash
   mv old-skill-name old-skill-name-cskill
   ```

2. **Update internal references**
   - Update SKILL.md
   - Modify marketplace.json
   - Update documentation

3. **Test functionality**
   - Verify skill still works
   - Confirm correct installation

### **Migration Documentation**

For each migrated skill, document:

```markdown
## Migration History
- **Original Name**: `old-name`
- **New Name**: `old-name-cskill`
- **Migration Date**: YYYY-MM-DD
- **Reason**: Apply -cskill naming convention
- **Impact**: None, purely cosmetic change
```

## 📖 **Quick Reference Guide**

### **To Create New Name:**

1. **Identify main objective** (ex: "extract PDF text")
2. **Extract key concepts** (ex: extract, pdf, text)
3. **Build base name** (ex: pdf-text-extractor)
4. **Add suffix** (ex: pdf-text-extractor-cskill)

### **To Validate Existing Name:**

1. **Check "-cskill" suffix**
2. **Confirm lowercase format**
3. **Check valid characters**
4. **Evaluate descriptiveness**

### **To Troubleshoot:**

- **Name too short**: Add descriptor
- **Name too long**: Remove secondary words
- **Confusing name**: Use clearer synonyms
- **Name conflict**: Add differentiator

## ✅ **Convention Summary**

**Formula:** `{descriptive-description}-cskill/`

**Essential Rules:**

- ✅ Always end with "-cskill"
- ✅ Always lowercase
- ✅ Use hyphens as separators
- ✅ Be descriptive and clear

**Results:**

- 🎯 Immediate identification as Claude Skill
- 🏗️ Clear origin (Agent-Skill-Creator)
- 📁 Easy organization
- 🔍 Efficient search
- 💬 Clear communication

**This convention ensures professional consistency and eliminates any confusion about the origin and type of created skills!**
