<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Smalot\PdfParser\Parser;
use Exception;

class ResumeParserService
{
    /**
     * Parse a PDF resume file into structured data
     * 
     * @param string $filePath Path to the PDF file
     * @return array Structured data from the resume
     */
    public function parseResume(string $filePath): array
    {
        try {
            Log::info("Starting to parse resume: {$filePath}");
            
            // Handle different storage locations
            if (strpos($filePath, 'public/') === 0) {
                // Convert public storage path to physical path
                $filePath = Storage::path($filePath);
            }
            
            Log::info("Attempting to parse file at physical path: {$filePath}");
            
            // Make sure file exists
            if (!file_exists($filePath)) {
                throw new Exception("Resume file not found at: {$filePath}");
            }
            
            // Extract text from PDF with primary method
            try {
                $parser = new Parser();
                $pdf = $parser->parseFile($filePath);
                $text = $pdf->getText();
                
                // Check if text was properly extracted
                if (empty(trim($text))) {
                    throw new Exception("Primary extraction method returned empty text");
                }
                
                Log::info("Successfully extracted text from PDF using primary method");
            } catch (Exception $e) {
                Log::warning("Primary PDF extraction failed: " . $e->getMessage() . ". Trying alternative method...");
                
                // Fallback to shell exec with pdftotext if available
                if (function_exists('shell_exec')) {
                    $escapedPath = escapeshellarg($filePath);
                    $text = shell_exec("pdftotext {$escapedPath} - 2>/dev/null");
                    
                    if (!empty(trim($text))) {
                        Log::info("Successfully extracted text using pdftotext fallback");
                    } else {
                        throw new Exception("All PDF extraction methods failed");
                    }
                } else {
                    throw $e; // Rethrow if no fallback is available
                }
            }
            
            // Log a sample of the extracted text for debugging
            Log::info("Text extraction sample (first 500 chars): " . substr($text, 0, 500));
            
            // Parse different sections using enhanced structure (matching the new analyzer.py)
            $result = [
                'contact_info' => $this->extractPersonalInfo($text),
                'education' => $this->extractEducation($text),
                'experience' => $this->extractExperience($text),
                'skills' => [
                    'all_skills' => $this->extractSkills($text),
                    'programming_languages' => $this->extractProgrammingLanguages($text, []),
                    'soft_skills' => []
                ],
                'languages' => $this->extractLanguages($text),
                'metadata' => [
                    'filename' => basename($filePath),
                    'file_size' => filesize($filePath),
                    'file_type' => pathinfo($filePath, PATHINFO_EXTENSION),
                    'text_length' => strlen($text)
                ],
                'recommendations' => [
                    'job_roles' => [],
                    'skills_to_add' => [],
                    'industry_matches' => []
                ]
            ];
            
            // Add additional recommendations based on the parsed data
            $result['recommendations'] = $this->generateRecommendations($result);
            
            // Convert arrays to objects for consistent JSON encoding
            array_walk_recursive($result, function(&$item) {
                if (is_array($item) && array_keys($item) === range(0, count($item) - 1)) {
                    $item = array_values($item);
                }
            });
            
            // Validate that the result can be JSON encoded
            $jsonString = json_encode($result);
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception("Failed to encode parsed data: " . json_last_error_msg());
            }
            
            Log::info("Resume parsing completed successfully", [
                'sections' => array_keys($result),
                'skills_count' => count($result['skills']['all_skills']),
                'json_valid' => true
            ]);
            
            return $result;
        } catch (Exception $e) {
            Log::error("Error parsing resume: " . $e->getMessage());
            
            // Return empty structured data on error
            return [
                'contact_info' => [],
                'education' => [],
                'experience' => [],
                'skills' => [
                    'all_skills' => [],
                    'programming_languages' => [],
                    'soft_skills' => []
                ],
                'languages' => [],
                'metadata' => [
                    'filename' => basename($filePath),
                    'file_size' => filesize($filePath),
                    'file_type' => pathinfo($filePath, PATHINFO_EXTENSION),
                    'error' => true
                ],
                'recommendations' => [
                    'job_roles' => [],
                    'skills_to_add' => [],
                    'industry_matches' => []
                ],
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Parse a PDF resume file using the enhanced Python extractor and parser
     * 
     * @param string $filePath Path to the PDF file
     * @return array Structured data from the resume
     */
    public function parseResumeWithEnhanced(string $filePath): array
    {
        try {
            Log::info("Starting to parse resume with enhanced parser: {$filePath}");
            
            // Handle different storage locations
            if (strpos($filePath, 'public/') === 0) {
                // Convert public storage path to physical path
                $filePath = Storage::path($filePath);
            }
            
            Log::info("Attempting to parse file at physical path: {$filePath}");
            
            // Make sure file exists
            if (!file_exists($filePath)) {
                throw new Exception("Resume file not found at: {$filePath}");
            }
            
            // Path to the Python script
            $pythonScript = base_path('streamlit_frontend/enhanced_parser_cli.py');
            
            // Always create/update the Python script to ensure it has the latest changes
                $this->createEnhancedParserCLI();
            
            // Determine correct Python executable for OS
            $venvPython = null;
            if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
                $venvPython = base_path('streamlit_frontend/venv/Scripts/python.exe');
            } else {
            $venvPython = base_path('streamlit_frontend/venv/bin/python');
            }
            if (!file_exists($venvPython)) {
                $venvPython = 'python'; // fallback to system python
            }
            $escapedFilePath = escapeshellarg($filePath);
            $command = escapeshellarg($venvPython) . " " . escapeshellarg($pythonScript) . " " . $escapedFilePath;
            
            // Execute the command and capture output
            $output = shell_exec($command);
            
            if (empty($output)) {
                throw new Exception("Enhanced parser returned empty output");
            }
            
            // Decode the JSON output
            $result = json_decode($output, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception("Failed to decode parser output: " . json_last_error_msg() . " Output: " . substr($output, 0, 500));
            }
            
            // Format result to match expected structure
            $formattedResult = $this->formatEnhancedParserResults($result, basename($filePath));
            
            Log::info("Resume parsing completed successfully with enhanced parser", [
                'sections' => array_keys($formattedResult),
                'skills_count' => count($formattedResult['skills']['general'] ?? []) + count($formattedResult['skills']['soft_skills'] ?? []),
                'primary_field' => $formattedResult['primary_field'] ?? 'N/A',
                'json_valid' => true
            ]);
            
            return $formattedResult;
        } catch (Exception $e) {
            Log::error("Error parsing resume with enhanced parser: " . $e->getMessage());
            
            return [
                'contact_info' => [],
                'education' => [],
                'experience' => [],
                'skills' => [
                    'general' => [],
                    'soft_skills' => []
                ],
                'languages' => [],
                'primary_field' => 'general', // Default on error
                'error' => $e->getMessage(),
                'metadata' => [
                    'filename' => basename($filePath),
                    'error' => true
                ]
            ];
        }
    }
    
    /**
     * Format the results from the enhanced parser to match our expected structure.
     * 
     * @param array $parserOutput The raw results from the enhanced Python parser.
     * @param string $filename The original filename for metadata.
     * @return array The formatted results suitable for Resume->parsed_data.
     */
    private function formatEnhancedParserResults(array $parserOutput, string $filename): array
    {
        $primaryField = $parserOutput['primary_field'] ?? 'general'; // Default to general if not present

        // Directly use the skills structure from Python output.
        // The controller and Streamlit frontend are expected to handle this rich structure.
        // Provide a default structure if 'skills' is entirely missing from Python output,
        // matching what the controller might expect as a fallback.
        $skillsData = $parserOutput['skills'] ?? [
            'general' => [], 
            'soft_skills' => [], 
            'all_extracted_normalized' => [] 
            // If $parserOutput['skills'] is present, it will contain the detailed categories
            // e.g., 'medical' => [...], 'finance' => [...], 'soft_skills' => [...], etc.
        ];

        $formatted = [
            'contact_info' => $parserOutput['contact_info'] ?? [],
            'education' => $parserOutput['education'] ?? [],
            'experience' => $parserOutput['experience'] ?? [],
            'skills' => $skillsData, // Use the potentially rich skills structure from Python
            'languages' => $parserOutput['languages'] ?? [],
            'primary_field' => $primaryField,
            'job_recommendations' => $parserOutput['job_recommendations'] ?? [], // Pass through job recommendations
            'raw_text' => $parserOutput['raw_text'] ?? null, // Pass through raw_text
            'metadata' => [
                'filename' => $filename,
                'parsed_by' => 'enhanced_parser_cli.py',
                'parse_timestamp' => date('Y-m-d H:i:s'),
            ],
        ];

        // Propagate Python error information if present
        if (isset($parserOutput['error'])) {
            $formatted['error'] = $parserOutput['error'];
            // Log traceback for server-side debugging, don't send it to client unless explicitly needed for user debugging.
            if (isset($parserOutput['traceback'])) {
                Log::warning("Python parser error trace: " . $parserOutput['traceback']);
                // Optionally, could add a more generic error message or flag to $formatted if needed
            }
        }
        
        // Preserve existing CGPA formatting logic for education entries
        if (isset($formatted['education']) && is_array($formatted['education'])) {
            foreach ($formatted['education'] as &$edu) {
                if (isset($edu['CGPA']) && !isset($edu['cgpa'])) {
                    $edu['cgpa'] = $edu['CGPA'];
                    unset($edu['CGPA']);
                }
                if (isset($edu['cgpa'])) {
                    $originalCgpa = $edu['cgpa'];
                    $cleanedCgpa = preg_replace('/[^0-9.]/', '', str_replace('CGPA:', '', $originalCgpa));
                    if (is_numeric($cleanedCgpa)) {
                        $edu['cgpa'] = floatval($cleanedCgpa);
                    } else {
                        $edu['cgpa'] = (string) $originalCgpa; // Keep original string if not cleanly parsable to float
                    }
                }
            }
        }

        return $formatted;
    }
    
    /**
     * Create the enhanced parser CLI script
     */
    private function createEnhancedParserCLI()
    {
        $pythonScript = base_path('streamlit_frontend/enhanced_parser_cli.py');
        
        $scriptContent = <<<'PYTHON'
#!/usr/bin/env python
import sys
import json
import os
import traceback # For detailed error logging

# Add the current directory (streamlit_frontend) to the path
# so we can import from lib.enhanced_parser and lib.analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.enhanced_parser import EnhancedParser
from lib.enhanced_extractor import EnhancedExtractor # Import EnhancedExtractor

def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "Usage: python enhanced_parser_cli.py <file_path>"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(json.dumps({
            "error": f"File not found: {file_path}"
        }))
        sys.exit(1)
    
    try:
        # Initialize EnhancedExtractor and extract text from the PDF
        extractor = EnhancedExtractor(debug=False) # Set debug as needed
        text = extractor.extract_from_pdf(file_path)
        
        if text is None or not text.strip():
            print(json.dumps({
                "error": f"Failed to extract text from PDF: {file_path}"
            }))
            sys.exit(1)
        
        # Initialize EnhancedParser with auto-detection for primary_field
        parser = EnhancedParser()
        parsed_data = parser.parse(text)
        
        print(json.dumps(parsed_data, indent=4))
        
    except Exception as e:
        print(json.dumps({
            "error": f"Error processing resume: {str(e)}", # Changed error message slightly for clarity
            "traceback": traceback.format_exc() 
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
PYTHON;

        file_put_contents($pythonScript, $scriptContent);
        chmod($pythonScript, 0755); // Make it executable
        Log::info("Enhanced parser CLI script created/updated at: {$pythonScript}");
    }
    
    /**
     * Extract personal information from resume
     */
    private function extractPersonalInfo(string $text): array
    {
        $personalInfo = [];
        
        // First, try to find a clear personal info section
        $sections = $this->splitIntoSections($text);
        $personalSection = $sections['personal'] ?? '';
        
        // Extract name - look for the most prominent name at the start of the resume
        // Avoid matching section headers by checking for common header words
        $namePattern = '/^(?!.*(?:RESUME|CV|CURRICULUM|VITAE|PERSONAL|PROFILE))([A-Z][a-zA-Z. ]+(?:\s+[A-Z][a-zA-Z. ]+)+)/m';
        if (preg_match($namePattern, $text, $matches) && isset($matches[1])) {
            $personalInfo['name'] = trim($matches[1]);
        }
        
        // Extract contact information from the personal section if found, otherwise from full text
        $textToSearch = $personalSection ?: $text;
        
        // Phone - look for labeled or standalone phone numbers
        $phonePatterns = [
            '/(?:Phone|Tel|Mobile|Cell)[\s:]+([+\d][\d\s.()-]{8,})$/m',
            '/^[+\d][\d\s.()-]{8,}$/m'
        ];
        
        foreach ($phonePatterns as $pattern) {
            if (preg_match($pattern, $textToSearch, $matches) && isset($matches[1])) {
                $personalInfo['phone'] = preg_replace('/[^\d+]/', '', $matches[1]);
                break;
            }
        }
        
        // Email - look for labeled or standalone email
        $emailPatterns = [
            '/(?:Email|E-mail)[\s:]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,})$/m',
            '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$/m'
        ];
        
        foreach ($emailPatterns as $pattern) {
            if (preg_match($pattern, $textToSearch, $matches) && isset($matches[1])) {
                $personalInfo['email'] = strtolower(trim($matches[1]));
                break;
            }
        }
        
        // Website/Portfolio
        $urlPatterns = [
            '/(?:Website|Portfolio|Blog)[\s:]+(?:https?:\/\/)?((?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/m',
            '/^(?:https?:\/\/)?((?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/m'
        ];
        
        foreach ($urlPatterns as $pattern) {
            if (preg_match($pattern, $textToSearch, $matches) && isset($matches[1])) {
                $personalInfo['website'] = 'https://' . str_replace('www.', '', $matches[1]);
                break;
            }
        }
        
        // Location/Address - look for labeled location or address pattern
        $addressPatterns = [
            '/(?:Location|Address)[\s:]+([^•\n]+(?:,\s*[^•\n]+){1,2})$/m',
            '/^([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2}|\s*[A-Z]{2}))$/m'
        ];
        
        foreach ($addressPatterns as $pattern) {
            if (preg_match($pattern, $textToSearch, $matches) && isset($matches[1])) {
                $personalInfo['address'] = trim($matches[1]);
                break;
            }
        }
        
        return $personalInfo;
    }
    
    /**
     * Split resume text into sections based on common section headers
     */
    private function splitIntoSections(string $text): array
    {
        $sections = [];
        
        // Define section patterns with variations
        $sectionPatterns = [
            'personal' => '/(?:PERSONAL|CONTACT|PROFILE)\s*(?:INFORMATION|DETAILS|DATA)?(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'education' => '/(?:EDUCATION|ACADEMIC|QUALIFICATION)S?\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'experience' => '/(?:EXPERIENCE|EMPLOYMENT|WORK|PROFESSIONAL)S?\s*(?:HISTORY|BACKGROUND)?\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'skills' => '/(?:SKILLS|EXPERTISE|COMPETENCIES|TECHNICAL)S?\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'languages' => '/(?:LANGUAGES?|LINGUISTIC)\s*(?:PROFICIENCY|SKILLS?)?\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'interests' => '/(?:INTERESTS?|HOBBIES|ACTIVITIES)\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si',
            'references' => '/(?:REFERENCES?|RECOMMENDATIONS?)\s*(?:\:|\n)(.*?)(?=\n[A-Z\s]{2,}:|\Z)/si'
        ];
        
        foreach ($sectionPatterns as $section => $pattern) {
            if (preg_match($pattern, $text, $matches)) {
                $sections[$section] = trim($matches[1]);
            }
        }
        
        return $sections;
    }
    
    /**
     * Extract education information from resume
     */
    private function extractEducation(string $text): array
    {
        $education = [];
        $sections = $this->splitIntoSections($text);
        
        if (!isset($sections['education'])) {
            return $education;
        }
        
        $educationText = $sections['education'];
        
        // Split into entries by looking for year patterns or double newlines
        $entryPattern = '/(?:(?:19|20)\d{2}.*?(?=(?:19|20)\d{2}|\Z))|(?:[^\n]+\n[^\n]+(?:\n(?:[^\n]|\n[^\n])+)?)/s';
        if (preg_match_all($entryPattern, $educationText, $entries) && isset($entries[0])) {
            foreach ($entries[0] as $entry) {
                $entry = trim($entry);
                if (empty($entry)) continue;
                
                $eduItem = [
                    'institution' => '',
                    'degree' => '',
                    'field' => '',
                    'dates' => '',
                    'gpa' => ''
                ];
                
                // Extract dates
                $datePattern = '/(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|Present|Current|Now)/i';
                if (preg_match($datePattern, $entry, $dates) && isset($dates[0])) {
                    $eduItem['dates'] = trim($dates[0]);
                    // Remove the date from entry to make other extractions cleaner
                    $entry = str_replace($dates[0], '', $entry);
                }
                
                // Extract degree and field
                $degreePattern = '/(?:Bachelor|Master|PhD|BSc|MSc|BA|MBA|BBA|Associate|Diploma)[^,\n]*(?:in|of)?\s+([^,\n]+)/i';
                if (preg_match($degreePattern, $entry, $degree)) {
                    $eduItem['degree'] = trim($degree[0]);
                    if (isset($degree[1])) {
                        $eduItem['field'] = trim($degree[1]);
                    }
                    // Remove the degree from entry
                    $entry = str_replace($degree[0], '', $entry);
                }
                
                // Extract GPA if present
                $gpaPattern = '/(?:GPA|Grade):\s*([\d.]+)/i';
                if (preg_match($gpaPattern, $entry, $gpa) && isset($gpa[1])) {
                    $eduItem['gpa'] = $gpa[1];
                    // Remove GPA from entry
                    $entry = str_replace($gpa[0], '', $entry);
                }
                
                // What remains should be the institution
                $entry = trim(preg_replace('/[\s\n]+/', ' ', $entry));
                if (!empty($entry)) {
                    $eduItem['institution'] = $entry;
                }
                
                // Only add if we have at least an institution or degree
                if (!empty($eduItem['institution']) || !empty($eduItem['degree'])) {
                    $education[] = $eduItem;
                }
            }
        }
        
        return $education;
    }
    
    /**
     * Extract work experience from resume
     */
    private function extractExperience(string $text): array
    {
        $experience = [];
        $sections = $this->splitIntoSections($text);
        
        if (!isset($sections['experience'])) {
            return $experience;
        }
        
        $experienceText = $sections['experience'];
        
        // Split into entries by looking for date patterns or company patterns
        $entryPattern = '/(?:(?:19|20)\d{2}.*?(?=(?:19|20)\d{2}|\Z))|(?:[A-Z][^•\n]+(?:\n(?:[^•\n]|\n[^•\n])+)?)/s';
        if (preg_match_all($entryPattern, $experienceText, $entries) && isset($entries[0])) {
            foreach ($entries[0] as $entry) {
                $entry = trim($entry);
                if (empty($entry)) continue;
                
                $expItem = [
                    'company' => '',
                    'position' => '',
                    'dates' => '',
                    'location' => '',
                    'responsibilities' => []
                ];
                
                // Extract dates
                $datePattern = '/(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:(?:19|20)\d{2}|Present|Current|Now)/i';
                if (preg_match($datePattern, $entry, $dates) && isset($dates[0])) {
                    $expItem['dates'] = trim($dates[0]);
                    // Remove the date from entry
                    $entry = str_replace($dates[0], '', $entry);
                }
                
                // Split remaining text into lines
                $lines = array_map('trim', explode("\n", $entry));
                
                // First non-empty line is typically company or position
                $firstLine = '';
                foreach ($lines as $index => $line) {
                    if (!empty($line)) {
                        $firstLine = $line;
                        unset($lines[$index]);
                        break;
                    }
                }
                
                // Try to separate company and position if combined
                if (strpos($firstLine, '|') !== false) {
                    $parts = array_map('trim', explode('|', $firstLine, 2));
                    if (count($parts) >= 2) {
                        $expItem['company'] = $parts[0];
                        $expItem['position'] = $parts[1];
                    }
                } elseif (stripos($firstLine, ' at ') !== false) {
                    $parts = array_map('trim', explode(' at ', $firstLine, 2));
                    if (count($parts) >= 2) {
                        $expItem['position'] = $parts[0];
                        $expItem['company'] = $parts[1];
                    }
                } else {
                    // If we can't split, assume it's the company name
                    $expItem['company'] = $firstLine;
                    
                    // Next non-empty line might be the position
                    foreach ($lines as $index => $line) {
                        if (!empty($line) && !preg_match('/^[•\-]/', $line)) {
                            $expItem['position'] = $line;
                            unset($lines[$index]);
                            break;
                        }
                    }
                }
                
                // Extract location if present
                $locationPattern = '/(?:in|at)\s+([^,•\n]+(?:,\s*[^,•\n]+)?)/i';
                foreach ($lines as $index => $line) {
                    if (preg_match($locationPattern, $line, $location) && isset($location[1])) {
                        $expItem['location'] = trim($location[1]);
                        unset($lines[$index]);
                        break;
                    }
                }
                
                // Remaining lines are likely responsibilities
                foreach ($lines as $line) {
                    $line = trim($line);
                    if (!empty($line)) {
                        // Clean up bullet points
                        $line = preg_replace('/^[•\-]\s*/', '', $line);
                        $expItem['responsibilities'][] = $line;
                    }
                }
                
                // Only add if we have at least a company name
                if (!empty($expItem['company'])) {
                    $experience[] = $expItem;
                }
            }
        }
        
        return $experience;
    }
    
    /**
     * Extract skills from resume text
     * 
     * @param string $text Resume text
     * @return array List of skills
     */
    private function extractSkills(string $text): array
    {
        $skills = [];
        
        // First look for a dedicated skills section
        $sections = $this->splitIntoSections($text);
        $skillsSection = $sections['skills'] ?? '';
        
        // Log for debugging
        Log::info("Skills section detection:", [
            'found_section' => !empty($skillsSection),
            'section_length' => strlen($skillsSection)
        ]);
        
        // Combine the skills section with the full text for better extraction
        $textToSearch = $skillsSection ?: $text;
        
        // Filter patterns to EXCLUDE from skills (phone numbers, names, etc.)
        $excludePatterns = [
            '/\d{5,}/', // Phone numbers and numeric sequences with 5+ digits
            '/\d{3,4}[\s\-]?\d{3,4}/', // Phone number patterns
            '/[A-Za-z]+\s[A-Za-z]+\s?\d+/', // Names with numbers
            '/\b[A-Z][a-z]+\s[A-Z][a-z]+\b/', // Typical name patterns (FirstName LastName)
        ];
        
        // Enhanced skills lists for specific industries - Computer Science, Finance, and Medical
        // Computer Science specific skills
        $csSkills = [
            // Programming Languages
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby", "Go", "Swift", "Kotlin", 
            "R", "MATLAB", "Scala", "Rust", "Perl", "Shell", "PowerShell", "Bash", "SQL", "NoSQL",
            // Web Development
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "jQuery", "Bootstrap", 
            "Material UI", "Tailwind CSS", "Django", "Flask", "Laravel", "Spring Boot", "ASP.NET",
            "REST API", "GraphQL", "JSON", "XML", "JWT", "OAuth", "Microservices", "PWA",
            // DevOps & Cloud
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins", "CI/CD", "Git", "GitHub",
            "GitLab", "Bitbucket", "Linux", "Nginx", "Apache", "Serverless", "Prometheus", "Grafana",
            // Data Science
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
            "Data Analysis", "Data Visualization", "Tableau", "Power BI", "Big Data", "Hadoop", "Spark",
            // Mobile Development
            "Android", "iOS", "React Native", "Flutter", "Xamarin", "Mobile Development", "App Development",
            // Databases
            "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server", "Redis", "Cassandra", "Firebase",
            // Other Technical
            "Agile", "Scrum", "Jira", "Confluence", "Testing", "Unit Testing", "Selenium", "Cypress", "TDD"
        ];
        
        // Finance specific skills
        $financeSkills = [
            // Analysis & Modeling
            "Financial Analysis", "Financial Modeling", "Forecasting", "Budgeting", "Valuation", 
            "DCF Analysis", "Equity Research", "Investment Analysis", "Portfolio Management", 
            "Risk Assessment", "Financial Planning", "Strategic Planning", "Scenario Analysis",
            // Accounting & Reporting
            "Financial Reporting", "GAAP", "IFRS", "Balance Sheet", "Income Statement", "Cash Flow", 
            "Audit", "Tax", "Bookkeeping", "Reconciliation", "Financial Statements", "Cost Accounting",
            "Variance Analysis", "SOX Compliance", "Revenue Recognition", "Accounts Payable", "Accounts Receivable",
            // Software & Tools
            "Excel", "Advanced Excel", "Macros", "VBA", "Tableau", "Power BI", "QuickBooks", "SAP",
            "Oracle Financials", "Bloomberg Terminal", "FactSet", "Capital IQ", "Microsoft Dynamics",
            // Banking & Investment
            "Investment Banking", "Commercial Banking", "Corporate Finance", "M&A", "Capital Markets",
            "Wealth Management", "Asset Management", "Credit Analysis", "Underwriting", "Private Equity",
            "Venture Capital", "IPO", "Due Diligence", "Trading", "Securities", "Derivatives",
            // Credentials & Methodologies
            "CFA", "CPA", "FRM", "Series 7", "Series 63", "ChFC", "CFP", "EA", "Six Sigma", "Lean"
        ];
        
        // Medical specific skills
        $medicalSkills = [
            // Clinical Skills
            "Patient Care", "Patient Assessment", "Vital Signs", "Diagnosis", "Treatment Planning", 
            "Medical Documentation", "Venepuncture", "Injections", "Wound Care", "CPR", "BLS", "ACLS", 
            "Emergency Medicine", "Triage", "Physical Examination", "Medication Administration",
            "Patient Monitoring", "Clinical Procedures", "Suturing", "Catheterization", "Intubation",
            // Medical Knowledge
            "Anatomy", "Physiology", "Pathology", "Pharmacology", "Microbiology", "Immunology", 
            "Biochemistry", "Genetics", "Disease Management", "Medical Terminology", "Differential Diagnosis",
            // Healthcare Systems
            "Electronic Medical Records", "EMR", "EHR", "EPIC", "Cerner", "Meditech", "Health Informatics", 
            "HIPAA", "Healthcare Compliance", "Medical Billing", "Coding", "ICD-10", "CPT", 
            "Hospital Management", "Public Health", "Telemedicine", "Care Coordination",
            // Specialties
            "Primary Care", "Internal Medicine", "Surgery", "Pediatrics", "Obstetrics", "Gynecology", 
            "Cardiology", "Neurology", "Oncology", "Psychiatry", "Radiology", "Anesthesiology",
            "Orthopedics", "Dermatology", "Ophthalmology", "Geriatrics", "Family Medicine",
            // Medical Research
            "Clinical Research", "Medical Writing", "Research Methodology", "Data Collection",
            "Clinical Trials", "Evidence-Based Medicine", "Biostatistics", "Literature Review"
        ];
        
        // Combine all skills for initial detection
        $allSpecificSkills = array_merge($csSkills, $financeSkills, $medicalSkills);
        
        // Generic professional skills that apply across fields
        $genericSkills = [
            // Communication
            "Communication", "Presentation Skills", "Public Speaking", "Writing", "Technical Writing",
            "Business Writing", "Documentation", "Reporting", "Email Communication",
            // Leadership
            "Leadership", "Management", "Team Leadership", "People Management", "Supervision",
            "Decision Making", "Strategic Thinking", "Delegation", "Mentoring", "Coaching",
            // Teamwork
            "Teamwork", "Collaboration", "Team Building", "Cross-functional Collaboration",
            "Remote Collaboration", "Virtual Teams", "Interpersonal Skills",
            // Problem Solving
            "Problem Solving", "Critical Thinking", "Analytical Skills", "Troubleshooting",
            "Root Cause Analysis", "Logical Reasoning", "Creative Problem Solving",
            // Other Professional
            "Time Management", "Organization", "Multitasking", "Prioritization", "Self-motivated",
            "Attention to Detail", "Adaptability", "Flexibility", "Initiative", "Customer Service",
            "Client Relations", "Negotiation", "Conflict Resolution", "Cultural Awareness"
        ];
        
        // Find exact matches from the predefined skills lists
        foreach (array_merge($allSpecificSkills, $genericSkills) as $skill) {
            // Look for the skill with word boundaries
            if (preg_match('/\b' . preg_quote($skill, '/') . '\b/i', $textToSearch)) {
                $skills[] = $skill;
            }
        }
        
        // Extract bullet-pointed skills (common in resumes)
        preg_match_all('/[•\-\*]\s*([A-Za-z0-9\'\"\s\+\#\/\&\.]+)(?:$|,|;|\.|and)/m', $textToSearch, $bulletMatches);
        if (!empty($bulletMatches[1])) {
            foreach ($bulletMatches[1] as $match) {
                $cleanedSkill = trim($match);
                
                // Skip if it matches any exclude patterns
                $shouldExclude = false;
                foreach ($excludePatterns as $pattern) {
                    if (preg_match($pattern, $cleanedSkill)) {
                        $shouldExclude = true;
                        break;
                    }
                }
                
                // Only add if reasonable length, not excluded, and not already added
                if (!$shouldExclude && strlen($cleanedSkill) > 2 && strlen($cleanedSkill) < 50 && !in_array($cleanedSkill, $skills)) {
                    $skills[] = $cleanedSkill;
                }
            }
        }
        
        // Look for common skill section formats like "Languages: Python, Java"
        preg_match_all('/([A-Za-z\s]+):\s*([A-Za-z0-9\s,\+\#\/\&\.]+)(?:$|\.)/m', $textToSearch, $sectionMatches);
        if (!empty($sectionMatches[1]) && !empty($sectionMatches[2])) {
            for ($i = 0; $i < count($sectionMatches[1]); $i++) {
                $category = trim($sectionMatches[1][$i]);
                // Check if this looks like a skills category
                if (in_array(strtolower($category), ['skills', 'technologies', 'languages', 'frameworks', 'tools', 'proficient in', 'expertise in'])) {
                    $skillList = $sectionMatches[2][$i];
                    // Split by common separators
                    $skillItems = preg_split('/[,;\/|•]+/', $skillList);
                    foreach ($skillItems as $item) {
                        $cleanedSkill = trim($item);
                        
                        // Skip if it matches any exclude patterns
                        $shouldExclude = false;
                        foreach ($excludePatterns as $pattern) {
                            if (preg_match($pattern, $cleanedSkill)) {
                                $shouldExclude = true;
                                break;
                            }
                        }
                        
                        if (!$shouldExclude && strlen($cleanedSkill) > 2 && strlen($cleanedSkill) < 50 && !in_array($cleanedSkill, $skills)) {
                            $skills[] = $cleanedSkill;
                        }
                    }
                }
            }
        }
        
        // Filter out any remaining items that match exclude patterns
        $filteredSkills = [];
        foreach ($skills as $skill) {
            $shouldExclude = false;
            foreach ($excludePatterns as $pattern) {
                if (preg_match($pattern, $skill)) {
                    $shouldExclude = true;
                    break;
                }
            }
            
            if (!$shouldExclude) {
                $filteredSkills[] = $skill;
            }
        }
        
        // Log extraction results
        Log::info("Skills extraction results:", [
            'skills_count' => count($filteredSkills),
            'first_few_skills' => array_slice($filteredSkills, 0, 5)
        ]);
        
        return array_unique($filteredSkills);
    }
    
    /**
     * Extract programming languages specifically
     */
    private function extractProgrammingLanguages(string $text, array $skills): array
    {
        $programmingLanguages = [];
        
        // Common programming languages to check for
        $languagesList = [
            'Java', 'C++', 'C#', 'Python', 'R', 'JavaScript', 'TypeScript', 'PHP', 'Ruby', 
            'Go', 'Swift', 'Kotlin', 'Rust', 'Scala', 'MATLAB', 'Perl',
            'SQL', 'HTML', 'CSS', 'Bash', 'PowerShell'
        ];
        
        // Check each language in the text
        foreach ($languagesList as $language) {
            if (stripos($text, $language) !== false) {
                $programmingLanguages[] = $language;
            }
        }
        
        // Also check if any of the extracted skills match programming languages
        foreach ($skills as $category => $skillList) {
            // Handle both string and array values
            if (is_array($skillList)) {
                foreach ($skillList as $skill) {
                    foreach ($languagesList as $language) {
                        if (is_string($skill) && stripos($skill, $language) !== false && !in_array($language, $programmingLanguages)) {
                            $programmingLanguages[] = $language;
                        }
                    }
                }
            } elseif (is_string($skillList)) {
                foreach ($languagesList as $language) {
                    if (stripos($skillList, $language) !== false && !in_array($language, $programmingLanguages)) {
                        $programmingLanguages[] = $language;
                    }
                }
            }
        }
        
        return array_unique($programmingLanguages);
    }
    
    /**
     * Extract languages from resume
     */
    private function extractLanguages(string $text): array
    {
        $languages = [];
        $sections = $this->splitIntoSections($text);
        
        if (!isset($sections['languages'])) {
            return $languages;
        }
        
        $languageText = $sections['languages'];
        
        // Common language proficiency levels
        $proficiencyLevels = [
            'Native' => 100,
            'Fluent' => 90,
            'Advanced' => 80,
            'Proficient' => 70,
            'Intermediate' => 50,
            'Basic' => 30,
            'Beginner' => 20
        ];
        
        // Common language names to validate against
        $validLanguages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Bengali', 'Dutch',
            'Swedish', 'Norwegian', 'Danish', 'Finnish', 'Polish', 'Czech', 'Slovak',
            'Hungarian', 'Romanian', 'Bulgarian', 'Greek', 'Turkish', 'Hebrew', 'Thai',
            'Vietnamese', 'Indonesian', 'Malay', 'Filipino', 'Urdu', 'Persian', 'Tamil'
        ];
        
        // Try to match language entries in different formats
        $patterns = [
            // Format: Language (Level)
            '/([A-Z][a-z]+)\s*(?:\(([^)]+)\))/m',
            // Format: Language: Level
            '/([A-Z][a-z]+):\s*([^,\n]+)/m',
            // Format: Language - Level
            '/([A-Z][a-z]+)\s*[-–]\s*([^,\n]+)/m',
            // Format: • Language - Level
            '/[•\-]\s*([A-Z][a-z]+)\s*[-–]\s*([^,\n]+)/m',
            // Format: Just language names
            '/[•\-]?\s*([A-Z][a-z]+)(?:\s|$)/m'
        ];
        
        foreach ($patterns as $pattern) {
            if (preg_match_all($pattern, $languageText, $matches, PREG_SET_ORDER)) {
                foreach ($matches as $match) {
                    if (!isset($match[1])) continue;
                    
                    $language = trim($match[1]);
                    
                    // Validate that this is actually a language name
                    if (!in_array($language, $validLanguages)) {
                        continue;
                    }
                    
                    $proficiency = isset($match[2]) ? trim($match[2]) : 'Fluent';
                    
                    // Convert text proficiency to percentage
                    $percentage = 90; // Default to high proficiency if not specified
                    
                    foreach ($proficiencyLevels as $level => $value) {
                        if (stripos($proficiency, $level) !== false) {
                            $percentage = $value;
                            break;
                        }
                    }
                    
                    // Look for percentage in the proficiency string
                    if (preg_match('/(\d+)%/', $proficiency, $percentMatch) && isset($percentMatch[1])) {
                        $percentage = min(100, max(0, intval($percentMatch[1])));
                    }
                    
                    $languages[$language] = $percentage;
                }
            }
        }
        
        return $languages;
    }
    
    /**
     * Extract workshops/training from resume
     */
    private function extractWorkshops(string $text): array
    {
        $workshops = [];
        
        // Look for the WORKSHOPS section
        if (preg_match('/WORKSHOPS(.*?)(?:INTEREST|LANGUAGE|EXPERTISE|EDUCATION|$)/si', $text, $matches)) {
            $workshopText = $matches[1];
            
            // Split the text into lines and process each workshop
            $lines = preg_split('/\r\n|\r|\n/', $workshopText);
            foreach ($lines as $line) {
                $line = trim($line);
                if (!empty($line) && strlen($line) > 5) {
                    $workshops[] = $line;
                }
            }
        }
        
        return $workshops;
    }
    
    /**
     * Extract interests from resume
     */
    private function extractInterests(string $text): array
    {
        $interests = [];
        
        // Look for the INTEREST section
        if (preg_match('/INTEREST(.*?)(?:REFERENCE|WORKSHOPS|LANGUAGE|EXPERTISE|EDUCATION|$)/si', $text, $matches)) {
            $interestText = $matches[1];
            
            // Extract interests - they are often listed as words or short phrases
            $lines = preg_split('/\r\n|\r|\n/', $interestText);
            foreach ($lines as $line) {
                $line = trim($line);
                if (!empty($line)) {
                    $interests[] = $line;
                }
            }
        }
        
        return $interests;
    }
    
    /**
     * Extract references from resume
     */
    private function extractReferences(string $text): array
    {
        $references = [];
        
        // Look for the REFERENCE section
        if (preg_match('/REFERENCE(.*?)$/si', $text, $matches)) {
            $referenceText = $matches[1];
            
            // Extract individual references
            $refPattern = '/([A-Z][A-Z\s]+[A-Z.]).*?(?:\d{2,3}[-\.\s]??\d{3}[-\.\s]??\d{3,4}|\d{3}[-\.\s]??\d{7})/s';
            preg_match_all($refPattern, $referenceText, $refMatches, PREG_SET_ORDER);
            
            foreach ($refMatches as $refMatch) {
                $refName = trim($refMatch[1]);
                $refDetails = trim($refMatch[0]);
                
                $reference = [
                    'name' => $refName,
                    'details' => $refDetails
                ];
                
                // Extract position and affiliation
                $positionPattern = '/(?:' . preg_quote($refName, '/') . ')\s+(.*?)(?=at|P:|$)/i';
                if (preg_match($positionPattern, $refDetails, $posMatch)) {
                    $reference['position'] = trim($posMatch[1]);
                }
                
                // Extract affiliation
                $affiliationPattern = '/at\s+(.*?)(?=P:|$)/i';
                if (preg_match($affiliationPattern, $refDetails, $affMatch)) {
                    $reference['affiliation'] = trim($affMatch[1]);
                }
                
                // Extract phone
                $phonePattern = '/P:?\s*(\d{2,3}[-\.\s]??\d{3}[-\.\s]??\d{3,4}|\d{3}[-\.\s]??\d{7})/i';
                if (preg_match($phonePattern, $refDetails, $phoneMatch)) {
                    $reference['phone'] = trim($phoneMatch[1]);
                }
                
                $references[] = $reference;
            }
        }
        
        return $references;
    }
} 