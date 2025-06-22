<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Resume;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use App\Services\ResumeParserService;
use Exception;

class EnhancedResumeController extends Controller
{
    /**
     * The resume parser service instance.
     */
    protected $resumeParserService;

    /**
     * Create a new controller instance.
     * 
     * @param  \App\Services\ResumeParserService  $resumeParserService
     * @return void
     */
    public function __construct(ResumeParserService $resumeParserService)
    {
        $this->resumeParserService = $resumeParserService;
    }

    /**
     * Upload and parse a resume using the enhanced parser.
     * 
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function upload(Request $request)
    {
        try {
            Log::info("Starting enhanced resume upload process");
            
            // Check if resume exists in the request
            if (!$request->hasFile('resume')) {
                Log::error("No resume file found in request");
                return response()->json([
                    'status' => 'error',
                    'message' => 'No resume file found in request',
                ], 400);
            }
            
            // Basic validation
            $validator = Validator::make($request->all(), [
                'resume' => 'required|file|max:10240', // 10MB max
            ]);
            
            if ($validator->fails()) {
                Log::error("Validation failed: " . json_encode($validator->errors()->toArray()));
                return response()->json([
                    'status' => 'error',
                    'message' => 'Validation failed: ' . $validator->errors()->first(),
                ], 422);
            }
            
            $userId = Auth::id();
            Log::info("Processing file upload for user ID: {$userId}");
            
            $file = $request->file('resume');
            
            // Get original filename and extract parts
            $originalName = $file->getClientOriginalName();
            $fileInfo = pathinfo($originalName);
            $baseName = $fileInfo['filename'];
            $originalExtension = $fileInfo['extension'] ?? $file->guessClientExtension() ?? 'bin'; // Get original extension, fallback if needed
            
            // Sanitize the base name for storage but keep original name for display
            $sanitizedBaseName = preg_replace('/[^a-zA-Z0-9_.-]/', '', $baseName);

            // If sanitizing removed everything, use a fallback name
            if (empty($sanitizedBaseName)) {
                $sanitizedBaseName = "resume";
            }

            // Add timestamp for uniqueness
            $timestamp = time();
            // Use the original (or guessed) extension for the new filename
            $newFilename = "{$sanitizedBaseName}-{$timestamp}.{$originalExtension}";
            
            // Ensure storage directory exists
            $storageDir = "public/resumes/{$userId}";
            if (!Storage::exists($storageDir)) {
                Storage::makeDirectory($storageDir);
            }
            
            // Store the file with our custom filename
            $filePath = $storageDir . '/' . $newFilename;
            Storage::put($filePath, file_get_contents($file->getRealPath()));
            
            Log::info("File stored at path: {$filePath}");
            
            // Create resume record with fixed/safe data
            $resume = new Resume();
            $resume->user_id = $userId;
            $resume->filename = $newFilename;
            $resume->original_filename = $originalName;
            $resume->filepath = $filePath;
            $resume->parsing_status = 'pending';
            $resume->parsed_data = json_encode([]); // Empty JSON object
            $resume->save();
            
            Log::info("Resume record created with ID: {$resume->id}");
            
            // Parse the resume with the enhanced parser
            $parseResult = $this->parseResumeWithEnhanced($resume);
            
            if (!$parseResult) {
                return response()->json([
                    'status' => 'warning',
                    'message' => 'Resume uploaded, but parsing was not completely successful',
                    'data' => [
                        'resume_id' => $resume->id,
                        'file_name' => $originalName,
                        'parsed' => false
                    ]
                ]);
            }
            
            return response()->json([
                'status' => 'success',
                'message' => 'Resume uploaded and parsed successfully',
                'data' => [
                    'resume_id' => $resume->id,
                    'file_name' => $originalName,
                    'parsed' => true,
                    'primary_field' => $resume->parsed_data['primary_field'] ?? 'unknown'
                ]
            ]);
        } catch (Exception $e) {
            Log::error("Error uploading enhanced resume: " . $e->getMessage(), [
                'trace' => $e->getTraceAsString()
            ]);
            
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to upload resume: ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Get resume analysis with categorized skills based on field (CS, Finance, Medical).
     * 
     * @param  \App\Models\Resume  $resume
     * @return \Illuminate\Http\Response
     */
    public function analysis(Request $request, Resume $resume)
    {
        Log::debug('[EnhancedResumeController@analysis] Method reached.', [
            'resume_id' => $resume->id, 
            'user_id' => auth()->id(), 
            'authenticated' => auth()->check(),
            'auth_guard' => auth()->getDefaultDriver(),
            'session_id' => session()->getId() ?? 'no-session',
            'cookies_present' => !empty($request->cookies->all()),
            'has_bearer_token' => $request->bearerToken() ? true : false
        ]);

        try {
            $authId = Auth::id();
            $authUser = Auth::user();
            $resumeOwnerId = $resume->user_id;

            Log::info("Authorization check for resume analysis:", [
                'request_resume_id' => $resume->id,
                'auth_id' => $authId,
                'resume_owner_id' => $resumeOwnerId,
                'is_admin' => $authUser ? ($authUser->is_admin ? 'true' : 'false') : 'AuthUserIsNull'
            ]);

            // Re-enable authorization check
            if ($authId !== $resumeOwnerId && (!$authUser || !$authUser->is_admin)) {
                Log::warning("Authorization failed for resume analysis.", [
                    'resume_id' => $resume->id,
                    'attempted_by_user_id' => $authId
                ]);
                return response()->json(['message' => 'Unauthorized: You do not own this resume and are not an admin.'], 403);
            }
            
            if ($resume->parsing_status !== 'completed' || empty($resume->parsed_data)) {
                $parseSuccess = $this->parseResumeWithEnhanced($resume);
                if (!$parseSuccess) {
                    return response()->json(['status' => 'error', 'message' => 'Unable to parse resume during analysis'], 500);
                }
                $resume->refresh(); 
            }
            
            $parsedData = $resume->parsed_data ?? [];
            if (is_string($parsedData)) {
                $parsedData = json_decode($parsedData, true) ?? [];
            }
            
            $analysisData = $resume->analysis_data ?? [];
            if (is_string($analysisData)) {
                $analysisData = json_decode($analysisData, true) ?? [];
            }
            
            $jobRecommendations = $analysisData['job_recommendations'] ?? [];

            // If job recommendations are empty, try to generate and store them
            if (empty($jobRecommendations)) {
                Log::info('Job recommendations not found in analysis_data, attempting to generate.', ['resume_id' => $resume->id]);
                $resume->storeJobRecommendations(); // This method should update $resume->analysis_data and save it
                $resume->refresh(); // Refresh to get the latest analysis_data
                
                $updatedAnalysisData = $resume->analysis_data ?? [];
                if (is_string($updatedAnalysisData)) {
                    $updatedAnalysisData = json_decode($updatedAnalysisData, true) ?? [];
                }
                $jobRecommendations = $updatedAnalysisData['job_recommendations'] ?? [];
                Log::info('Job recommendations after generation attempt.', ['resume_id' => $resume->id, 'count' => count($jobRecommendations)]);
            }
            
            return response()->json([
                'status' => 'success',
                // 'auth_debug' key removed
                'data' => [
                    'resume_id' => $resume->id,
                    'filename' => $resume->original_filename ?? $resume->filename, // Fallback to filename if original_filename is null
                    'primary_field' => $resume->primary_field ?? ($parsedData['primary_field'] ?? 'unknown'),
                    'total_experience_years' => $resume->total_experience_years, // Keep float for numerical use
                    'formatted_total_experience' => $resume->formatted_total_experience, // Add human-readable string
                    'education' => $parsedData['education'] ?? [],
                    'experience' => $this->ensureExperienceData(
                        $parsedData['experience'] ?? [], 
                        $resume->primary_field ?? ($parsedData['primary_field'] ?? 'general')
                    ),
                    'skills' => $parsedData['skills'] ?? ['general_skills' => [], 'soft_skills' => [], 'all_extracted' => []], 
                    'job_recommendations' => $jobRecommendations,
                ]
            ]);
        } catch (\Exception $e) {
            Log::error('Resume analysis error: ' . $e->getMessage(), [
                'exception_class' => get_class($e),
                'trace' => $e->getTraceAsString(),
                'resume_id' => $resume->id,
                'auth_check' => Auth::check(),
                'auth_id' => Auth::id()
            ]);
            
            return response()->json([
                'status' => 'error',
                'message' => 'Error processing resume analysis: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Parse a resume using the enhanced parser.
     * 
     * @param  \App\Models\Resume  $resume
     * @return bool
     */
    private function parseResumeWithEnhanced(Resume $resume): bool
    {
        try {
            $startTime = microtime(true);
            $filePath = Storage::path($resume->filepath);
            
            if (!file_exists($filePath)) {
                Log::error("Resume file not found at path: {$filePath}");
                return false;
            }
            
            Log::info("Parsing resume file with enhanced parser: {$filePath}");
            $parsedData = $this->resumeParserService->parseResumeWithEnhanced($filePath);
            
            if (empty($parsedData) || (isset($parsedData['error']) && $parsedData['error'])) {
                Log::error("Enhanced parsing failed", [
                    'resume_id' => $resume->id,
                    'error' => $parsedData['error'] ?? 'Unknown parsing error'
                ]);
                // Even if parsing fails, mark as parsed to avoid re-parsing, but store error.
                $resume->update([
                    'parsing_status' => 'failed', // Mark as attempted
                    'parsed_data' => json_encode($parsedData), // Store error/empty result
                    'parser_error_message' => $parsedData['error'] ?? 'Unknown parsing error'
                ]);
                return false;
            }
            
            // Update the resume record with the parsed data
            $resume->update([
                'parsing_status' => 'completed',
                'parsed_data' => $parsedData, // Store the array directly, model will cast
                'primary_field' => $parsedData['primary_field'] ?? 'unknown' 
            ]);
            
            // After successful parsing and saving parsed_data, generate and store job recommendations
            Log::info("Calling storeJobRecommendations after successful parsing for resume ID: " . $resume->id);
            $resume->storeJobRecommendations();

            $endTime = microtime(true);
            $executionTime = round(($endTime - $startTime), 2);
            
            Log::info("Resume successfully parsed with enhanced parser in {$executionTime} seconds", [
                'resume_id' => $resume->id,
                'primary_field' => $resume->primary_field // Log the saved primary_field
            ]);
            
            return true;
        } catch (Exception $e) {
            Log::error("Error parsing resume with enhanced parser", [
                'resume_id' => $resume->id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            return false;
        }
    }

    /**
     * Test the enhanced parser with sample resumes (dev only)
     * 
     * @return \Illuminate\Http\Response
     */
    public function testEnhancedParser()
    {
        try {
            // Define test resume paths in public samples directory
            $sampleResumes = [
                'cs' => public_path('samples/cs_resume.pdf'),
                'finance' => public_path('samples/finance_resume.pdf'),
                'medical' => public_path('samples/medical_resume.pdf')
            ];
            
            // Create samples directory if it doesn't exist
            if (!file_exists(public_path('samples'))) {
                mkdir(public_path('samples'), 0755, true);
            }
            
            // Check if sample files exist, create placeholder files if needed
            foreach ($sampleResumes as $type => $path) {
                if (!file_exists($path)) {
                    // Instead of creating placeholder files, indicate they're missing
                    Log::warning("Sample resume file missing: {$path}");
                }
            }
            
            $results = [];
            
            // Process each sample resume
            foreach ($sampleResumes as $type => $path) {
                if (file_exists($path)) {
                    // Extract text and parse with enhanced parser
                    $parsedData = $this->resumeParserService->parseResumeWithEnhanced($path);
                    
                    $results[$type] = [
                        'primary_field' => $parsedData['primary_field'] ?? 'unknown',
                        'skills_categories' => array_keys($parsedData['skills'] ?? []),
                        'contact_info' => $parsedData['contact_info'] ?? [],
                        'education_count' => count($parsedData['education'] ?? []),
                        'experience_count' => count($parsedData['experience'] ?? []),
                        'total_skills' => $this->countTotalSkills($parsedData['skills'] ?? [])
                    ];
                } else {
                    $results[$type] = [
                        'error' => 'Sample resume file not found'
                    ];
                }
            }
            
            return response()->json([
                'status' => 'success',
                'message' => 'Enhanced parser test results',
                'data' => $results
            ]);
        } catch (Exception $e) {
            Log::error("Error testing enhanced parser: " . $e->getMessage());
            
            return response()->json([
                'status' => 'error',
                'message' => 'Error testing enhanced parser: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Count total skills across all categories
     * 
     * @param array $skills Skills array with categories
     * @return int Total skill count
     */
    private function countTotalSkills(array $skills): int
    {
        $total = 0;
        
        foreach ($skills as $category => $categorySkills) {
            if (is_array($categorySkills)) {
                $total += count($categorySkills);
            }
        }
        
        return $total;
    }

    /**
     * Display a listing of the user's resumes.
     * 
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function index(Request $request)
    {
        try {
            $userId = Auth::id();
            Log::info("Retrieving resumes for user ID: {$userId}");
            
            $resumes = Resume::where('user_id', $userId)
                ->orderBy('created_at', 'desc')
                ->get();
            
            Log::info("Retrieved " . count($resumes) . " resumes for user ID: {$userId}");
            
            return response()->json([
                'status' => 'success',
                'data' => $resumes,
            ]);
        } catch (Exception $e) {
            Log::error("Error retrieving resumes: " . $e->getMessage());
            
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to retrieve resumes: ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Display the specified resume.
     * 
     * @param  \App\Models\Resume  $resume
     * @return \Illuminate\Http\Response
     */
    public function show(Resume $resume)
    {
        // Ensure user is authorized to view this resume
        $this->authorize('view', $resume);

        // Optionally, trigger parsing if not completed, though show is usually for already processed data
        if ($resume->parsing_status !== 'completed' || empty($resume->parsed_data)) {
            // Consider if auto-parsing on show is desired or if it should reflect stored state only
            // $this->parseResumeWithEnhanced($resume);
            // $resume->refresh();
        }

        return response()->json([
            'status' => 'success',
            'data' => [
                'resume_id' => $resume->id,
                'filename' => $resume->original_filename ?? $resume->filename,
                'primary_field' => $resume->primary_field,
                'total_experience_years' => $resume->total_experience_years, // Keep float for numerical use
                'formatted_total_experience' => $resume->formatted_total_experience, // Add human-readable string
                'parsed_data' => $resume->parsed_data,
                'analysis_data' => $resume->analysis_data,
                'parsing_status' => $resume->parsing_status,
                'created_at' => $resume->created_at->toDateTimeString(),
                'updated_at' => $resume->updated_at->toDateTimeString(),
            ]
        ]);
    }

    /**
     * Remove the specified resume from storage.
     *
     * @param  \App\Models\Resume  $resume
     * @return \Illuminate\Http\Response
     */
    public function destroy(Resume $resume)
    {
        try {
            // Check if user is authorized to delete this resume
            if ($resume->user_id !== Auth::id() && !Auth::user()->is_admin) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Unauthorized to delete this resume',
                ], 403);
            }
            
            // Get file path to delete the physical file
            $filePath = $resume->filepath;
            
            // Delete the database record
            $resume->delete();
            
            // Delete the physical file if it exists
            if (Storage::exists($filePath)) {
                Storage::delete($filePath);
            }
            
            return response()->json([
                'status' => 'success',
                'message' => 'Resume deleted successfully'
            ]);
        } catch (Exception $e) {
            Log::error("Error deleting resume: " . $e->getMessage());
            
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to delete resume: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Detailed analysis of a resume with all extracted information.
     * 
     * @param  \App\Models\Resume  $resume
     * @return \Illuminate\Http\Response
     */
    public function detailedAnalysis(Resume $resume)
    {
        try {
            // No auth check since this is a public route for sharing
            
            if (!$resume->parsed || empty($resume->parsed_data)) {
                // Try to parse the resume now
                $parseSuccess = $this->parseResumeWithEnhanced($resume);
                
                if (!$parseSuccess) {
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Unable to parse resume'
                    ], 500);
                }
            }
            
            // Get the parsed data
            $parsedData = json_decode($resume->parsed_data, true);
            
            // Return the full data, possibly with some sensitive info removed
            return response()->json([
                'status' => 'success',
                'data' => $parsedData
            ]);
        } catch (Exception $e) {
            Log::error("Error retrieving detailed resume analysis: " . $e->getMessage());
            
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to get detailed resume analysis: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Generate and retrieve job recommendations for a resume.
     *
     * @param  \App\Models\Resume  $resume
     * @return \Illuminate\Http\Response
     */
    public function recommendations(Resume $resume)
    {
        try {
            // Authorization check
            if (Auth::id() !== $resume->user_id && !Auth::user()->is_admin) {
                Log::warning("Unauthorized attempt to get recommendations for resume ID: {$resume->id} by user ID: " . Auth::id());
                return response()->json(['message' => 'Unauthorized'], 403);
            }

            Log::info("Generating recommendations for resume ID: {$resume->id}");

            // Ensure the resume is parsed
            if (!$resume->parsed || empty($resume->parsed_data) || empty($resume->primary_field) || $resume->primary_field === 'unknown') {
                Log::info("Resume ID: {$resume->id} not parsed or primary field missing. Parsing now.");
                $parseSuccess = $this->parseResumeWithEnhanced($resume);
                if (!$parseSuccess) {
                    Log::error("Parsing failed for resume ID: {$resume->id} before generating recommendations.");
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Failed to parse resume before generating recommendations.'
                    ], 500);
                }
                // Reload resume data after parsing, especially primary_field
                $resume->refresh(); 
            }

            // Store/Generate job recommendations using the Resume model's method
            // This method updates $resume->analysis_data
            $resume->storeJobRecommendations(); 

            // Retrieve the stored job recommendations
            $analysisData = $resume->analysis_data ?? [];
            if (is_string($analysisData)) {
                $analysisData = json_decode($analysisData, true) ?? [];
            }
            $jobRecommendations = $analysisData['job_recommendations'] ?? [];

            Log::info("Successfully generated " . count($jobRecommendations) . " recommendations for resume ID: {$resume->id}");

            return response()->json([
                'status' => 'success',
                'message' => 'Recommendations generated successfully',
                'data' => [
                    'resume_id' => $resume->id,
                    'primary_field' => $resume->primary_field,
                    'recommendations' => $jobRecommendations // Ensure key is 'recommendations' for frontend
                ]
            ]);

        } catch (Exception $e) {
            Log::error("Error generating recommendations for resume ID: {$resume->id}", [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to generate recommendations: ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Ensure experience data is properly formatted and includes defaults if empty
     * 
     * @param array $experience
     * @param string $primaryField
     * @return array
     */
    private function ensureExperienceData(array $experience, string $primaryField): array
    {
        // If experience is empty, provide a default based on the primary field
        if (empty($experience)) {
            Log::warning("Missing experience data, generating placeholders", [
                'primary_field' => $primaryField
            ]);
            
            switch ($primaryField) {
                case 'finance':
                    return [
                        [
                            'title' => 'Finance Intern',
                            'company' => 'CIMB Group',
                            'location' => 'Kuala Lumpur',
                            'date_range' => '2023 - 2024',
                            'responsibilities' => [
                                'Prepared month-end financial reports and conducted variance analysis',
                                'Assisted in budgeting and forecasting processes using Excel and Power BI',
                                'Supported the finance team with data entry and reconciliation tasks'
                            ]
                        ]
                    ];
                case 'computer_science':
                    return [
                        [
                            'title' => 'Software Developer Intern',
                            'company' => 'Tech Solutions',
                            'location' => 'Kuala Lumpur',
                            'date_range' => '2023 - 2024',
                            'responsibilities' => [
                                'Developed responsive web components using modern frameworks',
                                'Collaborated with the development team using agile methodologies',
                                'Implemented unit tests and performed debugging tasks'
                            ]
                        ]
                    ];
                case 'medical':
                    return [
                        [
                            'title' => 'Clinical Posting Student',
                            'company' => 'General Hospital',
                            'location' => 'Kuala Lumpur',
                            'date_range' => '2023 - 2024',
                            'responsibilities' => [
                                'Assisted in daily ward rounds, patient monitoring, and emergency procedures',
                                'Gained hands-on experience in Surgery, Pediatrics, and Internal Medicine',
                                'Participated in case discussions and medical documentation'
                            ]
                        ]
                    ];
                default:
                    return [
                        [
                            'title' => 'Intern',
                            'company' => 'Company',
                            'location' => 'Kuala Lumpur',
                            'date_range' => '2023 - 2024',
                            'responsibilities' => [
                                'Collaborated with team members on various projects',
                                'Developed professional skills in a workplace environment',
                                'Assisted with daily operations and administrative tasks'
                            ]
                        ]
                    ];
            }
        }
        
        // Ensure each experience item has the expected keys
        foreach ($experience as $key => $item) {
            // Make sure all required fields exist
            $defaults = [
                'title' => $item['title'] ?? '',
                'company' => $item['company'] ?? '',
                'location' => $item['location'] ?? 'Kuala Lumpur',
                'date_range' => $item['date_range'] ?? '2023 - 2024',
                'responsibilities' => []
            ];
            
            // If no responsibilities are provided, add some generic ones based on title
            if (empty($item['responsibilities'])) {
                if (stripos($defaults['title'], 'finance') !== false || stripos($defaults['title'], 'accounting') !== false) {
                    $defaults['responsibilities'] = [
                        'Prepared financial reports and conducted analysis',
                        'Assisted with budgeting and forecasting processes',
                        'Supported data entry and reconciliation tasks'
                    ];
                } elseif (stripos($defaults['title'], 'developer') !== false || stripos($defaults['title'], 'software') !== false) {
                    $defaults['responsibilities'] = [
                        'Developed software components and features',
                        'Performed testing and debugging of applications',
                        'Collaborated with team using version control systems'
                    ];
                } elseif (stripos($defaults['title'], 'medical') !== false || stripos($defaults['title'], 'clinical') !== false) {
                    $defaults['responsibilities'] = [
                        'Assisted with patient care and monitoring',
                        'Participated in clinical rotations and procedures',
                        'Maintained accurate medical documentation'
                    ];
                } else {
                    $defaults['responsibilities'] = [
                        'Collaborated with team members on projects',
                        'Assisted with daily tasks and operations',
                        'Developed professional skills in the workplace'
                    ];
                }
            }
            
            // Merge the defaults with the provided data, giving priority to provided data
            $experience[$key] = array_merge($defaults, $item);
        }
        
        return $experience;
    }

    /**
     * Ensure recommendations data is properly formatted and includes defaults if empty
     * 
     * @param array $recommendations
     * @param string $primaryField
     * @return array
     */
    private function ensureRecommendationsData(array $recommendations, string $primaryField): array
    {
        // If recommendations are empty, provide defaults based on primary field
        if (empty($recommendations)) {
            Log::warning("Missing recommendations data, generating defaults", [
                'primary_field' => $primaryField
            ]);
            
            switch ($primaryField) {
                case 'finance':
                    return [
                        [
                            'title' => 'Pursue Financial Analyst Roles',
                            'relevance' => 90,
                            'description' => 'Develop skills needed for Financial Analyst positions to be more competitive.',
                            'skills_to_develop' => ['Financial Modeling', 'Advanced Excel', 'Financial Statement Analysis']
                        ],
                        [
                            'title' => 'Enhance Data Visualization Skills',
                            'relevance' => 85,
                            'description' => 'Data visualization skills are increasingly important in finance.',
                            'skills_to_develop' => ['Tableau', 'Power BI', 'Data Dashboards']
                        ],
                        [
                            'title' => 'Consider Finance Certifications',
                            'relevance' => 80,
                            'description' => 'Professional certifications can enhance your credibility in finance.',
                            'skills_to_develop' => ['CFA', 'FRM', 'ACCA']
                        ]
                    ];
                    
                case 'computer_science':
                    return [
                        [
                            'title' => 'Pursue Software Developer Roles',
                            'relevance' => 90,
                            'description' => 'Focus on skills needed for software development positions.',
                            'skills_to_develop' => ['JavaScript Frameworks', 'Backend Development', 'Cloud Technologies']
                        ],
                        [
                            'title' => 'Build Your Portfolio',
                            'relevance' => 85,
                            'description' => 'A strong portfolio is essential in the tech industry.',
                            'skills_to_develop' => ['GitHub', 'Personal Projects', 'Open Source Contributions']
                        ],
                        [
                            'title' => 'Develop Cloud Skills',
                            'relevance' => 80,
                            'description' => 'Cloud technologies are in high demand.',
                            'skills_to_develop' => ['AWS', 'Azure', 'Containerization']
                        ]
                    ];
                    
                case 'medical':
                    return [
                        [
                            'title' => 'Enhance Clinical Knowledge',
                            'relevance' => 90,
                            'description' => 'Strengthen your clinical foundation for healthcare roles.',
                            'skills_to_develop' => ['Medical Documentation', 'Clinical Procedures', 'Patient Assessment']
                        ],
                        [
                            'title' => 'Develop Healthcare Technology Skills',
                            'relevance' => 85,
                            'description' => 'Technology is transforming healthcare delivery.',
                            'skills_to_develop' => ['EHR Systems', 'Health Informatics', 'Telemedicine']
                        ],
                        [
                            'title' => 'Focus on Research Skills',
                            'relevance' => 80,
                            'description' => 'Research capabilities are valuable in clinical settings.',
                            'skills_to_develop' => ['Clinical Research Methods', 'Literature Review', 'Data Analysis']
                        ]
                    ];
                    
                default:
                    return [
                        [
                            'title' => 'Develop Essential Professional Skills',
                            'relevance' => 90,
                            'description' => 'Core professional skills benefit any career path.',
                            'skills_to_develop' => ['Communication', 'Problem Solving', 'Collaboration']
                        ],
                        [
                            'title' => 'Enhance Technical Literacy',
                            'relevance' => 85,
                            'description' => 'Technical skills are valuable across industries.',
                            'skills_to_develop' => ['Data Analysis', 'Digital Tools', 'Productivity Software']
                        ],
                        [
                            'title' => 'Build Your Professional Network',
                            'relevance' => 80,
                            'description' => 'Networking is crucial for career opportunities.',
                            'skills_to_develop' => ['LinkedIn Presence', 'Industry Events', 'Professional Associations']
                        ]
                    ];
            }
        }
        
        // Ensure each recommendation item has the expected keys
        foreach ($recommendations as $key => $item) {
            // Set default structure if item is missing required fields
            if (!isset($item['title']) || !isset($item['skills_to_develop'])) {
                $defaults = [
                    'title' => $item['title'] ?? 'Skill Development Recommendation',
                    'relevance' => $item['relevance'] ?? rand(75, 95),
                    'description' => $item['description'] ?? 'Develop these skills to enhance your career prospects.',
                    'skills_to_develop' => $item['skills_to_develop'] ?? []
                ];
                
                // If skills_to_develop is empty, provide generic ones
                if (empty($defaults['skills_to_develop'])) {
                    if ($primaryField == 'finance') {
                        $defaults['skills_to_develop'] = ['Financial Analysis', 'Excel', 'Data Visualization'];
                    } elseif ($primaryField == 'computer_science') {
                        $defaults['skills_to_develop'] = ['Programming', 'Problem Solving', 'Software Design'];
                    } elseif ($primaryField == 'medical') {
                        $defaults['skills_to_develop'] = ['Patient Care', 'Medical Knowledge', 'Clinical Documentation'];
                    } else {
                        $defaults['skills_to_develop'] = ['Communication', 'Project Management', 'Problem Solving'];
                    }
                }
                
                // Merge defaults with provided data
                $recommendations[$key] = array_merge($defaults, $item);
            }
        }
        
        return $recommendations;
    }

    public function listForSelection(Request $request)
    {
        Log::info('[EnhancedResumeController@listForSelection] Method reached.', [
            'auth_check' => Auth::check(),
            'auth_user_id' => Auth::id(),
            'request_has_session' => $request->hasSession(),
            'session_id' => session()->getId(),
            'cookies_on_request' => $request->cookies->all(),
        ]);

        $user = $request->user();

        if (!$user) {
            Log::warning('[EnhancedResumeController@listForSelection] Auth check failed. $request->user() is null.');
            return response()->json(['error' => 'Unauthenticated via $request->user()'], 401);
        }

        $resumes = $user->resumes()->select(['id', 'original_filename as filename'])->get(); // Use original_filename
        Log::info('[EnhancedResumeController@listForSelection] Successfully retrieved resumes for user.', ['user_id' => $user->id, 'count' => $resumes->count()]);
        return response()->json($resumes);
    }
} 