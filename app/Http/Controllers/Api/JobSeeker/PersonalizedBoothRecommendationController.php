<?php

namespace App\Http\Controllers\Api\JobSeeker;

use App\Http\Controllers\Controller;
use App\Models\Resume;
use App\Models\JobFair;
use App\Models\BoothJobOpening;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class PersonalizedBoothRecommendationController extends Controller
{
    /**
     * Get personalized booth recommendations for a given resume and job fair.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Models\Resume  $resume
     * @param  \App\Models\JobFair  $jobFair
     * @return \Illuminate\Http\JsonResponse
     */
    public function getRecommendations(Request $request, Resume $resume, JobFair $jobFair)
    {
        Log::info("PersonalizedBoothRecommendationController@getRecommendations invoked.", [
            'resume_id' => $resume->id,
            'job_fair_id' => $jobFair->id,
            'job_fair_title' => $jobFair->title
        ]);

        // 1. Ensure the resume has parsed data
        if (empty($resume->parsed_data) || !is_array($resume->parsed_data)) {
            Log::warning("Resume ID {$resume->id} has no parsed data.");
            return response()->json(['error' => 'Resume has no parsed data available.'], 400);
        }
        Log::debug("Resume Parsed Data Keys:", ['id' => $resume->id, 'keys' => array_keys($resume->parsed_data)]);

        // 2. Ensure job fair is active/published (optional, but good practice)
        if (!in_array($jobFair->status, ['active', 'published'])) {
            Log::warning("Job Fair not active/published.", ['id' => $jobFair->id, 'status' => $jobFair->status]);
            return response()->json(['message' => 'Job fair not found or not publicly available.'], 404);
        }

        // 3. Extract key information from the resume
        $resumeSkills = array_map('strtolower', array_merge(
            $resume->parsed_data['skills']['general_skills'] ?? [],
            $resume->parsed_data['skills']['soft_skills'] ?? []
        ));
        $resumeTotalExperienceYears = $resume->total_experience_years; // Accessor
        
        // Get the resume's primary field directly from the model attribute
        $resumePrimaryField = $resume->primary_field; 
        $resumeNormalizedPrimaryField = null;
        if ($resumePrimaryField) {
            $resumeNormalizedPrimaryField = strtolower(str_replace(' ', '_', $resumePrimaryField));
        }

        // Directly extract CGPA from parsed_data for this controller context
        $resumeCGPA = null;
        if (!empty($resume->parsed_data['education'])) {
            foreach ($resume->parsed_data['education'] as $edu) {
                if (isset($edu['cgpa']) && is_numeric($edu['cgpa'])) {
                    $resumeCGPA = floatval($edu['cgpa']);
                    break; 
                }
            }
        }

        Log::info("Resume Details for Matching:", [
            'resume_id' => $resume->id,
            'skills_count' => count($resumeSkills),
            'total_experience_years' => $resumeTotalExperienceYears,
            'cgpa_used_for_matching' => $resumeCGPA // Log the CGPA value being used
        ]);

        // 4. Load job fair with necessary relations: booths -> jobOpenings -> jobRequirement
        $jobFair->load([
            'booths.jobOpenings' => function ($query) {
                $query->select(['id', 'booth_id', 'job_title', 'description', 'primary_field', 'required_skills_general', 'required_skills_soft', 'required_experience_years', 'required_experience_entries', 'required_cgpa']); 
            },
            'booths:id,job_fair_id,company_name,booth_number_on_map' // Removed map_coordinates
        ]);
        Log::info("Job fair data loaded with relations.", ['job_fair_id' => $jobFair->id, 'booth_count' => $jobFair->booths->count()]);

        $recommendedBooths = [];

        foreach ($jobFair->booths as $booth) {
            Log::debug("Processing Booth:", ['booth_id' => $booth->id, 'company' => $booth->company_name, 'openings_count' => $booth->jobOpenings->count()]);
            $recommendedOpeningsForBooth = [];
            $highestScoreInBooth = 0;

            foreach ($booth->jobOpenings as $opening) { // $opening is an instance of BoothJobOpening
                
                // --- Strict Primary Field Filter ---
                $openingPrimaryField = $opening->primary_field;
                $openingNormalizedPrimaryField = null;
                if ($openingPrimaryField) {
                    $openingNormalizedPrimaryField = strtolower(str_replace(' ', '_', $openingPrimaryField));
                }

                // If resume has a primary field and it doesn't match the opening's primary field, skip this opening.
                if ($resumeNormalizedPrimaryField && $openingNormalizedPrimaryField !== $resumeNormalizedPrimaryField) {
                    Log::debug("Skipping opening due to primary field mismatch", [
                        'resume_field' => $resumeNormalizedPrimaryField,
                        'opening_field' => $openingNormalizedPrimaryField,
                        'opening_id' => $opening->id
                    ]);
                    continue; // Skip to the next opening
                }
                // If resume has no primary field, we can't filter by it, so all openings pass this check.
                // This case should ideally be handled earlier (e.g., prompt user to complete resume analysis if primary_field is missing)

                Log::debug("Processing Opening (passed primary field check or no resume field to check against):", [
                    'opening_id' => $opening->id, 
                    'job_title' => $opening->job_title, 
                    'raw_opening_data' => $opening->attributesToArray() // Log all attributes of the opening
                ]);
                
                // Criteria are now directly on the $opening object
                $score = 0;
                $scoreDetails = ['skills' => 0, 'experience' => 0, 'education' => 0];
                $matchDetails = [
                    'matched_general_skills' => [], 'missing_general_skills' => [],
                    'matched_soft_skills' => [], 'missing_soft_skills' => [],
                    'experience_met' => false, 'required_experience_years' => $opening->required_experience_years,
                    'resume_total_experience_years' => $resumeTotalExperienceYears,
                    'resume_formatted_total_experience' => $resume->formatted_total_experience,
                    'education_met' => false, 'required_cgpa' => $opening->required_cgpa,
                    'resume_cgpa' => $resumeCGPA ?? 'N/A', // Use the directly extracted CGPA for display
                    'required_experience_entries' => $opening->required_experience_entries,
                ];

                // Skills Score
                $reqGeneralSkills = array_map('strtolower', $opening->required_skills_general ?? []);
                $reqSoftSkills = array_map('strtolower', $opening->required_skills_soft ?? []);
                $totalReqSkills = count($reqGeneralSkills) + count($reqSoftSkills);
                $matchedSkillsCount = 0;
                if ($totalReqSkills > 0) {
                    foreach ($reqGeneralSkills as $reqSkill) { if (in_array($reqSkill, $resumeSkills)) { $matchedSkillsCount++; $matchDetails['matched_general_skills'][] = $reqSkill; } else { $matchDetails['missing_general_skills'][] = $reqSkill; } }
                    foreach ($reqSoftSkills as $reqSkill) { if (in_array($reqSkill, $resumeSkills)) { $matchedSkillsCount++; $matchDetails['matched_soft_skills'][] = $reqSkill; } else { $matchDetails['missing_soft_skills'][] = $reqSkill; } }
                    $scoreDetails['skills'] = ($matchedSkillsCount / $totalReqSkills) * 40;
                }
                $score += $scoreDetails['skills'];

                // Experience Score
                if ($resumeTotalExperienceYears >= $opening->required_experience_years) {
                    $scoreDetails['experience'] = 30;
                    $matchDetails['experience_met'] = true;
                } else if ($opening->required_experience_years > 0) {
                    $scoreDetails['experience'] = ($resumeTotalExperienceYears / $opening->required_experience_years) * 30;
                    $scoreDetails['experience'] = max(0, min($scoreDetails['experience'], 30));
                }
                $score += $scoreDetails['experience'];
                
                // Education Score
                if ($resumeCGPA !== null && $opening->required_cgpa !== null && $opening->required_cgpa > 0) {
                    if ($resumeCGPA >= $opening->required_cgpa) {
                        $scoreDetails['education'] = 30;
                        $matchDetails['education_met'] = true;
                    } else {
                        // Pro-rata score if CGPA is lower but still present
                        $scoreDetails['education'] = ($resumeCGPA / $opening->required_cgpa) * 30;
                        $scoreDetails['education'] = max(0, min($scoreDetails['education'], 30)); 
                    }
                } elseif ($resumeCGPA !== null && ($opening->required_cgpa === null || $opening->required_cgpa == 0)) {
                    // If opening requires no CGPA, but resume has one, grant full points for education availability
                    $scoreDetails['education'] = 30;
                    $matchDetails['education_met'] = true;
                }
                $score += $scoreDetails['education'];

                Log::debug("Score Calculation for Opening:", [
                    'opening_id' => $opening->id,
                    'job_title' => $opening->job_title,
                    'final_score' => round($score, 2),
                    'skills_score' => $scoreDetails['skills'],
                    'exp_score' => $scoreDetails['experience'],
                    'edu_score' => $scoreDetails['education'],
                    'matched_general' => $matchDetails['matched_general_skills'],
                    'missing_general' => $matchDetails['missing_general_skills'],
                    'opening_req_exp_years' => $opening->required_experience_years,
                    'opening_req_exp_entries' => $opening->required_experience_entries,
                    'opening_req_cgpa' => $opening->required_cgpa,
                ]);

                if ($score >= 0) { 
                    $recommendedOpeningsForBooth[] = [
                        'job_opening_id' => $opening->id,
                        'job_title' => $opening->job_title,
                        'description' => $opening->description,
                        'primary_field' => $opening->primary_field,
                        'score' => round($score, 2),
                        'score_details' => $scoreDetails,
                        'match_details' => $matchDetails,
                    ];
                    if ($score > $highestScoreInBooth) {
                        $highestScoreInBooth = $score;
                    }
                }
            }

            if (!empty($recommendedOpeningsForBooth)) {
                // Sort openings within the booth by score desc
                usort($recommendedOpeningsForBooth, fn($a, $b) => $b['score'] <=> $a['score']);
                $recommendedBooths[] = [
                    'booth_id' => $booth->id,
                    'company_name' => $booth->company_name,
                    'booth_number_on_map' => $booth->booth_number_on_map,
                    'highest_score_in_booth' => round($highestScoreInBooth, 2),
                    'recommended_openings' => $recommendedOpeningsForBooth,
                ];
                Log::info("Booth added to recommendations", ['booth_id' => $booth->id, 'openings_count' => count($recommendedOpeningsForBooth), 'highest_score' => $highestScoreInBooth]);
            } else {
                Log::info("No recommended openings for booth", ['booth_id' => $booth->id]);
            }
        }

        // Sort booths by the highest score found within them
        usort($recommendedBooths, fn($a, $b) => $b['highest_score_in_booth'] <=> $a['highest_score_in_booth']);
        Log::info("Final recommendation list generated.", ['recommended_booth_count' => count($recommendedBooths)]);

        return response()->json([
            'data' => [
                'resume_id' => $resume->id,
                'job_fair_id' => $jobFair->id,
                'job_fair_title' => $jobFair->title,
                'job_fair_map_url' => $jobFair->map_image_url,
                'recommended_booths' => $recommendedBooths,
            ]
        ]);
    }
} 