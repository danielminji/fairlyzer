<?php

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// Define resume files
$resumeFiles = [
    // 'Computer Science' => 'C:/laragon/www/resume/storage/app/public/resumes/computerscienceResume.pdf',
    // 'Finance' => 'C:/laragon/www/resume/storage/app/public/resumes/financeResume.pdf',
    'Medical' => 'C:/laragon/www/resume/public/storage/resumes/medicalResume.pdf' // Corrected path
];

// Parse each resume
$service = app('App\Services\ResumeParserService');
$parser = new \Smalot\PdfParser\Parser(); // Added for direct parsing

foreach ($resumeFiles as $type => $filePath) {
    if (!file_exists($filePath)) {
        echo "File not found: {$filePath}\n";
        continue;
    }

    echo "\n\n==================================================================\n";
    echo "RAW TEXT EXTRACTION FOR {$type} RESUME: {$filePath}\n";
    echo "==================================================================\n";

    try {
        // Attempt to use pdftotext for better layout preservation
        $escapedFilePath = escapeshellarg($filePath);
        // The command: pdftotext -layout {filePath} -
        // The '-' at the end tells pdftotext to output to stdout
        $pdftotextCommand = "pdftotext -layout " . $escapedFilePath . " -";
        
        $text = shell_exec($pdftotextCommand);

        if ($text === null || trim($text) === '') {
            // pdftotext might not be installed, command failed, or returned empty output
            if ($text === null) {
                echo "shell_exec('{$pdftotextCommand}') failed. pdftotext might not be installed or not in PATH.\n";
            } else {
                echo "pdftotext command executed but returned empty output.\n";
            }
            echo "Falling back to Smalot\PdfParser\Parser.\n";
            // Fallback to Smalot parser
            $pdf = $parser->parseFile($filePath);
            $text = $pdf->getText();
        } else {
            echo "Successfully extracted text using pdftotext.\n";
        }

        echo "RAW EXTRACTED TEXT:\n";
        echo "------------------------------------------------------------------\n";
        echo $text;
        echo "\n------------------------------------------------------------------\n";
    } catch (Exception $e) {
        echo "Error extracting text with Smalot\PdfParser: " . $e->getMessage() . "\n";
    }

    // Commenting out the rest of the analysis for now to focus on raw text
    /*
    echo "\n\n==================================================================\n";
    echo "ANALYZING {$type} RESUME: {$filePath}\n";
    echo "==================================================================\n";
    
    echo "\nENHANCED PARSER RESULTS:\n";
    echo "==================================================================\n";
    
    $enhancedResult = $service->parseResumeWithEnhanced($filePath);
    
    if (empty($enhancedResult)) {
        echo "Failed to parse resume with enhanced parser.\n";
    } else {
        if (isset($enhancedResult['error'])) {
            echo "Error with enhanced parser: " . $enhancedResult['error'] . "\n";
        }
        
        echo "Primary Field: " . ($enhancedResult['primary_field'] ?? 'unknown') . "\n\n";
        
        echo "CONTACT INFO:\n";
        if (!empty($enhancedResult['contact_info'])) {
            foreach ($enhancedResult['contact_info'] as $key => $value) {
                if (!empty($value)) {
                    echo "- {$key}: " . substr(str_replace(["\n", "\r"], " ", $value), 0, 50) . "\n";
                }
            }
        } else {
            echo "No contact info found.\n";
        }
        
        echo "\nSKILLS CATEGORIES:\n";
        if (isset($enhancedResult['skills']['categorized']) && is_array($enhancedResult['skills']['categorized'])) {
            foreach ($enhancedResult['skills']['categorized'] as $category => $skills) {
                if (is_array($skills) && !empty($skills)) {
                    echo "- {$category}: " . count($skills) . " skills - " . implode(", ", array_slice($skills, 0, 3)) . "...\n";
                }
            }
        } else {
            echo "No categorized skills found.\n";
        }
        
        echo "\nEDUCATION:\n";
        if (!empty($enhancedResult['education'])) {
            foreach ($enhancedResult['education'] as $edu) {
                echo "- " . ($edu['degree'] ?? 'Unknown degree') . " from " . ($edu['institution'] ?? 'Unknown institution') . "\n";
            }
        } else {
            echo "No education history found.\n";
        }
        
        echo "\nEXPERIENCE:\n";
        if (!empty($enhancedResult['experience'])) {
            foreach ($enhancedResult['experience'] as $exp) {
                echo "- " . ($exp['title'] ?? 'Unknown position') . " at " . ($exp['company'] ?? 'Unknown company') . "\n";
            }
        } else {
            echo "No work experience found.\n";
        }
        
        echo "\nJOB RECOMMENDATIONS:\n";
        if (!empty($enhancedResult['job_recommendations'])) {
            foreach (array_slice($enhancedResult['job_recommendations'], 0, 3) as $job) {
                echo "- " . ($job['role'] ?? 'Unknown role') . " (Match: " . ($job['match_score'] ?? 0) . "%)\n";
            }
        } else {
            echo "No job recommendations found.\n";
        }
    }
    */
}

echo "\n\nAnalysis complete.\n"; 