# Naming Conventions: The "_skill" Suffix

## 🎯 **Purpose and Overview**

This document establishes the mandatory naming convention for all Claude Skills created by Agent-Skill-Creator, using the "_skill" suffix and **snake_case** format to ensure clear identification, Python compatibility, and professional consistency.

## 🏷️ **The "_skill" Suffix**

### **Meaning**

- **_skill** = Indicates a Claude Skill module
- Indicates the skill was automatically created by Agent-Skill-Creator
- Differentiates from manually created skills or other tools
- **Ensures Python import compatibility**

### **Benefits**

✅ **Python Compatibility**

- Can be directly imported as Python module
- No need for path escaping or special handling
- Works seamlessly with `from xxx_skill import ...`

✅ **Immediate Identification**

- Anyone sees "_skill" and immediately knows it's a Claude Skill
- Instant recognition of origin (Agent-Skill-Creator)

✅ **Easy Organization**

- Easy to filter and find skills created by the creator
- Logical grouping in file systems
- Efficient search with consistent pattern

✅ **Professionalism**

- Professional and standardized naming convention
- Clarity in communication about origin and type
- Organized and intentional appearance

## 📋 **Naming Rules**

### **1. Mandatory Format**

```
{descriptive_description}_skill/
```

### **2. Base Name Structure**

#### **Simple Skills (Single Objective)**

```
{action}_{object}_skill/
```

**Examples:**

- `pdf_text_extractor_skill/`
- `csv_data_cleaner_skill/`
- `image_converter_skill/`
- `email_automation_skill/`
- `report_generator_skill/`

#### **Complex Skill Suites (Multiple Components)**

```
{domain}_analysis_suite_skill/
{domain}_automation_skill/
{domain}_workflow_skill/
```

**Examples:**

- `financial_analysis_suite_skill/`
- `ecommerce_automation_skill/`
- `research_workflow_skill/`
- `business_intelligence_skill/`

#### **Component Skills (Within Suites)**

```
{functionality}_{domain}_skill/
```

**Examples:**

- `data_acquisition_skill/`
- `technical_analysis_skill/`
- `reporting_generator_skill/`
- `user_interface_skill/`

### **3. Formatting Rules**

✅ **REQUIRED:**

- Always lowercase
- Use underscores (_) to separate words
- End with "_skill"
- Be descriptive and clear
- Use only alphanumeric characters and underscores

❌ **PROHIBITED:**

