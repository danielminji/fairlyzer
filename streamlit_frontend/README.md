# Resume Analyzer & Booth Recommendations

A Streamlit-based application that analyzes resumes and matches job seekers with booths at job fairs based on skills and requirements.

## Installation

### Prerequisites
- Python 3.8+ installed
- [Laravel backend API](https://github.com/youraccount/resume-analyzer-api) running

### Setup

1. Clone this repository
```bash
git clone https://github.com/youraccount/resume-analyzer.git
cd resume-analyzer/streamlit_frontend
```

2. Install dependencies
```bash
# Using pip
pip install -r requirements.txt

# Optional: Download spaCy model for NLP features
python -m spacy download en_core_web_sm
```

3. Run the application
```bash
# On Windows, use the included PowerShell script
.\run.ps1

# Or run directly with Streamlit
streamlit run app.py
```

## Common Issues & Troubleshooting

### Requirements Installation
Make sure to use the `-r` flag when installing requirements:
```bash
# Correct
pip install -r requirements.txt

# Incorrect (will fail)
pip install requirements.txt
```

### Package Versions
The application now uses flexible version requirements with `>=` to prevent unnecessary downgrades. To check if your installed packages meet the requirements:

```bash
# Run the version checker script
.\check_versions.ps1
```

This will show a comparison between required and installed package versions and highlight any potential issues.

### Resume Upload Issues
If you encounter the "strtolower(): Argument #1 ($string) must be of type string, array given" error when uploading resumes:

- Rename your file to use only letters, numbers, underscores, and hyphens (avoid spaces and special characters)
- Examples of good filenames:
  - `my_resume.pdf` (good)
  - `john_smith_resume.pdf` (good)
  - `resume-2023.pdf` (good)
- Examples of problematic filenames:
  - `My Resume (2023).pdf` (bad - contains spaces and parentheses)
  - `résumé.pdf` (bad - contains non-ASCII characters)
  - `John's Resume.pdf` (bad - contains apostrophe and space)

The application will try to sanitize filenames automatically, but it's best to use clean filenames from the start.

## Features

- Resume upload and analysis
- Skill extraction from resumes
- Matching with job fair booths based on skills
- Interactive booth map with recommendations
- Organizer dashboard for managing job fairs and booths
- Admin dashboard for user management

## License

MIT

## Architecture

The application follows a clean architecture with clear separation of concerns:

### Core Components

- **Enhanced Parser (`lib/enhanced_parser.py`)**: The core resume parsing and analysis engine.
- **Analyzer (`lib/analyzer.py`)**: Unified interface for resume analysis that uses the enhanced parser.
- **API Client (`lib/api.py`)**: Handles communication with the Laravel backend API.
- **Auth Client (`lib/auth_client.py`)**: Manages authentication and session state.
- **UI Components (`lib/ui_components.py`)**: Reusable UI components for consistent rendering.

### Pages

1. **Resume Upload (`pages/01_resume_upload.py`)**: Upload resume files for analysis.
2. **Resume Analysis (`pages/02_resume_analysis.py`)**: Display detailed resume analysis with skills, experience, education, and recommendations.
3. **Booth Recommendations (`pages/03_booth_recommendations.py`)**: Show recommended booths based on resume skills.
4. **Booth Map (`pages/04_booth_map.py`)**: Interactive map visualization of booths with recommendations highlighted.

### Flow

1. User uploads a resume through the upload page
2. The analyzer parses and analyzes the resume
3. The analysis results are displayed on the analysis page
4. Recommendations are calculated based on resume skills and displayed on the recommendations page
5. The booth map visualizes these recommendations in context of the job fair layout

## Integration with Backend

The application connects with a Laravel API backend for:
- User authentication
- Storing and retrieving resumes
- Managing job fairs and booths
- Retrieving recommendations

The integration is handled through the `api.py` module, which provides a clean interface for making API requests.

## Data Flow

1. **Resume Upload**: User uploads a resume → API stores the file → Backend analyzes it → Analysis data stored
2. **Resume Analysis**: Frontend requests analysis data from backend → Displays analysis
3. **Booth Recommendations**: Frontend requests recommendations based on resume id and job fair id → Displays recommendations
4. **Booth Map**: Frontend requests booth data → Plots booths on map → Highlights recommended booths

## Directory Structure

```
streamlit_frontend/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── lib/                    # Core libraries
│   ├── __init__.py         # Package initialization
│   ├── analyzer.py         # Unified analyzer module
│   ├── enhanced_parser.py  # Advanced resume parser
│   ├── api.py              # API client for backend
│   ├── auth_client.py      # Authentication manager
│   ├── ui_components.py    # Reusable UI components
│   └── css/                # CSS styling
├── pages/                  # Application pages
│   ├── 01_resume_upload.py         # Resume upload page
│   ├── 02_resume_analysis.py       # Resume analysis page
│   ├── 03_booth_recommendations.py # Booth recommendations page
│   └── 04_booth_map.py             # Interactive booth map
├── tests/                  # Unit tests
└── .streamlit/             # Streamlit configuration
```

## Best Practices Used

- **Separation of Concerns**: Clear separation between data processing, API communication, and UI rendering
- **Single Responsibility**: Each module has a single responsibility
- **DRY (Don't Repeat Yourself)**: Common functionality is abstracted into reusable components
- **Consistent API**: All modules follow consistent naming and parameter conventions
- **Error Handling**: Comprehensive error handling for API calls and data processing
- **Type Hints**: Python type annotations for better code clarity and IDE support

## Requirements

- Python 3.7+
- Streamlit 1.31.0
- Requests library
- Pandas library
- Matplotlib library
- Plotly library
- Python-dotenv

## Running the Application

To run the Streamlit application:

```
streamlit run app.py
```

The application will be available at http://localhost:8501

### Running Both Frontend and Backend

For convenience, you can use the provided scripts in the root directory to run both the Laravel backend and Streamlit frontend:

- **Windows**: Run `run.bat` by double-clicking it or from the command line
- **Linux/Mac**: Run `