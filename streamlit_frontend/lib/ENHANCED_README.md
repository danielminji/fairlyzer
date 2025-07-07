# Enhanced Resume Analyzer

This directory contains enhanced components for the resume analysis system that provide improved extraction, parsing, and job recommendation capabilities.

## New Components

### Enhanced Extractor (`enhanced_extractor.py`)
An improved PDF text extraction module that better handles modern resume layouts, including:
- Better handling of two-column layouts
- Improved section detection
- Better handling of formatting and whitespace

### Enhanced Parser (`enhanced_parser.py`)
A more advanced parser that extracts structured information from resume text with significantly better accuracy:
- Improved contact information extraction
- Better education and work experience parsing
- Enhanced skills categorization
- More accurate language proficiency detection
- Industry detection based on skills and experience
- Job role recommendations based on profile matching

### Advanced Resume Analyzer (`advanced_resume_analyzer.py`)
A top-level integration module that combines the enhanced extractor and parser:
- Provides a unified interface for resume analysis
- Includes booth recommendations based on skills and industry
- Better error handling and debugging

### Analyzer Transition (`analyzer_transition.py`)
A compatibility layer to support transitioning between the legacy and enhanced analyzers:
- Provides backward compatibility
- Allows feature flagging to enable/disable enhanced features
- Consistent error handling and logging

## Installation

Install the required dependencies:

```bash
pip install requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

### Basic Usage

```python
from lib.analyzer_transition import analyze_resume_pdf

# Analyze a resume (using enhanced analyzer by default)
result_json = analyze_resume_pdf('path/to/resume.pdf')
```

### Advanced Usage

```python
from lib.analyzer_transition import AnalyzerManager

# Create analyzer manager with options
analyzer = AnalyzerManager(use_advanced=True, debug=True)

# Analyze a resume
result = analyzer.analyze_resume('path/to/resume.pdf')

# Access structured data
contact_info = result.get('data', {}).get('contact_info', {})
skills = result.get('data', {}).get('skills', {}).get('skills_list', [])
recommended_jobs = result.get('data', {}).get('job_recommendations', [])
```

## Features Comparison

| Feature | Legacy Analyzer | Enhanced Analyzer |
|---------|----------------|-------------------|
| PDF Text Extraction | Basic handling | Improved layout detection |
| Contact Info | Basic regex | NER + improved patterns |
| Education | Limited accuracy | Better institution/degree matching |
| Experience | Basic extraction | Improved title/company/date extraction |
| Skills | Simple list | Categorized with skill groups |
| Languages | Not supported | Language-proficiency detection |
| Industry Detection | Basic | ML-based on skills and experience |
| Job Recommendations | Not supported | Comprehensive matching algorithm |
| Booth Recommendations | Basic matching | Improved relevance scoring |

## Further Improvements

Future enhancements could include:
1. Machine learning-based section classification
2. Improved entity recognition with a custom-trained NER model
3. Resume quality scoring and suggestions
4. Integration with job databases for more accurate matching 