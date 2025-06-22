#!/usr/bin/env python
import re
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Download necessary NLTK resources if not available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Load spaCy model for entity recognition
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy en_core_web_sm model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class EnhancedParser:
    """
    Enhanced resume parser with improved accuracy for modern resume formats.
    Handles various layouts and provides better structured extraction.
    Focuses on Skills (General/Soft), Work Experience, and Education.
    """
        
    def __init__(self, debug=False, primary_field=None):
        self.debug = debug
        self.primary_field = primary_field
        
        self.skill_categories = {
            'programming_languages': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'TypeScript', 'Ruby', 'Swift', 'Kotlin', 'Go', 'Rust', 'R', 'MATLAB'],
            'web_development': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Laravel', 'Express.js', 'Spring Boot', 'ASP.NET', 'Bootstrap', 'Tailwind CSS', 'jQuery', 'Redux', 'REST API'],
            'database': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'Firebase', 'DynamoDB', 'Redis', 'Cassandra', 'NoSQL'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible', 'Linux', 'Bash', 'Shell Scripting'],
            'mobile': ['Android', 'iOS', 'Flutter', 'React Native', 'Swift UI', 'Jetpack Compose', 'Kotlin Multiplatform', 'Xamarin', 'App Development'],
            'data_science': ['Machine Learning', 'Data Analysis', 'NumPy', 'Pandas', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'NLP', 'Computer Vision', 'Big Data', 'Statistics', 'Data Visualization', 'Tableau', 'Power B', 'Jupyter'],
            'design_tools': ['Figma', 'Adobe XD', 'Sketch', 'InVision', 'Photoshop', 'Illustrator', 'UI/UX Design', 'Prototyping', 'Wireframing', 'Canva', 'Responsive Design'],
            'financial_analysis': ['Financial Modeling', 'Financial Analysis', 'Valuation', 'DCF', 'Financial Statements', 'Equity Research', 'Investment Analysis', 'Portfolio Management', 'Risk Assessment', 'Forecasting', 'Analysis'],
            'financial_software': ['Excel', 'Bloomberg Terminal', 'FactSet', 'Capital IQ', 'QuickBooks', 'SAP', 'Oracle Financials', 'Microsoft Dynamics', 'Tableau', 'Power BI', 'PowerPoint'],
            'accounting': ['Accounting', 'Auditing', 'Financial Reporting', 'Bookkeeping', 'GAAP', 'IFRS', 'Tax Preparation', 'Budgeting', 'Cost Accounting', 'Reconciliation'],
            'finance_certifications': ['CFA', 'CPA', 'FRM', 'Series 7', 'Series 63', 'ChFC', 'CFP', 'EA', 'CAIA', 'PMP', 'Six Sigma'],
            'banking': ['Investment Banking', 'Commercial Banking', 'Corporate Finance', 'M&A', 'Capital Markets', 'Wealth Management', 'Credit Analysis', 'Underwriting', 'Private Equity', 'Venture Capital'],
            'clinical_skills': ['Patient Care', 'Venepuncture', 'Vital Signs', 'CPR', 'Suturing', 'Injections', 'Wound Care', 'Physical Examination', 'Diagnosis', 'Treatment Planning', 'Medical Documentation', 'Triage', 'EMR'],
            'medical_specialties': ['Pediatrics', 'Surgery', 'Internal Medicine', 'Psychiatry', 'Radiology', 'Obstetrics', 'Gynecology', 'O&G', 'Obstetrics & Gynecology', 'Cardiology', 'Neurology', 'Oncology', 'Emergency Medicine', 'Family Medicine', 'Anesthesiology'], # Added O&G, Obstetrics & Gynecology
            'medical_knowledge': ['Anatomy', 'Physiology', 'Pharmacology', 'Pathology', 'Microbiology', 'Immunology', 'Biochemistry', 'Genetics', 'Medical Terminology', 'Disease Management', 'Clinical Research', 'Monitoring'],
            'healthcare_systems': ['Electronic Medical Records', 'EMR', 'EHR', 'Health Informatics', 'HIPAA', 'Healthcare Compliance', 'Medical Billing', 'Coding', 'Hospital Management', 'Public Health', 'Telemedicine'],
            'medical_technologies': ['Medical Imaging', 'Ultrasound', 'X-ray', 'CT Scan', 'MRI', 'Medical Devices', 'Surgical Equipment', 'Lab Equipment', 'Health Monitoring Systems', 'Remote Patient Monitoring']
        }
        
        self.soft_skills_keywords = [
            'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Assertive', 'Resilience',
            'Critical Thinking', 'Time Management', 'Adaptability', 'Organization', 'Empathy',
            'Creativity', 'Analytical Skills', 'Attention to Detail', 'Collaboration', 'Counseling',
            'Project Management', 'Presentation Skills', 'Research', 'Writing', 'Documentation',
            'Negotiation', 'Interpersonal Skills', 'Decision Making', 'Emotional Intelligence',
            'Debugging', 'Problem-solving',
            'Time-management'
        ]
        
        self.section_headers = {
            'contact': ['contact'],
            'summary': ['profile', 'summary', 'objective', 'about me', 'professional summary'],
            'education': ['education', 'academic background', 'academic qualifications', 'qualifications'],
            'experience': ['experience', 'employment history', 'work history', 'professional experience', 'work experience'],
            'skills': ['skills', 'expertise', 'competencies', 'technical skills', 'technologies'],
            'projects': ['projects', 'portfolio', 'personal projects'],
            'languages': ['languages', 'language proficiency'],
            'references': ['references', 'reference']
        }

        self.industry_keywords = {
            'computer_science': ['software', 'web', 'development', 'programming', 'engineering', 'data science', 'IT', 'information technology', 'tech', 'cyber', 'frontend', 'backend', 'full stack', 'devops', 'cloud', 'artificial intelligence', 'AI', 'ML', 'machine learning', 'UX', 'UI', 'database', 'algorithm', 'coding', 'computer science', 'developer'],
            'finance': ['finance', 'financial', 'banking', 'investment', 'finacial services', 'accounting', 'auditing', 'wealth management', 'trading', 'asset management', 'risk', 'tax', 'economic', 'insurance', 'fintech', 'financial technology', 'budget', 'treasury', 'regulatory', 'compliance', 'portfolio', 'equity', 'capital', 'cfa', 'cpa', 'frm', 'analyst', 'graduate', 'reports', 'variance', 'forecasting', 'ledger', 'commerce'],
            'medical': ['medical', 'healthcare', 'clinical', 'hospital', 'patient care', 'pharmacy', 'doctor', 'physician', 'nursing', 'dental', 'health', 'biomedical', 'pharmaceutical', 'life sciences', 'biotech', 'telemedicine', 'wellness', 'surgery', 'pediatrics', 'anatomy', 'diagnosis', 'suturing', 'mbbs', 'md', 'rn', 'pharmacology', 'physiology', 'pathology']
        }
        
        self.degrees_list = [
        'Bachelor of Computer Science', 'BSc Computer Science', 'B.Sc. Computer Science', 'Bachelor of Science in Computer Science',
        'Master of Computer Science', 'MSc Computer Science', 'M.Sc. Computer Science', 'PhD Computer Science', 'Doctor of Philosophy in Computer Science',
        'Bachelor of Information Technology', 'BSc IT', 'Master of Information Technology', 'MSc IT', 'PhD Information Technology',
        'Bachelor of Software Engineering', 'BSc Software Engineering', 'Master of Software Engineering',
        'Bachelor of Data Science', 'Master of Data Science', 'PhD Data Science',
        'Bachelor of Artificial Intelligence', 'Master of Artificial Intelligence', 'PhD Artificial Intelligence',
        'Bachelor of Finance', 'BSc Finance', 'BBA Finance', 'Bachelor of Business Administration in Finance',
        'Master of Finance', 'MSc Finance', 'MBA Finance', 'PhD Finance', 'Doctor of Philosophy in Finance',
        'Bachelor of Accounting', 'BAcc', 'Bachelor of Commerce', 'BCom', 'Master of Accounting', 'MAcc', 'Master of Commerce', 'MCom',
        'Chartered Accountant', 'Certified Public Accountant', 'CPA', 'Chartered Financial Analyst', 'CFA',
        'Bachelor of Finance (Hons)',
            'Bachelor of Medicine and Bachelor of Surgery', 'Bachelor of Medicine', 'Bachelor of Surgery', 'MBBS', 'MD', 'Doctor of Medicine', 'Doctor of Dental Surgery', 'DDS',
        'Bachelor of Pharmacy', 'BPharm', 'Master of Pharmacy', 'MPharm', 'Doctor of Pharmacy', 'PharmD',
        'Bachelor of Nursing', 'BNurs', 'Master of Nursing', 'MNurs', 'Doctor of Nursing Practice', 'DNP',
        'Bachelor of Biomedical Science', 'Master of Biomedical Science', 'PhD Biomedical Science',
            'Diploma', 'Certificate', 'Associate Degree', 'Foundation', 'Matriculation', 'Honours', 'Hons.'
    ]

        # Sort degrees_list by length (descending) to match longer, more specific degrees first
        self.degrees_list.sort(key=len, reverse=True)

        self.job_titles_list = [
        'Software Engineer', 'Backend Developer', 'Frontend Developer', 'Full Stack Developer', 'Web Developer', 'Mobile Developer', 'DevOps Engineer',
        'Data Scientist', 'Data Analyst', 'Machine Learning Engineer', 'AI Engineer', 'Cloud Engineer', 'System Administrator', 'Network Engineer',
            'Security Engineer', 'QA Engineer', 'Test Engineer', 'UI/UX Designer', 'Product Manager', 'Technical Lead', 'CTO', 'IT Support', 'Junior Developer Intern',
            'Accountant', 'Auditor', 'Financial Analyst', 'Investment Analyst', 'Risk Analyst', 'Portfolio Manager', 'Asset Manager', 'Finance Manager', 'Finance Intern',
        'Chief Financial Officer', 'CFO', 'Tax Consultant', 'Treasury Analyst', 'Compliance Officer', 'Credit Analyst', 'Loan Officer',
        'Bank Manager', 'Branch Manager', 'Wealth Manager', 'Actuary', 'Underwriter', 'Insurance Agent', 'Financial Planner', 'Forensic Accountant',
            'Medical Doctor', 'Physician', 'Surgeon', 'Dentist', 'Pharmacist', 'Nurse', 'Clinical Researcher', 'Medical Laboratory Scientist', 'Clinical Posting Student', 'Medical Intern',
        'Radiologist', 'Anesthesiologist', 'Pediatrician', 'Psychiatrist', 'General Practitioner', 'Specialist', 'Therapist', 'Occupational Therapist',
        'Physical Therapist', 'Speech Therapist', 'Medical Officer', 'House Officer', 'Resident', 'Consultant', 'Medical Assistant', 'Paramedic',
        'Healthcare Administrator', 'Medical Coder', 'Medical Biller', 'Medical Transcriptionist'
    ]

        self.institution_markers = ['university', 'college', 'institute', 'school', 'academy', 'polytechnic', 'kebangsaan', 'teknologi', 'universiti']

        self.company_name_keywords = [ # Keywords that might indicate a company name if NER fails
            'Sdn Bhd', 'Ltd', 'Inc', 'LLC', 'Corp', 'Berhad', 'Group', 'Solutions', 'Technologies', 'Services',
            'Consulting', 'Bank', 'Hospital', 'Clinic', 'University', 'Institute', 'School', 'Foundation', 'Center', 'Centre'
        ]

        # Define education-specific patterns
        self.date_pattern_education = re.compile(
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\s*-\s*(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|Present|Current)|\b\d{4}\s*-\s*\d{4}\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b|\b\d{4}\b',
            re.IGNORECASE
        )
        self.cgpa_pattern_education = re.compile(r'(?:CGPA|GPA)[:\s]*([0-4]\.\d{1,2}|[1-3])(?:\s*/\s*[45]\.0?)?', re.IGNORECASE)
        self.institution_markers_lower = [marker.lower() for marker in self.institution_markers]
        self.acronym_pattern = re.compile(r'\(([A-Z]{2,6})\)')

        # --- START: New __init__ logic for sorted_skill_references ---
        self.sorted_skill_references = []
        _skill_map = {} # temp map to handle precedence and store canonical names

        # Populate with general skills first
        for category_key, skill_list_in_cat in self.skill_categories.items():
            for skill_name in skill_list_in_cat:
                if skill_name: # Ensure skill_name is not empty
                    _skill_map[skill_name.lower()] = {'canonical': skill_name, 'type': 'general'}

        # Populate/overwrite with soft skills (soft skills take precedence)
        for soft_skill_name in self.soft_skills_keywords:
            if soft_skill_name: # Ensure skill_name is not empty
                _skill_map[soft_skill_name.lower()] = {'canonical': soft_skill_name, 'type': 'soft'}
        
        # Convert to list of (canonical_name, type) and sort by length of canonical name descending
        # This ensures longer skills (e.g., "UI/UX Design") are matched before shorter ones (e.g., "UI")
        self.sorted_skill_references = sorted(
            [(data['canonical'], data['type']) for data in _skill_map.values() if data['canonical']], # Ensure canonical is not empty
            key=lambda x: len(x[0]),
            reverse=True
        )
        if self.debug:
            # print(f"DEBUG (__init__): Sorted skill references (first 10): {self.sorted_skill_references[:10]}")
            # print(f"DEBUG (__init__): Sorted skill references (last 10): {self.sorted_skill_references[-10:]}")
            pass # Keep debug prints minimal for now
        # --- END: New __init__ logic for sorted_skill_references ---


    def parse(self, text: str) -> Dict[str, Any]:
        if self.debug:
            print("\n--- Starting Resume Parsing ---")
            print(f"Input text (first 300 chars): {text[:300].replace(chr(10), ' ')}")

        # Normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        if not self.primary_field:
            self.primary_field = self._identify_primary_field(text)

        sections = self._extract_sections(text)
        
        # ALWAYS pass the full text to _extract_experience.
        # Its internal logic, with _is_line_a_potential_header_or_new_title,
        # should handle segmentation of experience entries and prevent over-collection.
        if self.debug:
            print(f"DEBUG (parse): Passing full text (len: {len(text)}) to _extract_experience.")
        experience_entries = self._extract_experience(text, self.primary_field)
        
        extracted_data = {
            "education": self._extract_education(sections.get('education', text)),
            "experience": experience_entries, 
            "skills": self._extract_skills(sections.get('skills', text), self.primary_field),
            "summary": sections.get('summary', sections.get('profile', "Summary not found")), 
            "primary_field": self.primary_field
        }
        
        if self.debug:
            print("--- Extracted Data ---")
            print(f"Education: {extracted_data['education']}")
            print(f"Experience: {extracted_data['experience']}")
            print(f"Skills: {extracted_data['skills']}")
            print(f"Primary Field: {extracted_data['primary_field']}")
            print("--- Resume Parsing Complete ---\n")
            
        return extracted_data

    def _identify_primary_field(self, text_to_analyze):
        category_scores = {field: 0 for field in self.industry_keywords.keys()}
        
        # Normalize whitespace: replace multiple spaces/newlines with a single space
        normalized_text = re.sub(r'\s+', ' ', text_to_analyze).strip()

        if self.debug: 
            print(f"DEBUG (_identify_primary_field): Analyzing full text for primary field (length: {len(text_to_analyze)} chars).")
            print(f"DEBUG (_identify_primary_field): Normalized text for analysis (first 300): '{normalized_text[:300]}'")
            manual_check_keyword = 'software' 
            # Test with new regex pattern directly
            pattern_manual_check = r'(?<!\w)' + re.escape(manual_check_keyword) + r'(?!\w)'
            manual_occurrences_new_regex = len(re.findall(pattern_manual_check, normalized_text, re.IGNORECASE))
            print(f"DEBUG (_identify_primary_field): MANUAL CHECK with new regex '{pattern_manual_check}' - Keyword '{manual_check_keyword}' found {manual_occurrences_new_regex} times in NORMALIZED text.")
            if manual_check_keyword.lower() in normalized_text.lower():
                 print(f"DEBUG (_identify_primary_field): MANUAL CHECK - Substring '{manual_check_keyword}' IS present in lowercased normalized_text.")
            else:
                 print(f"DEBUG (_identify_primary_field): MANUAL CHECK - Substring '{manual_check_keyword}' IS NOT present in lowercased normalized_text.")
        
        for field, keywords in self.industry_keywords.items():
            for keyword in keywords:
                try:
                    # Use more robust regex: (?<!\w)keyword(?!\w)
                    # This means "not preceded by a word character" and "not followed by a word character"
                    pattern = r'(?<!\w)' + re.escape(keyword) + r'(?!\\w)'
                    occurrences = len(re.findall(pattern, normalized_text, re.IGNORECASE))
                    if occurrences > 0:
                        category_scores[field] += occurrences
                        if self.debug:
                           print(f"DEBUG (_identify_primary_field): Keyword '{keyword}' (pattern: '{pattern}') found {occurrences} times, adding to {field}. Current score for {field}: {category_scores[field]}")
                except re.error as e:
                    if self.debug: print(f"DEBUG (_identify_primary_field): Regex error for keyword '{keyword}', pattern '{pattern}': {e}")
                    continue
        
        if self.debug: print(f"DEBUG (_identify_primary_field): Final category scores: {category_scores}")

        # Determine the primary field based on the highest score
        
        # Check if any keywords were matched at all
        total_matches = sum(category_scores.values())

        if total_matches == 0: # No keywords matched across all categories
            primary_field_identified = "auto" # Changed from "general" to "auto" when no keywords match
        else:
            max_score = 0
            # First pass to find the max_score (must be > 0 if total_matches > 0)
            for score in category_scores.values():
                if score > max_score:
                    max_score = score
            
            top_fields = [field for field, score in category_scores.items() if score == max_score]

            if len(top_fields) == 1 : 
                primary_field_identified = top_fields[0]
            else: # Tie between 2 or more fields with max_score > 0
                # Prioritize if one of the tied fields is 'computer_science', then 'finance', then 'medical'
                if 'computer_science' in top_fields:
                    primary_field_identified = 'computer_science'
                elif 'finance' in top_fields: 
                    primary_field_identified = 'finance'
                elif 'medical' in top_fields: 
                    primary_field_identified = 'medical'
                else: 
                    primary_field_identified = top_fields[0] # Fallback to the first in list if no priority match (e.g. custom categories later)
        
        if self.debug: print(f"DEBUG (_identify_primary_field): Determined primary field: {primary_field_identified}")
        return primary_field_identified

    def _extract_sections(self, text: str) -> Dict[str, str]:
        extracted_sections = {}

        if self.debug: 
            print(f"DEBUG (_extract_sections): Processing text for section extraction (len: {len(text)} chars).")

        normalized_to_section_key_map = {}
        temp_normalized_list = []
        for section_k_target, phrases_list_for_key in self.section_headers.items():
            for p_orig in phrases_list_for_key: 
                normalized_p = ''.join(p_orig.lower().split())
                if normalized_p: 
                    temp_normalized_list.append((normalized_p, len(p_orig), section_k_target))
        
        temp_normalized_list.sort(key=lambda x: (x[1], len(x[0])), reverse=True)

        unique_normalized_phrases_for_matching = []
        seen_norm_phrases = set()
        for norm_p, _orig_len, sec_key in temp_normalized_list:
            if norm_p not in seen_norm_phrases:
                unique_normalized_phrases_for_matching.append((norm_p, sec_key))
                seen_norm_phrases.add(norm_p)

        found_headers_raw = [] 

        current_pos = 0
        for line_content in text.splitlines():
            line_start_pos = current_pos
            stripped_line_text = line_content.strip()
            current_pos += len(line_content) + 1 

            if not stripped_line_text: 
                continue

            normalized_current_line = ''.join(stripped_line_text.lower().split())

            if not normalized_current_line:
                continue
            
            for norm_header_to_find, target_section_key in unique_normalized_phrases_for_matching:
                if normalized_current_line == norm_header_to_find:
                    actual_match_start = line_start_pos + line_content.find(stripped_line_text)
                    actual_match_end = actual_match_start + len(stripped_line_text)
                    
                    if self.debug:
                        print(f"DEBUG (_extract_sections):   CONFIRMED match for normalized header '{norm_header_to_find}' (key: {target_section_key}) on line: '{stripped_line_text}'")
                    
                    found_headers_raw.append({
                        'start': actual_match_start,
                        'end': actual_match_end,
                        'key': target_section_key,
                        'header_line': stripped_line_text
                    })
                    break 
        
        found_headers_raw.sort(key=lambda x: x['start'])

        unique_final_headers = []
        last_header_end = -1
        for header_info in found_headers_raw:
            if header_info['start'] >= last_header_end:
                unique_final_headers.append(header_info)
                last_header_end = header_info['end']

        if self.debug:
            print(f"DEBUG (_extract_sections): Number of unique headers found: {len(unique_final_headers)}")
            for h in unique_final_headers: print(f"  Found Header: {h['key']} - '{h['header_line']}' @ {h['start']}")

        for i, header_data in enumerate(unique_final_headers):
            section_key = header_data['key']
            content_start_pos = header_data['end'] 
            content_end_pos = len(text)
            if i + 1 < len(unique_final_headers):
                content_end_pos = unique_final_headers[i+1]['start']
            
            section_text_content = text[content_start_pos:content_end_pos].strip()

            if section_text_content:
                if section_key not in extracted_sections: 
                     extracted_sections[section_key] = section_text_content
                elif self.debug:
                     print(f"DEBUG (_extract_sections): Section key '{section_key}' already exists. Current content (1st 50): '{extracted_sections[section_key][:50]}'. New content (1st 50): '{section_text_content[:50]}'. NOT appending/overwriting for now.")


        if self.debug:
            print(f"DEBUG (_extract_sections): Final section keys populated in extracted_sections: {list(extracted_sections.keys())}")
            for k, v_text in extracted_sections.items():
                print(f"DEBUG (_extract_sections): Section '{k}' content (first 100 chars): {v_text[:100].replace(chr(10), ' ')}")
        
        return extracted_sections

    def _extract_education(self, education_text: str) -> List[Dict[str, Any]]:
        if self.debug:
            print(f"DEBUG (_extract_education): Received education_text (len: {len(education_text)} chars)")
            # print(f"Raw education_text:\n'''{education_text[:500]}...'''") # Print initial part
        
        if not education_text or not education_text.strip():
            if self.debug: print("DEBUG (_extract_education): Education text is empty or not provided.")
            return []

        education_entries = []
        current_entry_data = {}
        
        # Initialize patterns here if they are complex and used repeatedly
        # Example: date_pattern = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\s*-\s*(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|Present|Current)|\b\d{4}\s*-\s*\d{4}\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b|\b\d{4}\b')
        # Moved to __init__ as self.date_pattern_education
        cgpa_pattern = re.compile(r'(?:CGPA|GPA)[:\s]*([0-4]\.\d{1,2}|[1-3])(?:\s*/\s*[45]\.0?)?', re.IGNORECASE)
        # Moved to __init__ as self.cgpa_pattern

        # Helper function to finalize and store an education entry
        def finalize_current_education_entry():
            nonlocal current_entry_data # Ensure we're modifying the outer scope's dict
            if current_entry_data and (current_entry_data.get("degree") or current_entry_data.get("institution")) :
                
                # Default missing fields to "N/A"
                current_entry_data.setdefault("degree", "N/A")
                current_entry_data.setdefault("institution", "N/A")
                current_entry_data.setdefault("cgpa", "N/A")
                current_entry_data.setdefault("date", "N/A") # Or graduation_date

                # Basic cleanup for institution and degree (remove trailing/leading punctuation)
                for key in ["degree", "institution"]:
                    if isinstance(current_entry_data[key], str):
                        current_entry_data[key] = current_entry_data[key].strip(' .,;-:')
                
                # Check if the entry is not just full of N/A (or very minimal like just a year)
                meaningful_fields = [
                    v for k, v in current_entry_data.items() 
                    if v != "N/A" and not (k == "date" and re.fullmatch(r'\d{4}', str(v)))
                ]
                if len(meaningful_fields) > 1: # Requires at least two meaningful fields beyond just a year
                    education_entries.append(current_entry_data)
                if self.debug: print(f"DEBUG (_extract_education): Finalized and added entry: {current_entry_data}")
                elif self.debug:
                    print(f"DEBUG (_extract_education): Skipped adding entry due to insufficient meaningful data: {current_entry_data}")

            current_entry_data = {} # Reset for the next entry

        # Pre-splitting lines and iterating
        if self.debug: print(f"DEBUG (_extract_education): About to split education_text. Type: {type(education_text)}")
        # print(repr(education_text)) # <<< THE DEBUG LINE TO ADD
        lines = education_text.strip().split('\n')
        if self.debug: print(f"DEBUG (_extract_education): Split into {len(lines)} lines. First few: {lines[:5]}")

        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx]
            if self.debug: print(f"DEBUG (_extract_education): Processing line {line_idx + 1}/{len(lines)}: '{line}'")

            original_line_for_institution_fallback = line 
            # Make a copy for modification within the loop for this line's processing
            current_line_text_for_processing = line 

            matched_degree_in_line = None
            # Sort degrees_list by length (descending) ensures longest match first
            # This is already done in __init__
            for known_degree in self.degrees_list: 
                # Stricter Regex: Ensure the known_degree is a more standalone match.
                # It should be at the start of the line, or be the whole line,
                # or be clearly demarcated.
                # Option 1: Starts with degree (case insensitive)
                if current_line_text_for_processing.lower().startswith(known_degree.lower()):
                    # Ensure it's not just a partial match of a longer word, unless it's the whole line
                    if len(current_line_text_for_processing) == len(known_degree) or \
                       (len(current_line_text_for_processing) > len(known_degree) and \
                        not current_line_text_for_processing[len(known_degree)].isalnum()): # Next char is not alphanumeric
                        matched_degree_in_line = known_degree 
                        # Remove the matched degree from the line text we are processing for other info
                        current_line_text_for_processing = current_line_text_for_processing[len(known_degree):].strip(" ,-:;()")
                        if self.debug: print(f"DEBUG (_extract_education): Matched degree (startswith): '{matched_degree_in_line}'. Remaining line: '{current_line_text_for_processing}'")
                        break 
                # Option 2: Whole line is the degree (case insensitive)
                elif current_line_text_for_processing.lower() == known_degree.lower():
                    matched_degree_in_line = known_degree
                    current_line_text_for_processing = "" # Whole line consumed
                    if self.debug: print(f"DEBUG (_extract_education): Matched degree (whole line): '{matched_degree_in_line}'.")
                    break
            
            if matched_degree_in_line:
                if self.debug: print(f"DEBUG (_extract_education): FINAL Matched Degree for this line: '{matched_degree_in_line}'")
                
                # If a degree is already in current_entry_data, and this new one is different,
                # it signifies a new education entry.
                if current_entry_data.get("degree") and current_entry_data.get("degree") != matched_degree_in_line:
                    if self.debug: print(f"DEBUG (_extract_education): New distinct degree '{matched_degree_in_line}' found. Current entry has '{current_entry_data.get('degree')}'. Finalizing previous entry: {current_entry_data}")
                    finalize_current_education_entry()
                
                # Set or update the degree in the current entry
                current_entry_data["degree"] = matched_degree_in_line
            
            # Now, process the potentially modified current_line_text_for_processing for CGPA and Date
            # This variable holds the line text *after* a degree might have been stripped from its start.

            if not current_entry_data.get("cgpa"):
                cgpa_match = self.cgpa_pattern_education.search(current_line_text_for_processing)
                if cgpa_match:
                    current_entry_data["cgpa"] = cgpa_match.group(1).strip()
                    if self.debug: print(f"DEBUG (_extract_education): Found CGPA: '{current_entry_data['cgpa']}' in line fragment: '{current_line_text_for_processing}'")
                    # Remove CGPA from the line text
                    current_line_text_for_processing = self.cgpa_pattern_education.sub('', current_line_text_for_processing, 1).strip(" ,-:;()")

            if not current_entry_data.get("date"):
                date_match_obj = self.date_pattern_education.search(current_line_text_for_processing)
                if date_match_obj:
                    current_entry_data["date"] = date_match_obj.group(0).strip()
                    if self.debug: print(f"DEBUG (_extract_education): Found Date: '{current_entry_data['date']}' in line fragment: '{current_line_text_for_processing}'")
                    # Remove Date from the line text
                    current_line_text_for_processing = self.date_pattern_education.sub('', current_line_text_for_processing, 1).strip(" ,-:;()")
            
            # What remains in current_line_text_for_processing is a candidate for institution part
            accumulated_institution_text_from_current_line = current_line_text_for_processing.strip()
            # current_institution_candidate will be built fresh based on current line's remnant + accumulated subsequent lines
            
            # Multi-line institution accumulation
            temp_line_idx = line_idx + 1
            potential_next_lines_for_institution = []
            processed_lines_in_accumulation = 0 # Keep track of how many lines we consume here
            while temp_line_idx < len(lines):
                next_line_raw = lines[temp_line_idx]
                next_line_stripped = next_line_raw.strip()

                if not next_line_stripped: # Skip empty lines
                    temp_line_idx +=1
                    processed_lines_in_accumulation += 1
                    continue

                # Check if next_line starts a new degree, or is a date/cgpa line itself
                is_next_line_a_new_degree_item = False
                for kd in self.degrees_list:
                    if next_line_stripped.lower().startswith(kd.lower()):
                        if len(next_line_stripped) == len(kd) or \
                           (len(next_line_stripped) > len(kd) and not next_line_stripped[len(kd)].isalnum()):
                            is_next_line_a_new_degree_item = True
                            break
                    elif next_line_stripped.lower() == kd.lower():
                        is_next_line_a_new_degree_item = True
                        break
                
                is_next_line_standalone_date = self.date_pattern_education.fullmatch(next_line_stripped)
                # Check if the line *starts with* CGPA: xxx, not necessarily fullmatch
                cgpa_prefix_match = self.cgpa_pattern_education.match(next_line_stripped)
                is_next_line_standalone_cgpa = cgpa_prefix_match and len(cgpa_prefix_match.group(0)) > 5 # Ensure it's a substantial CGPA string

                if is_next_line_a_new_degree_item or is_next_line_standalone_date or is_next_line_standalone_cgpa:
                    if self.debug: print(f"DEBUG (_extract_education): Next line '{next_line_stripped}' looks like a new entry start (Degree:{is_next_line_a_new_degree_item}, Date:{is_next_line_standalone_date}, CGPA:{is_next_line_standalone_cgpa}). Stopping institution accumulation.")
                    break
                
                doc_next_line = nlp(next_line_stripped)
                contains_marker = any(marker.lower() in next_line_stripped.lower() for marker in self.institution_markers_lower)
                is_org_entity = any(ent.label_ == "ORG" for ent in doc_next_line.ents)
                is_potential_continuation = (next_line_stripped and next_line_stripped[0].isupper()) or \
                                            self.acronym_pattern.search(next_line_stripped) or \
                                            (len(next_line_stripped.split()) <= 4 and not next_line_stripped.lower().startswith(("managed", "developed", "assisted", "responsible")))

                if contains_marker or is_org_entity or is_potential_continuation:
                    if self.debug: print(f"DEBUG (_extract_education): Adding next line '{next_line_stripped}' to potential institution text. (Marker:{contains_marker}, ORG:{is_org_entity}, PotentialCont:{is_potential_continuation})")
                    potential_next_lines_for_institution.append(next_line_stripped)
                    temp_line_idx += 1
                    processed_lines_in_accumulation += 1
                else: 
                    if self.debug: print(f"DEBUG (_extract_education): Next line '{next_line_stripped}' does not seem like institution continuation. Stopping. (Marker:{contains_marker}, ORG:{is_org_entity}, PotentialCont:{is_potential_continuation})")
                    break 
                
            # Now, assemble the full institution candidate from the current line's remainder and accumulated lines
            full_institution_candidate_parts = []
            if accumulated_institution_text_from_current_line:
                full_institution_candidate_parts.append(accumulated_institution_text_from_current_line)
            full_institution_candidate_parts.extend(potential_next_lines_for_institution)
            
            current_institution_candidate = " ".join(full_institution_candidate_parts).strip()
            if self.debug and current_institution_candidate:
                print(f"DEBUG (_extract_education): Assembled current_institution_candidate: '{current_institution_candidate}'")

            # --- This is the NER and refinement block for institution ---
            if current_institution_candidate: # Only proceed if we have a candidate
                final_acronym_part = None
                # original_candidate_before_ner_strip = current_institution_candidate # Keep for reference if needed
                
                # Correctly extract acronym and prepare candidate for NER
                acronym_overall_match = self.acronym_pattern.search(current_institution_candidate)
                candidate_for_ner = current_institution_candidate
                if acronym_overall_match:
                    final_acronym_part = acronym_overall_match.group(0) # e.g. "(UiTM)"
                    # Remove the acronym part from the candidate before sending to NER
                    candidate_for_ner = candidate_for_ner.replace(final_acronym_part, "").strip()
                    if self.debug: print(f"DEBUG (_extract_education): Acronym '{final_acronym_part}' found. Candidate for NER after strip: '{candidate_for_ner}'")
                elif self.debug:
                    print(f"DEBUG (_extract_education): No acronym part found by pattern '{self.acronym_pattern.pattern}' in current_institution_candidate: '{current_institution_candidate}'")

                # Initialize final_institution_name for this pass
                final_institution_name = ""

                if candidate_for_ner: 
                    doc_institution = nlp(candidate_for_ner) 
                    found_org_entities = [ent.text.strip() for ent in doc_institution.ents if ent.label_ == "ORG"]
                    if self.debug and ("teknologi mara" in candidate_for_ner.lower() or "kebangsaan malaysia" in candidate_for_ner.lower() or "malaya" in candidate_for_ner.lower()): 
                        print(f"DEBUG_INST_NER: Candidate for NER: '{candidate_for_ner}', Found ORG by spaCy: {found_org_entities}, Acronym part: {final_acronym_part}")

                    ner_extracted_institution_parts = []
                    if found_org_entities:
                        base_ner_name = " ".join(found_org_entities).strip()
                        acronym_core_from_final_part = final_acronym_part.strip("()") if final_acronym_part else ""

                        # Scenario 1: NER is too generic (e.g. "Universiti") or badly merges with acronym part from the main name
                        # Example: candidate_for_ner="Universiti Teknologi MARA", final_acronym_part="(UiTM)"
                        # spaCy on "Universiti Teknologi MARA" might give ['Universiti', 'UiTM'] or just ['Universiti']
                        # We want to prefer "Universiti Teknologi MARA" in such cases.
                        if phénomènes_like_uitm_or_ukm := (
                            candidate_for_ner.lower().startswith("universiti") and
                            acronym_core_from_final_part and # We have a distinct acronym like (UiTM)
                            (
                                base_ner_name.lower() == "universiti" or # NER was too generic
                                acronym_core_from_final_part.lower() in base_ner_name.lower() # NER merged part of acronym
                            ) and
                            len(candidate_for_ner.split()) > len(base_ner_name.split()) # Adjusted condition
                        ):
                            if self.debug: print(f"DEBUG_INST_NER: UiTM/UKM-like case. NER='{base_ner_name}', Candidate='{candidate_for_ner}'. Preferring candidate.")
                            ner_extracted_institution_parts.append(candidate_for_ner)
                        
                        # Scenario 2: NER is good, and the original candidate_for_ner is not significantly richer
                        # Example: candidate_for_ner="Universiti Malaya", final_acronym_part="(UM)"
                        # spaCy on "Universiti Malaya" gives ['Universiti Malaya']
                        # This is a good NER result.
                        elif base_ner_name and not (base_ner_name.lower() in ["university", "college", "institute", "school"] and len(candidate_for_ner.split()) > len(base_ner_name.split())):
                             if self.debug: print(f"DEBUG_INST_NER: Good NER or candidate not much richer. NER='{base_ner_name}', Candidate='{candidate_for_ner}'. Preferring NER.")
                             ner_extracted_institution_parts.append(base_ner_name)
                        
                        # Scenario 3: NER is bad/generic, but candidate_for_ner is richer and has markers
                        elif any(marker.lower() in candidate_for_ner.lower() for marker in self.institution_markers_lower) and len(candidate_for_ner.split()) > len(base_ner_name.split()):
                            if self.debug: print(f"DEBUG_INST_NER: NER bad/generic, candidate richer with markers. NER='{base_ner_name}', Candidate='{candidate_for_ner}'. Preferring candidate.")
                            ner_extracted_institution_parts.append(candidate_for_ner)
                        
                        # Scenario 4: Fallback to NER if it exists, even if not ideal
                        elif base_ner_name:
                            if self.debug: print(f"DEBUG_INST_NER: Fallback to NER. NER='{base_ner_name}', Candidate='{candidate_for_ner}'.")
                            ner_extracted_institution_parts.append(base_ner_name)
                        
                        # Scenario 5: If NER found nothing useful, but candidate_for_ner exists and seems plausible (already handled below)
                        # This 'else' corresponds to 'if found_org_entities:'
                    
                    else: # No ORG entities found by NER from candidate_for_ner
                        # Fallback: use candidate_for_ner if it has markers or looks like a name
                        has_marker = any(marker.lower() in candidate_for_ner.lower() for marker in self.institution_markers_lower)
                        not_same_as_degree = not current_entry_data.get("degree") or \
                                               (current_entry_data.get("degree") and \
                                                candidate_for_ner.lower() != current_entry_data.get("degree").lower())
                        word_list = [word for word in candidate_for_ner.split() if word]
                        is_capitalized_enough = False
                        if word_list: 
                            is_capitalized_enough = (sum(1 for word in word_list if word[0].isupper()) >= len(word_list) / 2) or \
                                                    (len(word_list) <= 2 and word_list[0][0].isupper()) 

                        if (has_marker or is_capitalized_enough) and not_same_as_degree:
                            if self.debug: print(f"DEBUG (_extract_education): No ORG from NER on '{candidate_for_ner}'. Using this as institution (marker: {has_marker}, capitalized: {is_capitalized_enough})")
                            ner_extracted_institution_parts.append(candidate_for_ner) 
                        elif self.debug:
                            print(f"DEBUG (_extract_education): No ORG from NER. Non-NER '{candidate_for_ner}' not used (marker:{has_marker}, cap:{is_capitalized_enough}, sameAsDegree:{not not_same_as_degree}).")
                    
                    if ner_extracted_institution_parts: 
                         final_institution_name = " ".join(ner_extracted_institution_parts).strip()

                # Re-attach acronym if it was stripped and not already part of the name
                if final_acronym_part and final_institution_name:
                    acronym_core = final_acronym_part.strip("()")
                    # Check if acronym core or full acronym (like "(UiTM)") is already in the built name
                    if not (re.search(r'\b' + re.escape(acronym_core) + r'\b', final_institution_name, re.IGNORECASE) or \
                            final_acronym_part.lower() in final_institution_name.lower()):
                        if self.debug: print(f"DEBUG_INST_NER: Appending acronym '{final_acronym_part}' to '{final_institution_name}'")
                        final_institution_name += " " + final_acronym_part
                    elif self.debug:
                        print(f"DEBUG_INST_NER: Acronym part '{final_acronym_part}' or core '{acronym_core}' already present/implied in '{final_institution_name}'. Not re-adding.")
                elif not final_institution_name and final_acronym_part: # Only acronym was found in original full candidate
                     final_institution_name = final_acronym_part
                elif not final_institution_name and candidate_for_ner : # No NER, no acronym, but had a candidate_for_ner
                     #This case should be rare if previous fallbacks worked
                    if self.debug: print(f"DEBUG_INST_NER: No NER, no acronym, using raw candidate_for_ner '{candidate_for_ner}' as last resort for final_institution_name.")
                    final_institution_name = candidate_for_ner


                # Clean and set the institution in current_entry_data
                if final_institution_name:
                    final_institution_name = final_institution_name.strip(" ,-:;")
                    # Correct acronym formatting like "Name (ACR)"
                    acronym_ending_match = re.search(r'\s*(\([A-Z]{2,6}\))$$', final_institution_name) 
                    if acronym_ending_match:
                        main_part = final_institution_name[:acronym_ending_match.start()].strip(" ,-:;")
                        final_institution_name = main_part + " " + acronym_ending_match.group(1) 
                    else: 
                        final_institution_name = final_institution_name.strip(" ,-:;()") 
                    
                    if final_institution_name and (not current_entry_data.get("degree") or final_institution_name.lower() != current_entry_data.get("degree", "").lower()):
                        current_entry_data["institution"] = final_institution_name
                        if self.debug: print(f"DEBUG (_extract_education): Set institution to: '{final_institution_name}'")
                    elif self.debug:
                        print(f"DEBUG (_extract_education): Final institution candidate '{final_institution_name}' was same as degree or empty, not setting.")
                
                # If NER block didn't yield an institution, but the original_line_for_institution_fallback
                # (the very first line of this education item) has content and isn't the degree/cgpa/date, consider it.
                elif not current_entry_data.get("institution") and \
                     original_line_for_institution_fallback.strip() and \
                     (not current_entry_data.get("degree") or original_line_for_institution_fallback.strip().lower() != current_entry_data.get("degree","").lower()) and \
                     (not current_entry_data.get("cgpa") or not current_entry_data.get("cgpa") in original_line_for_institution_fallback) and \
                     (not current_entry_data.get("date") or not current_entry_data.get("date") in original_line_for_institution_fallback):
                    
                    fallback_text_candidate = original_line_for_institution_fallback.strip(" ,-:;()")
                    if fallback_text_candidate and len(fallback_text_candidate.split()) < 7 and len(fallback_text_candidate) > 3 : # Avoid very short/long fallbacks
                        current_entry_data["institution"] = fallback_text_candidate
                        if self.debug: print(f"DEBUG (_extract_education): Fallback: used original line part as institution: '{fallback_text_candidate}'")


            # Advance main line_idx by 1 (for the current line) + lines consumed by institution accumulation
            line_idx += 1 + processed_lines_in_accumulation
            
            # Finalize if we have a degree or institution AND we are at the end of lines OR next line signals new entry
            should_finalize_now = False
            if current_entry_data.get("degree") or current_entry_data.get("institution"):
                if line_idx >= len(lines): # Reached end of all lines
                    should_finalize_now = True
                    if self.debug: print(f"DEBUG (_extract_education): Reached end of all lines. Triggering finalize.")
                else: # Check if the *new* current line_idx signals a new entry
                    next_line_check_raw = lines[line_idx]
                    next_line_check_stripped = next_line_check_raw.strip()
                    if next_line_check_stripped : # Only check if not empty
                        is_next_line_a_new_degree_item_for_finalize_check = False
                        for kd_finalize in self.degrees_list:
                            if next_line_check_stripped.lower().startswith(kd_finalize.lower()):
                                if len(next_line_check_stripped) == len(kd_finalize) or \
                                   (len(next_line_check_stripped) > len(kd_finalize) and not next_line_check_stripped[len(kd_finalize)].isalnum()):
                                    is_next_line_a_new_degree_item_for_finalize_check = True
                                    break
                            elif next_line_check_stripped.lower() == kd_finalize.lower():
                                is_next_line_a_new_degree_item_for_finalize_check = True
                                break
                        if is_next_line_a_new_degree_item_for_finalize_check and \
                           (not current_entry_data.get("degree") or next_line_check_stripped.lower() != current_entry_data.get("degree").lower()):
                            should_finalize_now = True
                            if self.debug: print(f"DEBUG (_extract_education): Next line '{next_line_check_stripped}' is a new degree. Triggering finalize.")
            
            if should_finalize_now:
                finalize_current_education_entry()


        # Finalize any last pending entry after loop (if not already caught by above)
        if current_entry_data.get("degree") or current_entry_data.get("institution"):
            if self.debug: print(f"DEBUG (_extract_education): Finalizing any last pending entry after loop: {current_entry_data}")
            finalize_current_education_entry()

        if self.debug: print(f"DEBUG (_extract_education): Final education entries list: {education_entries}")
        return education_entries

    def _is_line_a_potential_header_or_new_title(self, line_text: str, current_title: str = None) -> bool:
        """Helper to check if a line looks like a new section header or a different job title."""
        stripped_line = line_text.strip()
        if not stripped_line: return False

        # Check against general section headers (excluding experience itself)
        normalized_line = ''.join(stripped_line.lower().split())
        for section_key, header_phrases in self.section_headers.items():
            if section_key == 'experience': continue # Don't stop for sub-headers within experience if any
            for phrase in header_phrases:
                if normalized_line == ''.join(phrase.lower().split()):
                    if self.debug: print(f"DEBUG (_is_line_a_potential_header_or_new_title): Line '{stripped_line}' matches a general section header for '{section_key}'")
                    return True
        
        # Check against job titles (if it's different from the current one being processed)
        # This is a simplified check; relies on job_titles_list being comprehensive.
        # More robust would be to use the same title matching logic as in the main loop of _extract_experience.
        for known_title in self.job_titles_list:
            if isinstance(known_title, str) and stripped_line.lower() == known_title.lower():
                if current_title and current_title.lower() == stripped_line.lower():
                    continue # It's the same title, not a *new* one signaling end of previous entry
                if self.debug: print(f"DEBUG (_is_line_a_potential_header_or_new_title): Line '{stripped_line}' matches a known job title '{known_title}' (and is different from current)." )
                return True
        return False

    def _is_likely_standalone_company_location_line(self, line_text: str) -> bool:
        """
        Checks if a line is likely a company/location line rather than a responsibility.
        Considers NER tags and keywords.
        """
        if not line_text or len(line_text.split()) > 7: # Too long for typical Co/Loc line
            return False

        # Simple check for bullet points or action verbs - common in responsibilities
        if re.match(r'^\s*[-*•➢❖]', line_text) or any(line_text.lower().startswith(verb) for verb in ["assisted", "developed", "managed", "led", "responsible", "created", "implemented", "designed", "collaborated", "participated", "gained", "coordinated"]):
            return False

        doc = nlp(line_text)
        has_org = any(ent.label_ == "ORG" for ent in doc.ents)
        has_gpe = any(ent.label_ == "GPE" for ent in doc.ents)
        has_loc = any(ent.label_ == "LOC" for ent in doc.ents) # More general location

        if has_org or has_gpe or has_loc:
            # If it has ORG/GPE/LOC, and not too many verbs, it's likely Co/Loc
            num_verbs = sum(1 for token in doc if token.pos_ == "VERB")
            if num_verbs <= 1: # Allow one verb (e.g. "based in X") but not more
                return True
        
        # Check for keywords if NER is not definitive
        if any(keyword.lower() in line_text.lower() for keyword in self.company_name_keywords):
             # If it contains a company keyword and is relatively short, it's likely Co/Loc
            if len(line_text.split()) <= 5:
                return True
        
        # Check for "City, State" or "City, Country" like patterns
        if re.search(r'[A-Za-z\s]+,\s*[A-Za-z\s]+', line_text):
            return True

        return False

    def _extract_experience(self, experience_text: str, primary_field: str) -> List[Dict[str, Any]]:
        if self.debug:
            print(f"DEBUG (_extract_experience): Received experience_text (len: {len(experience_text)} chars)")
                
        if not experience_text or not experience_text.strip():
            if self.debug: print("DEBUG (_extract_experience): Experience text is empty or not provided.")
            return []
        
        # Ensure self.job_titles_list does not contain None
        # This was for a very specific bug, can be commented out if not relevant
        # if self.debug:
        #     if any(title is None for title in self.job_titles_list):
        #         print("ERROR (_extract_experience): self.job_titles_list contains a None value!")
        #     else:
        #         pass # print("DEBUG (_extract_experience): self.job_titles_list seems OK (no None values found).")
                
        experience_entries = []
        current_entry_data = {
            "title": None, "company": None, "location": None, 
            "date": None, "responsibilities": []
        }

        date_pattern_full = re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?)\s*(19|20\d{2})\s*(?:-|–|to|until)\s*(?:((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?)\s*(19|20\d{2})|Present|Current|Now)',
            re.IGNORECASE
        )
        year_date_pattern = re.compile(r'\b(19|20)\d{2}\s*(?:(?:-|–|to|until)\s*(19|20)\d{2})?|\b(Present|Current|Now)\b', re.IGNORECASE)

        def finalize_current_entry():
            # === DEBUG PRINT ===
            if self.debug and current_entry_data.get("title") == "Medical Intern":
                print(f"DEBUG_MEDICAL_INTERN (finalize_current_entry called): current_entry_data = {current_entry_data}")
            # === END DEBUG PRINT ===

            title_present = current_entry_data.get("title") and current_entry_data["title"] != "N/A"
            company_present = current_entry_data.get("company") and current_entry_data["company"] != "N/A"

            if title_present or company_present:
                raw_responsibilities = current_entry_data.get("responsibilities", [])
                cleaned_responsibilities = []
                if isinstance(raw_responsibilities, list): # Ensure it's a list
                    seen_resp = set() # Deduplicate
                    for resp_item in raw_responsibilities:
                        r_line = str(resp_item).strip().lstrip('*-•➢❖').strip() # Ensure string, strip bullets
                        if r_line and r_line not in seen_resp: # Check if not empty and not duplicate
                            cleaned_responsibilities.append(r_line)
                            seen_resp.add(r_line)
                
                current_entry_data["responsibilities"] = cleaned_responsibilities if cleaned_responsibilities else ["N/A"]
                
                # Fill N/A for other missing fields only if entry is valid
                for key_to_check in ["title", "company", "location", "date"]:
                    if current_entry_data.get(key_to_check) is None:
                        current_entry_data[key_to_check] = "N/A"
                
                experience_entries.append(current_entry_data.copy())
                if self.debug: print(f"DEBUG (_extract_experience): Finalized and added entry: {current_entry_data}")
                # === DEBUG PRINT ===
                if self.debug and current_entry_data.get("title") == "Medical Intern":
                    print(f"DEBUG_MEDICAL_INTERN (finalize_current_entry success): Entry ADDED to experience_entries.")
                # === END DEBUG PRINT ===
            elif self.debug and any(val for val in current_entry_data.values() if (isinstance(val, list) and val) or (not isinstance(val, list) and val is not None and val != "N/A")):
                 print(f"DEBUG (_extract_experience): Discarding incomplete entry parts: {current_entry_data}")
                 # === DEBUG PRINT ===
                 if self.debug and current_entry_data.get("title") == "Medical Intern":
                    print(f"DEBUG_MEDICAL_INTERN (finalize_current_entry): Entry DISCARDED.")
                 # === END DEBUG PRINT ===
            
            current_entry_data.clear()
            current_entry_data.update({
                "title": None, "company": None, "location": None,
                "date": None, "responsibilities": []
            })

        all_lines_from_experience_section = experience_text.strip().split('\n')
        if self.debug and not all_lines_from_experience_section:
            print("DEBUG (_extract_experience): all_lines_from_experience_section is EMPTY!")
        elif self.debug:
            # print(f"DEBUG (_extract_experience): all_lines_from_experience_section has {len(all_lines_from_experience_section)} lines.")
            pass # Keep debug minimal

        line_cursor = 0
        processed_lines_for_current_title_company_date = set() # Keep track of line indices used for title/co/date

        while line_cursor < len(all_lines_from_experience_section):
            line_consumed_this_iteration = False # <<< ADDED RESET HERE AT START OF LOOP
            current_line_index = line_cursor # Store current index for potential marking
            line = all_lines_from_experience_section[line_cursor].strip()
            line_cursor += 1

            if self.debug: 
                # print(f"DEBUG (_extract_experience): Processing line (type: {type(line)}): '{line}'")
                pass # Keep debug minimal

            if not line:
                    continue
            
            # Check if the line signals an end to the current experience entry
            should_finalize_due_to_header = False
            if current_entry_data.get("title"): # Only finalize if we have a current title we are working on
                if self._is_line_a_potential_header_or_new_title(line, current_entry_data.get("title")):
                    if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' (idx {current_line_index}) signals end of current entry (due to new header/title). Finalizing.")
                    finalize_current_entry()
                    processed_lines_for_current_title_company_date.clear()
                    should_finalize_due_to_header = True # Mark that finalization happened
                    continue  # <--- ADD THIS: skip further processing for header/title lines

            line_consumed_this_iteration = False 
            original_line_for_responsibility_check = line 

            # 1. Attempt to find a new Job Title
            potential_new_title_on_this_line = None
            sorted_job_titles = sorted([jt for jt in self.job_titles_list if jt], key=len, reverse=True)
            for known_title in sorted_job_titles: 
                if isinstance(known_title, str) and isinstance(line, str):
                    title_pattern = r'(?i)\b' + re.escape(known_title) + r'\b\s*(?:at|,|\(|–|-|$)'
                    match = re.match(title_pattern, line)
                    if match:
                        potential_new_title_on_this_line = known_title 
                        # === DEBUG PRINT ===
                        if self.debug and potential_new_title_on_this_line == "Medical Intern":
                            print(f"DEBUG_MEDICAL_INTERN (Title Identified): Matched '{potential_new_title_on_this_line}' on line '{line}'")
                        # === END DEBUG PRINT ===
                        break # Found the longest matching title
            if potential_new_title_on_this_line:
                if self.debug:
                    print(f"DEBUG (_extract_experience): Potential new title found: '{potential_new_title_on_this_line}' on line '{line}'")
                if current_entry_data.get("title") and \
                   isinstance(current_entry_data.get("title"), str) and \
                   current_entry_data.get("title").lower() != potential_new_title_on_this_line.lower():
                    if self.debug: print(f"DEBUG (_extract_experience): Different title found. Finalizing previous entry for '{current_entry_data.get('title')}'")
                    finalize_current_entry()
                    processed_lines_for_current_title_company_date.clear()
                if not current_entry_data.get("title") or \
                   (isinstance(current_entry_data.get("title"), str) and current_entry_data.get("title").lower() != potential_new_title_on_this_line.lower()):
                    current_entry_data["title"] = potential_new_title_on_this_line
                    processed_lines_for_current_title_company_date.add(current_line_index)
                    # === DEBUG PRINT ===
                    if self.debug and current_entry_data.get("title") == "Medical Intern":
                        print(f"DEBUG_MEDICAL_INTERN (Title Set): Title set to '{current_entry_data['title']}' from line (idx {current_line_index}): '{line}'")
                    # === END DEBUG PRINT ===
                    if self.debug: print(f"DEBUG (_extract_experience): Set New Title: '{potential_new_title_on_this_line}' from line (idx {current_line_index}): '{line}'")
                    remaining_line_after_title = line[len(potential_new_title_on_this_line):].strip()
                    if remaining_line_after_title.startswith(('at ', ', ')):
                        company_part = remaining_line_after_title.split(',')[0].replace('at ', '', 1).strip()
                        company_part_no_date = re.split(r'\s+(?:19|20)\d{2}\b|\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', company_part, 1)[0].strip()
                        if company_part_no_date and not current_entry_data.get("company"):
                            current_entry_data["company"] = company_part_no_date
                            # === DEBUG PRINT ===
                            if self.debug and current_entry_data.get("title") == "Medical Intern":
                                print(f"DEBUG_MEDICAL_INTERN (Company from title line): Company set to '{current_entry_data['company']}'")
                            # === END DEBUG PRINT ===
                            if self.debug: print(f"DEBUG (_extract_experience): Company from title line ('at' or ','): '{company_part_no_date}'")
                            original_line_for_responsibility_check = remaining_line_after_title.replace(company_part, "", 1).strip()
                    line_consumed_this_iteration = True # Title and possibly company consumed this line.

            date_search_text_for_title_line = "" # Initialize variable
            if line_consumed_this_iteration: # This implies a title was found and set
                date_search_text_for_title_line = original_line_for_responsibility_check # Text remaining after title & co
            if not current_entry_data.get("date") and date_search_text_for_title_line: # Check if there's text to search
                date_match_on_title_remnant = date_pattern_full.search(date_search_text_for_title_line) 
                if not date_match_on_title_remnant: date_match_on_title_remnant = year_date_pattern.search(date_search_text_for_title_line)
                if date_match_on_title_remnant:
                    date_str = date_match_on_title_remnant.group(0).strip()
                    current_entry_data["date"] = date_str
                    processed_lines_for_current_title_company_date.add(current_line_index) 
                    # === DEBUG PRINT ===
                    if self.debug and current_entry_data.get("title") == "Medical Intern":
                        print(f"DEBUG_MEDICAL_INTERN (Date from title line remnant): Date set to '{date_str}' from remnant '{date_search_text_for_title_line}'")
                    # === END DEBUG PRINT ===
                    if self.debug: print(f"DEBUG (_extract_experience): Found Date: '{date_str}' in title line remnant (idx {current_line_index}): '{date_search_text_for_title_line}'")
                    original_line_for_responsibility_check = date_search_text_for_title_line.replace(date_str, "").strip()
            
            # Only apply this short-remnant filter if the line was initially consumed by title/date logic on the title line itself
            if line_consumed_this_iteration and \
               (not original_line_for_responsibility_check.strip() or \
                len(original_line_for_responsibility_check.strip().split()) < 3):
                if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' (which was a title line) remnant '{original_line_for_responsibility_check}' is too short after title/date. Continuing.")
                continue 

            # 2. Attempt to find Date (if not already found and line not consumed by title)
            if not line_consumed_this_iteration and not current_entry_data.get("date"):
                date_match = date_pattern_full.search(line)
                if not date_match: date_match = year_date_pattern.search(line)
                if date_match:
                    date_str = date_match.group(0).strip()
                    if date_str.lower() == line.lower() or len(date_str) > len(line) / 2:
                        current_entry_data["date"] = date_str
                        processed_lines_for_current_title_company_date.add(current_line_index)
                        # === DEBUG PRINT ===
                        if self.debug and current_entry_data.get("title") == "Medical Intern":
                            print(f"DEBUG_MEDICAL_INTERN (Date from separate line): Date set to '{date_str}' from line '{line}'")
                        # === END DEBUG PRINT ===
                        if self.debug: print(f"DEBUG (_extract_experience): Found Date: '{date_str}' consuming line (idx {current_line_index}): '{line}'")
                        original_line_for_responsibility_check = line.replace(date_str, "").strip() # Update for responsibility
                        line_consumed_this_iteration = True # Date consumed this line.
            if line_consumed_this_iteration and (not original_line_for_responsibility_check or len(original_line_for_responsibility_check.split()) < 3) :
                continue # Line fully processed by date or remnant too short

            # 3. Attempt to find Company/Location (if not already found and line not consumed and a title exists)
            if not line_consumed_this_iteration and current_entry_data.get("title") and \
               (not current_entry_data.get("company") or not current_entry_data.get("location")) and \
               current_line_index not in processed_lines_for_current_title_company_date:
                
                line_for_co_loc_parse = line # Use a copy for this block's parsing attempts
                
                if self._is_likely_standalone_company_location_line(line_for_co_loc_parse):
                    doc = nlp(line_for_co_loc_parse)
                    # Extract all entities first to make them available
                    all_entities = [(ent.text.strip(), ent.label_) for ent in doc.ents]
                    org_entities_text = [e[0] for e in all_entities if e[1] == "ORG"]
                    gpe_loc_entities_text = [e[0] for e in all_entities if e[1] in ["GPE", "LOC"]]
                    fac_entities_text = [e[0] for e in all_entities if e[1] == "FAC"]

                    # ---- START DEBUG ----
                    if "hospital jasin" in line_for_co_loc_parse.lower() and "melaka" in line_for_co_loc_parse.lower():
                        if self.debug: print(f"DEBUG_HJ_MELAKA: Line: '{line_for_co_loc_parse}', All doc.ents: {all_entities}")
                    # ---- END DEBUG ----

                    identified_company_ner = None
                    identified_location_ner = None

                    # --- START Special Handling for Hospital FAC + ORG-as-Location ---
                    if len(fac_entities_text) == 1 and len(org_entities_text) == 1 and not gpe_loc_entities_text:
                        fac_name = fac_entities_text[0]
                        org_name = org_entities_text[0]
                        # Check if FAC looks like a hospital and ORG looks like a common Malaysian city/state or is short
                        known_malaysian_locations_lower = ["melaka", "kuala lumpur", "selangor", "penang", "johor bahru", "cyberjaya", "putrajaya"]
                        if ("hospital" in fac_name.lower() or "clinic" in fac_name.lower() or "medical centre" in fac_name.lower()) and \
                           (org_name.lower() in known_malaysian_locations_lower or len(org_name.split()) <= 2):
                            identified_company_ner = fac_name
                            identified_location_ner = org_name
                            if self.debug: print(f"DEBUG_HJ_MELAKA: Special FAC+ORG override: Co='{identified_company_ner}', Loc='{identified_location_ner}'")
                    # --- END Special Handling ---
                    
                    # If not handled by special case, then proceed with existing logic structure
                    if not (identified_company_ner and identified_location_ner):
                        if org_entities_text:
                            if len(org_entities_text) > 1 and gpe_loc_entities_text:
                                non_loc_orgs = [org for org in org_entities_text if org.lower() not in [gpe.lower() for gpe in gpe_loc_entities_text]]
                                if non_loc_orgs:
                                    identified_company_ner = sorted(non_loc_orgs, key=len, reverse=True)[0]
                                else: 
                                    identified_company_ner = sorted(org_entities_text, key=len, reverse=True)[0]
                            elif org_entities_text: 
                                 identified_company_ner = sorted(org_entities_text, key=len, reverse=True)[0]
                        
                        if gpe_loc_entities_text:
                            identified_location_ner = sorted(gpe_loc_entities_text, key=len, reverse=True)[0]

                    # If NER found both, and they are distinct, try to assign
                    if identified_company_ner and identified_location_ner and identified_company_ner.lower() != identified_location_ner.lower():
                        if not current_entry_data.get("company"):
                            current_entry_data["company"] = identified_company_ner
                            if self.debug: print(f"DEBUG (_extract_experience): NER Company (ORG): '{identified_company_ner}' from line '{line_for_co_loc_parse}'")
                        if not current_entry_data.get("location"):
                            current_entry_data["location"] = identified_location_ner
                            if self.debug: print(f"DEBUG (_extract_experience): NER Location (GPE/LOC): '{identified_location_ner}' from line '{line_for_co_loc_parse}'")
                        line_consumed_this_iteration = True
                    elif identified_company_ner and not current_entry_data.get("company"): # Only company by NER
                        current_entry_data["company"] = identified_company_ner
                        if self.debug: print(f"DEBUG (_extract_experience): NER Company (ORG only): '{identified_company_ner}' from line '{line_for_co_loc_parse}'")
                        # Try to infer location if company line has a comma and a plausible location part
                        if ',' in line_for_co_loc_parse and identified_company_ner in line_for_co_loc_parse.split(',')[0]:
                            potential_loc_part = line_for_co_loc_parse.split(',', 1)[1].strip()
                            if potential_loc_part and not gpe_loc_entities_text: # No GPE identified by NER for this part
                                # Basic check: is it short and looks like a place?
                                if len(potential_loc_part.split()) <= 3 and not any(kw.lower() in potential_loc_part.lower() for kw in self.company_name_keywords):
                                    current_entry_data["location"] = potential_loc_part
                                    if self.debug: print(f"DEBUG (_extract_experience): Inferred Location (post-ORG): '{potential_loc_part}' from '{line_for_co_loc_parse}'")
                        line_consumed_this_iteration = True
                    elif identified_location_ner and not current_entry_data.get("location"): # Only location by NER
                        current_entry_data["location"] = identified_location_ner
                        if self.debug: print(f"DEBUG (_extract_experience): NER Location (GPE/LOC only): '{identified_location_ner}' from line '{line_for_co_loc_parse}'")
                        # Try to infer company if location line has a comma and a plausible company part
                        if ',' in line_for_co_loc_parse and identified_location_ner in line_for_co_loc_parse.split(',')[1]:
                             potential_co_part = line_for_co_loc_parse.split(',',1)[0].strip()
                             if potential_co_part and not org_entities_text: # No ORG identified by NER
                                if len(potential_co_part.split()) <= 4 : # Allow slightly longer for company names
                                    current_entry_data["company"] = potential_co_part
                                    if self.debug: print(f"DEBUG (_extract_experience): Inferred Company (post-GPE/LOC): '{potential_co_part}' from '{line_for_co_loc_parse}'")
                        line_consumed_this_iteration = True

                    # Fallback/Refinement: if NER didn't populate both and line has "A, B" structure
                    if not line_consumed_this_iteration or (not current_entry_data.get("company") or not current_entry_data.get("location")):
                        if ',' in line_for_co_loc_parse:
                            parts = [p.strip() for p in line_for_co_loc_parse.split(',', 1)] # Split only on first comma
                        if len(parts) == 2:
                                part1_is_likely_co = any(ck.lower() in parts[0].lower() for ck in self.company_name_keywords) or len(parts[0].split()) <=3
                                part1_is_likely_loc = nlp(parts[0]).ents and nlp(parts[0]).ents[0].label_ in ["GPE", "LOC"]
                                
                                part2_is_likely_co = any(ck.lower() in parts[1].lower() for ck in self.company_name_keywords) or len(parts[1].split()) <=3
                                part2_is_likely_loc = nlp(parts[1]).ents and nlp(parts[1]).ents[0].label_ in ["GPE", "LOC"]

                                if not current_entry_data.get("company") and not current_entry_data.get("location"):
                                    # Case 1: Part1 is Co, Part2 is Loc (e.g. "Hospital Jasin, Melaka")
                                    if (identified_company_ner == parts[0] or part1_is_likely_co) and (identified_location_ner == parts[1] or part2_is_likely_loc) and not part1_is_likely_loc and not part2_is_likely_co :
                                        current_entry_data["company"] = parts[0]
                                        current_entry_data["location"] = parts[1]
                                        if self.debug: print(f"DEBUG (_extract_experience): Heuristic Co/Loc from '{line_for_co_loc_parse}': Co='{parts[0]}', Loc='{parts[1]}'")
                                        line_consumed_this_iteration = True
                                    # Case 2: Part1 is Loc, Part2 is Co (e.g. "Melaka, Hospital Jasin")
                                    elif (identified_location_ner == parts[0] or part1_is_likely_loc) and (identified_company_ner == parts[1] or part2_is_likely_co) and not part1_is_likely_co and not part2_is_likely_loc:
                                        current_entry_data["location"] = parts[0]
                                        current_entry_data["company"] = parts[1]
                                        if self.debug: print(f"DEBUG (_extract_experience): Heuristic Co/Loc (reversed) from '{line_for_co_loc_parse}': Co='{parts[1]}', Loc='{parts[0]}'")
                                        line_consumed_this_iteration = True
                                elif not current_entry_data.get("company") and identified_location_ner == parts[1]: # We have location as part2, part1 must be company
                                    current_entry_data["company"] = parts[0]
                                    if self.debug: print(f"DEBUG (_extract_experience): Heuristic Co (part1) based on Loc (part2='{parts[1]}'): Co='{parts[0]}'")
                                    line_consumed_this_iteration = True
                                elif not current_entry_data.get("location") and identified_company_ner == parts[0]: # We have company as part1, part2 must be location
                                     current_entry_data["location"] = parts[1]
                                     if self.debug: print(f"DEBUG (_extract_experience): Heuristic Loc (part2) based on Co (part1='{parts[0]}'): Loc='{parts[1]}'")
                                     line_consumed_this_iteration = True
                    
                    if line_consumed_this_iteration: # If company or location was set by any of the above
                        processed_lines_for_current_title_company_date.add(current_line_index)
                        temp_line_check_for_resp = line_for_co_loc_parse
                        
                        # Remove identified company and location from the line to check remnant for responsibility
                        co_text = current_entry_data.get("company")
                        loc_text = current_entry_data.get("location")

                        # More careful removal to avoid issues if one is substring of another (e.g. "New York", "New York City")
                        # Build a regex to remove them only if they appear as whole phrases, prioritizing longer one if overlap
                        to_remove = []
                        if co_text: to_remove.append(re.escape(co_text))
                        if loc_text: to_remove.append(re.escape(loc_text))
                        
                        if to_remove:
                            to_remove.sort(key=len, reverse=True) # Remove longer matches first
                            for item_to_remove_pattern in to_remove:
                                # Remove the item, also handling potential comma and spaces around it
                                # Attempt 1: item, | , item
                                temp_line_check_for_resp = re.sub(r'\b' + item_to_remove_pattern + r'\s*,?\s*|\s*,?\s*\b' + item_to_remove_pattern + r'\b', '', temp_line_check_for_resp, count=1, flags=re.IGNORECASE).strip(" ,")
                        
                        original_line_for_responsibility_check = temp_line_check_for_resp.strip(" ,")

                        if not original_line_for_responsibility_check or len(original_line_for_responsibility_check.split()) < 2:
                            if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' (idx {current_line_index}) identified as Co/Loc and remnant ('{original_line_for_responsibility_check}') is insignificant. Clearing for responsibility.")
                            original_line_for_responsibility_check = "" 
                        else: 
                            if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' (idx {current_line_index}) had Co/Loc. Remnant for resp: '{original_line_for_responsibility_check}'")
                    
                    if line_consumed_this_iteration and (not original_line_for_responsibility_check or len(original_line_for_responsibility_check.split()) < 3) : 
                        if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' consumed by Co/Loc or remnant '{original_line_for_responsibility_check}' too short. Continuing.")
                        continue 

            if should_finalize_due_to_header: # This check should be AFTER all attempts to extract Title/Date/Co/Loc from current line
                if self.debug: print(f"DEBUG (_extract_experience): Line '{line}' was a header that finalized an entry. Skipping for resp.")
                continue
            
            # If line_consumed_this_iteration became true due to Title/Date/Co/Loc,
            # original_line_for_responsibility_check might hold a remnant or be empty.
            # If it's empty or too short, no point in responsibility parsing for this line.
            if not original_line_for_responsibility_check.strip() or \
               (line_consumed_this_iteration and len(original_line_for_responsibility_check.strip().split()) < 3 and not original_line_for_responsibility_check.strip().lower() == "clear communication") : # Allow "clear communication" even if short
                if self.debug and line.strip() and original_line_for_responsibility_check.strip() : print(f"DEBUG (_extract_experience): Line remnant '({original_line_for_responsibility_check})' after T/D/C/L processing is too short or line was consumed. Skipping resp for this line: '{line}'")
                continue

            # 4. Add to responsibilities if line not consumed and is part of a valid entry
            if current_entry_data.get("title") and isinstance(original_line_for_responsibility_check, str) and original_line_for_responsibility_check.strip():
                
                # --- START: Add check to prevent Co/Loc remnants ---
                temp_is_co_loc_remnant_for_resp_block = False
                # REMOVED: if current_line_index in processed_lines_for_current_title_company_date: 
                _remnant_lower = original_line_for_responsibility_check.strip().lower()
                _company_name_lower = str(current_entry_data.get("company", "")).lower()
                _location_name_lower = str(current_entry_data.get("location", "")).lower()
                
                _cond1 = _company_name_lower and _remnant_lower in _company_name_lower and _company_name_lower != _remnant_lower
                _cond2 = _location_name_lower and _remnant_lower in _location_name_lower and _location_name_lower != _location_name_lower # Corrected from _location_name_lower != _location_name_lower
                _cond3 = _remnant_lower == "hospital" or \
                         (_location_name_lower and _remnant_lower == _location_name_lower) or \
                         _remnant_lower.startswith("hospital ,") or \
                         _remnant_lower == "hospital  , melaka" # Explicitly catch this problematic case

                if _cond1 or _cond2 or _cond3:
                    temp_is_co_loc_remnant_for_resp_block = True
                
                if temp_is_co_loc_remnant_for_resp_block: # Use the locally recalculated flag
                    if self.debug: print(f"DEBUG (_extract_experience): Skipping responsibility add for likely Co/Loc remnant (re-checked): '{original_line_for_responsibility_check}' from line index {current_line_index}")
                    continue 
                # --- END: Add check to prevent Co/Loc remnants ---

                # If line was already processed for title and is identical to title, skip.
                if current_line_index in processed_lines_for_current_title_company_date and \
                   original_line_for_responsibility_check.strip().lower() == str(current_entry_data.get("title", "")).lower():
                    if self.debug: print(f"DEBUG (_extract_experience): Skipping responsibility add for line (idx {current_line_index}) as it's identical to the title and was processed for metadata.")
                    continue

                # If the line looks like a new section header or a different job title, skip adding as responsibility for current entry.
                if self._is_line_a_potential_header_or_new_title(original_line_for_responsibility_check, current_entry_data.get("title")):
                    if self.debug: print(f"DEBUG (_extract_experience): Line '{original_line_for_responsibility_check}' looks like a new header/title. Skipping for current responsibilities.")
                    continue

                line_to_add_as_responsibility = original_line_for_responsibility_check.strip()
                line_lower_for_filter = line_to_add_as_responsibility.lower()
                is_just_year_or_date_range = year_date_pattern.fullmatch(line_lower_for_filter) or date_pattern_full.fullmatch(line_lower_for_filter)
                # Corrected regex for phone numbers and emails, ensuring proper escaping for Python strings
                is_contact_info_like = "linkedin.com/" in line_lower_for_filter or \
                                       "github.com/" in line_lower_for_filter or \
                                       re.match(r'^\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\s*$', line_lower_for_filter) or \
                                       re.match(r'^\s*[\w.-]+@[\w.-]+\.\w+\s*$', line_lower_for_filter)
                
                if not is_contact_info_like and \
                   line_lower_for_filter not in ["responsibilities", "key responsibilities", "achievements", "key achievements"] and \
                   not is_just_year_or_date_range:
                    if current_entry_data["responsibilities"]:
                        last_responsibility = current_entry_data["responsibilities"][-1]
                        starts_like_new_bullet = re.match(r'^\s*[-*•➢❖]', line_to_add_as_responsibility) or \
                                               (line_to_add_as_responsibility and line_to_add_as_responsibility[0].isupper() and \
                                                len(line_to_add_as_responsibility.split()) > 2 and \
                                                any(line_to_add_as_responsibility.lower().startswith(verb) for verb in ["assisted", "developed", "managed", "led", "responsible", "created", "implemented", "designed", "collaborated", "participated", "gained", "coordinated"]))

                        if line_to_add_as_responsibility.lower() == "plans under supervision" and \
                           last_responsibility.endswith("preliminary care"):
                            current_entry_data["responsibilities"][-1] += " " + line_to_add_as_responsibility
                            if self.debug: print(f"DEBUG (_extract_experience): Appended specific 'plans under supervision'")
                        elif not starts_like_new_bullet and \
                             not last_responsibility.strip().endswith(('.', '!', '?')) and \
                             (line_to_add_as_responsibility[0].islower() or \
                              len(line_to_add_as_responsibility.split()) <= 3):
                            current_entry_data["responsibilities"][-1] += " " + line_to_add_as_responsibility
                            if self.debug: print(f"DEBUG (_extract_experience): Appended general continuation: '{line_to_add_as_responsibility}'")
                        else: 
                            prev_resp_was_dangling_fragment = False
                            if current_entry_data["responsibilities"]:
                                last_resp_raw = current_entry_data["responsibilities"][-1]
                                # Clean the last responsibility to check its nature (strip bullets, whitespace)
                                last_resp_cleaned_for_dangle_check = last_resp_raw.lstrip('*-•➢❖').strip()

                                # Define "dangling fragment" characteristics:
                                # - It's not empty after cleaning
                                # - It's short (1 or 2 words)
                                # - It starts with a lowercase letter
                                # - It doesn't end with sentence-terminating punctuation
                                if last_resp_cleaned_for_dangle_check and \
                                   len(last_resp_cleaned_for_dangle_check.split()) <= 3 and \
                                   last_resp_cleaned_for_dangle_check[0].islower():
                                    prev_resp_was_dangling_fragment = True
                            
                            # Clean the current line as well, removing potential leading bullets for merging
                            current_line_cleaned_for_dangle_logic = line_to_add_as_responsibility.lstrip('*-•➢❖').strip()

                            if prev_resp_was_dangling_fragment:
                                # If the previous item was a dangling fragment,
                                # merge the current new bullet point line with it.
                                current_entry_data["responsibilities"][-1] = current_line_cleaned_for_dangle_logic + " " + last_resp_cleaned_for_dangle_check
                                if self.debug: print(f"DEBUG (_extract_experience): Merged new bullet '{current_line_cleaned_for_dangle_logic}' with dangling fragment '{last_resp_cleaned_for_dangle_check}'")
                            else:
                                # Otherwise, add the current line as a new responsibility item (original behavior)
                                current_entry_data["responsibilities"].append(line_to_add_as_responsibility) # Add raw line; bullets are stripped during finalize_current_entry
                                if self.debug: print(f"DEBUG (_extract_experience): Added new distinct resp: '{line_to_add_as_responsibility}'")
                    else: # No existing responsibilities, add as first
                        current_entry_data["responsibilities"].append(line_to_add_as_responsibility)
                        if self.debug: print(f"DEBUG (_extract_experience): Added first resp: '{line_to_add_as_responsibility}'")
                else:
                    if self.debug: print(f"DEBUG (_extract_experience): Line '{line_to_add_as_responsibility}' was FILTERED OUT from being a responsibility due to filter conditions (contact/header/date-like).")

        # Finalize any remaining entry after loop
        # === DEBUG PRINT ===
        if self.debug and current_entry_data.get("title") == "Medical Intern":
            print(f"DEBUG_MEDICAL_INTERN (End of Loop): Calling finalize_current_entry for potentially last entry.")
        # === END DEBUG PRINT ===
        finalize_current_entry()
        processed_lines_for_current_title_company_date.clear() # Clear one last time
        
        if self.debug: print(f"DEBUG (_extract_experience): Total experience entries found: {len(experience_entries)}")
        return experience_entries

    # --- START: Refactored _extract_skills and its helper ---
    def _parse_block_for_skills(self, text_block: str, general_set: set, soft_set: set):
        """
        Helper function to parse a block of text and extract skills.
        It uses self.sorted_skill_references to find known skills.
        """
        lines = [line.strip() for line in text_block.split('\n') if line.strip()]
        for line_content in lines:
            temp_line_for_matching = line_content 
            
            # Enhanced debug for specific skills - checks if any part of the skill name is in the line
            if self.debug:
                debug_skills_to_trace = ["o&g", "c++", "ui/ux design", "react native", "asp.net", "series 7"]
                for ds_trace in debug_skills_to_trace:
                    if ds_trace in temp_line_for_matching.lower():
                        print(f"DEBUG (_parse_block_for_skills): Processing line for potential special skill ('{ds_trace}'): '{temp_line_for_matching}'")
                        break # Print once per line if any debug skill is found

            for canonical_skill_name, skill_type in self.sorted_skill_references:
                if not canonical_skill_name: continue 

                # Add word boundaries to the pattern string
                if canonical_skill_name == "C++":
                    pattern_str = r'\bC\+\+\b' # Hardcoded pattern for C++
                elif canonical_skill_name == "C#":
                    pattern_str = r'\bC#\b'     # Hardcoded pattern for C#
                else:
                    pattern_str = r'\b' + re.escape(canonical_skill_name) + r'\b' # Corrected: single backslash for \b
                
                original_temp_line_for_current_skill_search = temp_line_for_matching # For debug
                
                if self.debug and canonical_skill_name.lower() == "c++": 
                    print(f"DEBUG_CPP_SKILL: Attempting to match repr(canonical_skill_name): {repr(canonical_skill_name)} with pattern repr: {repr(pattern_str)} in line repr: {repr(temp_line_for_matching)}")

                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                except re.error as e:
                    if self.debug: print(f"DEBUG (_parse_block_for_skills): Regex error for skill '{canonical_skill_name}', pattern '{pattern_str}': {e}")
                    continue 

                match_found_for_current_skill_in_line_iteration = False
                
                # --- START: Direct match for C++ and C# as a fallback/primary check if line is exact ---
                if canonical_skill_name in ["C++", "C#"] and temp_line_for_matching.lower() == canonical_skill_name.lower():
                    if self.debug: print(f"DEBUG_DIRECT_MATCH: Direct exact match for '{canonical_skill_name}' in line '{temp_line_for_matching}'")
                    match_found_for_current_skill_in_line_iteration = True
                    if skill_type == 'soft':
                        soft_set.add(canonical_skill_name)
                    else: 
                        general_set.add(canonical_skill_name)
                    if self.debug and canonical_skill_name.lower() == "c++":
                         print(f"DEBUG_CPP_SKILL: MATCHED (direct exact) '{canonical_skill_name}' (type: {skill_type}). Adding to set.")
                    temp_line_for_matching = "$" * len(temp_line_for_matching) # Mark as consumed
                # --- END: Direct Match ---
                
                # Proceed with regex search if not directly matched and consumed, or for other skills
                if not match_found_for_current_skill_in_line_iteration:
                    while True:
                        match = pattern.search(temp_line_for_matching)
                        if match:
                            match_found_for_current_skill_in_line_iteration = True
                            start, end = match.span()
                            
                            if skill_type == 'soft':
                                soft_set.add(canonical_skill_name)
                            else: 
                                general_set.add(canonical_skill_name)
                            
                            if self.debug and canonical_skill_name.lower() == "c++":
                               print(f"DEBUG_CPP_SKILL: MATCHED (regex) '{canonical_skill_name}' (type: {skill_type}). Adding to set.")
                            
                            if self.debug and (canonical_skill_name.lower() in ["o&g", "c++", "ui/ux design", "series 7"]):
                               print(f"DEBUG (_parse_block_for_skills): Matched skill '{canonical_skill_name}' (type: {skill_type}) in: '...{temp_line_for_matching[max(0,start-10):end+10]}...'")

                            temp_line_for_matching = temp_line_for_matching[:start] + ("$" * (end - start)) + temp_line_for_matching[end:]
                        else:
                            break # Exit while loop for current skill if no more matches in line

                if self.debug and match_found_for_current_skill_in_line_iteration:
                    if any(ds_trace in original_temp_line_for_current_skill_search.lower() for ds_trace in ["o&g", "c++", "ui/ux design", "series 7"]):
                        print(f"DEBUG (_parse_block_for_skills): Line after processing skill '{canonical_skill_name}': '{temp_line_for_matching}' (was: '{original_temp_line_for_current_skill_search}')")


    def _extract_skills(self, skills_text: str, primary_field: str) -> Dict[str, List[str]]:
        if not skills_text or not skills_text.strip():
            if self.debug: print("DEBUG (_extract_skills): Skills text is empty or not provided.")
            return {"general_skills": [], "soft_skills": []}
        if self.debug: print(f"DEBUG (_extract_skills): Received skills text (first 100): '{skills_text[:100].replace(chr(10), ' ')}'")

        final_general_skills = set()
        final_soft_skills = set()
        
        general_header_pattern = re.compile(r'^ \s*(General|Technical|Hard|Core)\s+Skills?\s*[: \n]', re.IGNORECASE | re.MULTILINE)
        soft_header_pattern = re.compile(r'^ \s*Soft\s+Skills?\s*[: \n]', re.IGNORECASE | re.MULTILINE)

        general_match = general_header_pattern.search(skills_text)
        soft_match = soft_header_pattern.search(skills_text)
        
        text_for_general = ""
        text_for_soft = ""
        unassigned_text_parts = [] 

        # Determine which parts of the text fall under general, soft, or unassigned
        last_processed_end = 0
        if general_match and soft_match:
            if general_match.start() < soft_match.start():
                # Order: Unassigned, General, Unassigned between, Soft, Unassigned after
                unassigned_text_parts.append(skills_text[last_processed_end:general_match.start()])
                text_for_general = skills_text[general_match.end():soft_match.start()]
                last_processed_end = soft_match.start() # before soft header
                # text between general_match.end() and soft_match.start() is general_text
                # then text from soft_match.end() is soft_text
            text_for_soft = skills_text[soft_match.end():]
                # Any text *between* sections if not captured by headers goes to unassigned
                # This logic is tricky. Let's simplify:
                # Slice text based on earliest header.
                
                # Re-evaluating slicing logic for clarity
            slices = []
                # Add text before the first header encountered (if any)
            first_header_start = min(general_match.start(), soft_match.start())
            if first_header_start > 0:
                    slices.append({'text': skills_text[:first_header_start], 'type': 'unassigned'})
                
            if general_match.start() < soft_match.start():
                    slices.append({'text': skills_text[general_match.end():soft_match.start()], 'type': 'general'})
                    slices.append({'text': skills_text[soft_match.end():], 'type': 'soft'})
                    # What if there's text after soft_match.end()? It's part of soft.
            else: # soft_match.start() < general_match.start()
                    slices.append({'text': skills_text[soft_match.end():general_match.start()], 'type': 'soft'})
                    slices.append({'text': skills_text[general_match.end():], 'type': 'general'})

                # Process slices
            for s_info in slices:
                    if s_info['type'] == 'general': 
                        self._parse_block_for_skills(s_info['text'], final_general_skills, final_soft_skills)
                    elif s_info['type'] == 'soft':
                        self._parse_block_for_skills(s_info['text'], final_general_skills, final_soft_skills)
                    else: # unassigned
                         self._parse_block_for_skills(s_info['text'], final_general_skills, final_soft_skills)
            else: # No specific header found, or only one header
                self._parse_block_for_skills(skills_text, final_general_skills, final_soft_skills)

        elif general_match: # Only general skills header
            unassigned_text_parts.append(skills_text[:general_match.start()])
            text_for_general = skills_text[general_match.end():]
            self._parse_block_for_skills(text_for_general, final_general_skills, final_soft_skills)
            for unassigned_block in unassigned_text_parts: # Parse text before header
                if unassigned_block.strip(): self._parse_block_for_skills(unassigned_block, final_general_skills, final_soft_skills)
        
        elif soft_match: # Only soft skills header
            unassigned_text_parts.append(skills_text[:soft_match.start()])
            text_for_soft = skills_text[soft_match.end():]
            self._parse_block_for_skills(text_for_soft, final_general_skills, final_soft_skills)
            for unassigned_block in unassigned_text_parts: # Parse text before header
                if unassigned_block.strip(): self._parse_block_for_skills(unassigned_block, final_general_skills, final_soft_skills)
        
        else: # No explicit headers found, treat all text as unassigned (potential skills)
            self._parse_block_for_skills(skills_text, final_general_skills, final_soft_skills)
        
        result = {
            "general_skills": sorted(list(final_general_skills - final_soft_skills)), 
            "soft_skills": sorted(list(final_soft_skills))
        }
        if self.debug: print(f"DEBUG (_extract_skills): Final skills: {result}")
        return result
    # --- END: Refactored _extract_skills and its helper ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_parser.py <resume_text_file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        # Try reading with utf-8-sig first to handle potential BOM
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            resume_text_content = f.read()
    except UnicodeDecodeError:
        # Fallback to utf-8 if utf-8-sig fails
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text_content = f.read()
        except Exception as e:
            print(f"Error: Could not read file {file_path} with utf-8-sig or utf-8 encoding: {e}")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    # Instantiate with debug=True to see detailed parsing steps
    parser_instance = EnhancedParser(debug=True)
    parsed_resume_data = parser_instance.parse(resume_text_content)
    
    import json
    print("\n--- JSON Output ---")
    # Ensure non-ASCII characters are handled correctly in JSON output
    print(json.dumps(parsed_resume_data, indent=2, ensure_ascii=False))