- Uppercase letters
- Hyphens (-) ← **禁止使用连字符**
- Whitespace
- Special characters (!@#$%&*)
- Numbers at the beginning
- Non-standard abbreviations

### **4. Recommended Length**

- **Minimum:** 10 characters (ex: `pdf_tool_skill`)
- **Ideal:** 20-40 characters (ex: `financial_analysis_suite_skill`)
- **Maximum:** 60 characters (justified exceptions)

## 🔧 **Name Generation Process**

### **Agent-Skill-Creator Automatic Logic**

```python
def generate_skill_name(user_requirements, complexity):
    """
    Generates skill name following _skill convention
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

    # 4. Apply _skill convention
    skill_name = f"{base_name}_skill"

    return skill_name

def sanitize_name(name):
    """Sanitizes name to valid format"""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and hyphens with underscores
    name = re.sub(r'[\s-]+', '_', name)
    # Remove special characters
    name = re.sub(r'[^a-z0-9_]', '', name)
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    # Remove underscores at start/end
    name = name.strip('_')
    return name
```

### **Transformation Examples**

| User Input | Type | Extracted Concepts | Generated Name |
|------------------|------|-------------------|-------------|
| "Extract text from PDF" | Simple | ["extract", "text", "pdf"] | `pdf_text_extractor_skill/` |
| "Clean CSV data automatically" | Simple | ["clean", "csv", "data"] | `csv_data_cleaner_skill/` |
| "Complete financial analysis platform" | Suite | ["financial", "analysis", "platform"] | `financial_analysis_suite_skill/` |
| "Automate e-commerce workflows" | Suite | ["automate", "ecommerce", "workflows"] | `ecommerce_automation_skill/` |
| "Generate weekly status reports" | Simple | ["generate", "weekly", "reports"] | `weekly_report_generator_skill/` |

## 📚 **Practical Examples by Domain**

### **Finance and Investments**

```
financial_analysis_suite_skill/
portfolio_optimizer_skill/
market_data_fetcher_skill/
risk_calculator_skill/
trading_signal_generator_skill/
```

### **Data Analysis**

```
data_visualization_skill/
statistical_analysis_skill/
etl_pipeline_skill/
data_cleaner_skill/
dashboard_generator_skill/
```

### **Document Automation**

```
pdf_processor_skill/
word_automation_skill/
excel_report_generator_skill/
presentation_creator_skill/
document_converter_skill/
```

### **E-commerce and Sales**

```
inventory_tracker_skill/
sales_analytics_skill/
customer_data_processor_skill/
order_automation_skill/
price_monitor_skill/
```

### **Research and Academia**

```
literature_review_skill/
citation_manager_skill/
research_data_collector_skill/
academic_paper_generator_skill/
survey_analyzer_skill/
```

## 🔍 **Validation and Quality**

### **Automatic Verification**

```python
def validate_skill_name(skill_name):
    """
    Validates if name follows _skill convention
    """

    # 1. Check _skill suffix
    if not skill_name.endswith("_skill"):
        return False, "Missing _skill suffix"

    # 2. Check lowercase format
    if skill_name != skill_name.lower():
        return False, "Must be lowercase"

    # 3. Check valid characters (no hyphens!)
    if not re.match(r'^[a-z0-9_]+_skill$', skill_name):
        return False, "Contains invalid characters (hyphens not allowed)"

    # 4. Check length
    if len(skill_name) < 10 or len(skill_name) > 60:
        return False, "Invalid length"

    # 5. Check consecutive underscores
    if '__' in skill_name:
        return False, "Contains consecutive underscores"

    return True, "Valid naming convention"
```

### **Quality Checklist**

For each generated name, verify:

- [ ] **Ends with "_skill"** ✓
- [ ] **Is in lowercase** ✓
- [ ] **Uses only underscores as separators** ✓
- [ ] **No hyphens (-)** ✓
- [ ] **Is descriptive and clear** ✓
- [ ] **Has no special characters** ✓
- [ ] **Appropriate length (10-60 characters)** ✓
- [ ] **Easy to pronounce and remember** ✓
- [ ] **Reflects main functionality** ✓
- [ ] **Is unique in ecosystem** ✓

## 🚀 **Best Practices**

### **1. Be Descriptive**

```
✅ good: pdf_text_extractor_skill
❌ bad: tool_skill

✅ good: financial_analysis_suite_skill
❌ bad: finance_skill
```

### **2. Keep It Simple**

```
✅ good: csv_data_cleaner_skill
❌ bad: automated_csv_data_validation_and_cleaning_tool_skill

✅ good: email_automation_skill
❌ bad: professional_email_marketing_automation_workflow_skill
```

### **3. Be Consistent**

```
✅ good: data_acquisition_skill, data_processing_skill, data_visualization_skill
❌ bad: get_data_skill, process_skill, visualize_skill
```

### **4. Think About the User**

```
✅ good: weekly_report_generator_skill (clear what it does)
❌ bad: wrk_gen_skill (abbreviated, confusing)
```

## 🔄 **Migration from Old Convention**

### **Existing Skills with "-cskill" (Hyphen)**

If you have existing skills with the old hyphen convention:

1. **Rename to underscore format**

   ```bash
   mv old-skill-name-cskill old_skill_name_skill
   ```

2. **Update internal references**
   - Update SKILL.md
   - Modify marketplace.json
   - Update documentation
   - Update Python imports

3. **Test functionality**
   - Verify skill still works
   - Confirm correct installation
   - Test Python imports

### **Migration Documentation**

For each migrated skill, document:

```markdown
## Migration History
- **Original Name**: `old-name-cskill`
- **New Name**: `old_name_skill`
- **Migration Date**: YYYY-MM-DD
- **Reason**: Apply snake_case naming convention for Python compatibility
- **Impact**: Improved import compatibility
```

## 📖 **Quick Reference Guide**

### **To Create New Name:**

1. **Identify main objective** (ex: "extract PDF text")
2. **Extract key concepts** (ex: extract, pdf, text)
3. **Build base name with underscores** (ex: pdf_text_extractor)
4. **Add suffix** (ex: pdf_text_extractor_skill)

### **To Validate Existing Name:**

1. **Check "_skill" suffix**
2. **Confirm lowercase format**
3. **Check NO hyphens (use underscores only)**
4. **Evaluate descriptiveness**

### **To Troubleshoot:**

- **Name too short**: Add descriptor
- **Name too long**: Remove secondary words
- **Confusing name**: Use clearer synonyms
- **Name conflict**: Add differentiator
- **Has hyphens**: Replace with underscores

## ✅ **Convention Summary**

**Formula:** `{descriptive_description}_skill/`

**Essential Rules:**

- ✅ Always end with "_skill"
- ✅ Always lowercase
- ✅ Use underscores as separators
- ✅ **NO hyphens (-) allowed**
- ✅ Be descriptive and clear

**Results:**

- 🎯 Immediate identification as Claude Skill
- 🏗️ Clear origin (Agent-Skill-Creator)
- 📁 Easy organization
- 🔍 Efficient search
- 💬 Clear communication
- 🐍 **Python import compatibility**

**This convention ensures professional consistency, Python compatibility, and eliminates any confusion about the origin and type of created skills!**

