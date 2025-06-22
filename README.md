<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework.

You may also try the [Laravel Bootcamp](https://bootcamp.laravel.com), where you will be guided through building a modern Laravel application from scratch.

If you don't feel like reading, [Laracasts](https://laracasts.com) can help. Laracasts contains thousands of video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

## Laravel Sponsors

We would like to extend our thanks to the following sponsors for funding Laravel development. If you are interested in becoming a sponsor, please visit the [Laravel Partners program](https://partners.laravel.com).

### Premium Partners

- **[Vehikl](https://vehikl.com/)**
- **[Tighten Co.](https://tighten.co)**
- **[WebReinvent](https://webreinvent.com/)**
- **[Kirschbaum Development Group](https://kirschbaumdevelopment.com)**
- **[64 Robots](https://64robots.com)**
- **[Curotec](https://www.curotec.com/services/technologies/laravel/)**
- **[Cyber-Duck](https://cyber-duck.co.uk)**
- **[DevSquad](https://devsquad.com/hire-laravel-developers)**
- **[Jump24](https://jump24.co.uk)**
- **[Redberry](https://redberry.international/laravel/)**
- **[Active Logic](https://activelogic.com)**
- **[byte5](https://byte5.de)**
- **[OP.GG](https://op.gg)**

## Contributing

Thank you for considering contributing to the Laravel framework! The contribution guide can be found in the [Laravel documentation](https://laravel.com/docs/contributions).

## Code of Conduct

In order to ensure that the Laravel community is welcoming to all, please review and abide by the [Code of Conduct](https://laravel.com/docs/contributions#code-of-conduct).

## Security Vulnerabilities

If you discover a security vulnerability within Laravel, please send an e-mail to Taylor Otwell via [taylor@laravel.com](mailto:taylor@laravel.com). All security vulnerabilities will be promptly addressed.

## License

The Laravel framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).

# Resume Analysis and Job Fair Recommendation System

## 1. Overview

This project is a comprehensive web application designed to assist job seekers and job fair organizers. Key functionalities include:
*   Uploading and analyzing resumes to extract key information (skills, experience, education).
*   Allowing users to explore upcoming job fairs, view details, and get directions.
*   Providing personalized booth recommendations at job fairs based on resume analysis and job opening requirements.
*   Displaying interactive job fair maps with highlighted recommended booths.

## 2. System Architecture

The system utilizes a dual-stack architecture, separating backend logic from the frontend user interface for clarity, scalability, and maintainability.

![System Architecture Diagram Placeholder](https://via.placeholder.com/800x400.png?text=High-Level+Architecture:+Streamlit+Frontend+<-->+API+<-->+Laravel+Backend+DB)
*(Note: Replace the placeholder above with an actual architecture diagram if available)*

### 2.1. Backend: Laravel (PHP Framework)

*   **Purpose**: Serves as the central API and business logic hub. It handles data persistence, user authentication, core processing tasks, and exposes a RESTful API for the frontend.
*   **Language/Framework**: PHP 8.3+ / Laravel Framework 11.x
*   **Key Responsibilities**:
    *   User authentication and management (via Laravel Sanctum for API tokens).
    *   Database interactions (CRUD operations for users, resumes, job fairs, job openings, etc.) using Eloquent ORM.
    *   Serving as the API endpoint for the Streamlit frontend.
    *   Initial processing of uploaded resumes (e.g., storing the file).
    *   Managing job fair data, including map image paths and location details.
    *   Potentially housing core recommendation logic or delegating to Python scripts.
*   **Core Libraries & Components**:
    *   `laravel/framework`: Core framework.
    *   `laravel/sanctum`: API authentication.
    *   `smalot/pdfparser`: For parsing PDF files (likely for initial processing or if PHP handles some text extraction).
    *   Eloquent ORM: Database interaction.
    *   Artisan Console: Command-line interface for development tasks.

### 2.2. Frontend: Streamlit (Python Framework)

*   **Purpose**: Provides an interactive and data-centric user interface for job seekers and potentially organizers/admins.
*   **Language/Framework**: Python / Streamlit Framework (1.28.0+)
*   **Key Responsibilities**:
    *   User interface for resume upload, job fair exploration, viewing recommendations.
    *   Making API calls to the Laravel backend to fetch and send data.
    *   Displaying job fair details, maps, and directions.
    *   Rendering personalized booth recommendations.
    *   Handling complex data processing and analysis tasks related to resumes and matching, leveraging Python's extensive NLP and ML libraries.
*   **Core Libraries & Components**:
    *   `streamlit`: Web application framework.
    *   `requests`: For making HTTP API calls to the Laravel backend.
    *   **Document Processing**: `PyPDF2`, `pdfplumber`, `python-docx` (for extracting text from resumes in PDF and DOCX formats).
    *   **NLP/ML**:
        *   `spacy`: For Named Entity Recognition (NER) to extract skills, experience, education, etc., from resume text.
        *   `nltk`: Natural Language Toolkit, for additional NLP tasks or resources.
        *   `scikit-learn`: For potential text classification, feature extraction, or more advanced recommendation algorithms.
    *   **Mapping & Geolocation**:
        *   `folium` & `streamlit-folium`: Displaying interactive maps.
        *   `streamlit_geolocation`: Getting user's current location for directions.
        *   (Indirectly) Geoapify API: Used by the backend (or via frontend passthrough) for static maps and route directions.
    *   **OCR & Image Processing**:
        *   `pytesseract` & `pdf2image`: For OCR on job fair map images to identify booth numbers/text.
        *   `opencv-python` & `Pillow (PIL)`: For image manipulation, preprocessing for OCR, and highlighting booths on maps.
    *   `pandas`, `numpy`: Data manipulation.
    *   `streamlit-authenticator`: For frontend authentication UI, coordinating with the Laravel backend.

### 2.3. Interaction between Backend and Frontend

1.  **User Actions (Streamlit)**: User interacts with the Streamlit UI (e.g., uploads a resume, selects a job fair).
2.  **API Calls (Streamlit -> Laravel)**: Streamlit makes authenticated API requests to the Laravel backend, sending data (e.g., resume file) or requesting information (e.g., job fair list, recommendations for a resume).
3.  **Processing (Laravel & Python Scripts/Streamlit)**:
    *   Laravel handles API request validation, database operations, and may trigger Python scripts (or rely on Streamlit to perform) for computationally intensive tasks like NER.
    *   The Streamlit environment directly uses its Python libraries (spaCy, scikit-learn, OCR tools) for detailed resume analysis and map processing.
4.  **API Responses (Laravel -> Streamlit)**: Laravel returns data in JSON format to Streamlit.
5.  **UI Update (Streamlit)**: Streamlit processes the API response and updates the user interface dynamically.

## 3. Core Functionalities & Technical Approach

### 3.1. Resume Analysis

*   **Text Extraction**: Resumes (PDF, DOCX) are processed using libraries like `pdfplumber`, `PyPDF2`, and `python-docx` to extract raw text.
*   **Named Entity Recognition (NER)**: `spaCy` (and potentially `NLTK`) models are used to identify and categorize key information from the extracted text, such as:
    *   Skills (technical, soft)
    *   Years of Experience
    *   Educational Qualifications (degrees, CGPA)
    *   Company Names, Job Titles
*   This structured data forms the basis for matching resumes with job openings.

### 3.2. Job Fair Exploration & Directions

*   Job fair data (details, location, map paths) is fetched from the Laravel backend.
*   Static maps are displayed using Geoapify.
*   Interactive directions are provided by:
    1.  Getting user's current location (`streamlit_geolocation`).
    2.  Fetching route data from Geoapify (via an API call).
    3.  Displaying the route on an interactive `folium` map.

### 3.3. Personalized Booth Recommendations

*   A hybrid approach is likely used:
    *   **ML-Extracted Features**: NER provides structured data from resumes.
    *   **Rule-Based Matching/Scoring**: The system compares the extracted resume features against the requirements of job openings at a selected fair using a set of predefined rules or a scoring algorithm. This determines which booths/openings are most relevant.

### 3.4. Map Highlighting

*   For recommended booths, the system attempts to highlight them on the job fair's floor plan.
*   **OCR**: If booth numbers are part of the map image, `pytesseract` (OCR) is used to read text from the map image.
*   **Image Processing**: `OpenCV` and `Pillow` are used to process the map image, locate the identified booth numbers (from OCR or other data), and draw visual highlights.

## 4. Setup and Installation (High-Level)

Detailed setup instructions should be added here. Generally, it involves:

### 4.1. Backend (Laravel)
1.  Clone the repository.
2.  Install PHP dependencies: `composer install`
3.  Configure environment: Copy `.env.example` to `.env` and set database, API keys, etc.
4.  Run database migrations: `php artisan migrate --seed`
5.  Link storage: `php artisan storage:link`
6.  Serve the application: `php artisan serve`

### 4.2. Frontend (Streamlit)
1.  Navigate to the `streamlit_frontend` directory.
2.  Install Python dependencies: `pip install -r requirements.txt`
3.  Download spaCy model: `python -m spacy download en_core_web_sm`
4.  (If applicable) Set up Tesseract OCR engine.
5.  Configure environment: Create `.env` in `streamlit_frontend` for API base URL, etc.
6.  Run the Streamlit app: `streamlit run app.py` (or your main Streamlit script)

## 5. Key Technologies Summary

*   **Backend**: PHP, Laravel
*   **Frontend**: Python, Streamlit
*   **Database**: Relational DB (e.g., MySQL, PostgreSQL via Laravel)
*   **API**: RESTful, JSON
*   **Authentication**: Laravel Sanctum, Streamlit Authenticator
*   **Document Parsing**: `smalot/pdfparser` (PHP), `PyPDF2`, `pdfplumber`, `python-docx` (Python)
*   **NLP/ML**: `spaCy`, `NLTK`, `scikit-learn`
*   **OCR**: `pytesseract`, `pdf2image`
*   **Image Processing**: `OpenCV`, `Pillow`
*   **Mapping**: `Geoapify` (API), `folium`, `streamlit-folium`, `streamlit_geolocation`
*   **Data Handling (Python)**: `pandas`, `numpy`

---
This README provides a foundational understanding of the system. For more detailed information, please refer to the respective codebases and specific documentation for the libraries used.
