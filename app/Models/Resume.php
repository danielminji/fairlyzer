<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Log; // Added for logging
// use Illuminate\Database\Eloquent\Relations\HasMany; // Potentially for future relations like saved_jobs etc.

class Resume extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'original_filename',
        'filepath',
        'primary_field',
        'parsed_data',
        'raw_text',
        'analysis_data',
        'parsing_status',
        'parser_error_message'
    ];

    protected $casts = [
        'parsed_data' => 'array',
        'analysis_data' => 'array',
    ];

    /**
     * Get the user that owns the resume.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
    
    /**
     * Accessor to calculate total experience in years from parsed_data.
     * Parses date strings like "YYYY - YYYY" or "Month YYYY - Month YYYY".
     *
     * @return float
     */
    public function getTotalExperienceYearsAttribute(): float
    {
        $totalMonths = 0;
        $experienceEntries = $this->parsed_data['experience'] ?? [];

        if (!is_array($experienceEntries)) {
            return 0.0;
        }

        $currentYear = date('Y');
        $currentMonth = date('n'); // Month number without leading zeros

        $monthMap = [
            'jan' => 1, 'january' => 1, 'feb' => 2, 'february' => 2, 'mar' => 3, 'march' => 3, 
            'apr' => 4, 'april' => 4, 'may' => 5, 'jun' => 6, 'june' => 6,
            'jul' => 7, 'july' => 7, 'aug' => 8, 'august' => 8, 'sep' => 9, 'september' => 9, 
            'oct' => 10, 'october' => 10, 'nov' => 11, 'november' => 11, 'dec' => 12, 'december' => 12,
        ];

        foreach ($experienceEntries as $entry) {
            if (isset($entry['date']) && is_string($entry['date'])) {
                $dateStr = strtolower(trim($entry['date']));

                $startYear = null;
                $startMonth = 1; // Default to January if month is not specified
                $endYear = null;
                $endMonth = 12; // Default to December if month is not specified or 'Present'

                // Regex to capture full details (months and years)
                $pattern = '/(?:([a-z]{3,})\s*)?(\d{4})\s*(?:-|–|to|until)\s*(?:(?:([a-z]{3,})\s*)?(\d{4})|(present|current|now))/i';
                
                // Simpler pattern for year-only or year-present (this was the pre-change version)
                $yearOnlyPattern = '/(\d{4})\s*(?:(?:-|–|to|until)\s*(\d{4}|present|current|now))?/i';

                if (preg_match($pattern, $dateStr, $matches)) {
                    if (!empty($matches[1]) && isset($monthMap[substr($matches[1], 0, 3)])) {
                        $startMonth = $monthMap[substr($matches[1], 0, 3)];
                    }
                    $startYear = (int)$matches[2];

                    if (!empty($matches[5])) { // End date is Present/Current
                        $endYear = (int)$currentYear;
                        $endMonth = (int)$currentMonth;
                    } else { // Specific end year and possibly month
                        $endYear = (int)$matches[4];
                        // If end month is not specified with a specific end year, default to December
                        // $endMonth is already 12 by default, so only change if a month is found.
                        if (!empty($matches[3]) && isset($monthMap[substr($matches[3], 0, 3)])) {
                            $endMonth = $monthMap[substr($matches[3], 0, 3)];
                        }
                    }
                } elseif (preg_match($yearOnlyPattern, $dateStr, $matches)) {
                    $startYear = (int)$matches[1];
                    // $startMonth is already 1 by default

                    if (isset($matches[2])) {
                        if (in_array(strtolower($matches[2]), ['present', 'current', 'now'])) {
                            $endYear = (int)$currentYear;
                            $endMonth = (int)$currentMonth;
                        } else {
                            $endYear = (int)$matches[2];
                            // $endMonth is already 12 by default for year-only ranges ending in a specific year
                        }
                    } else {
                        // Single year entry like "2024" or a role that implicitly ended that year.
                        // For simplicity, treat as a full year if past, or up to current if current year.
                        if ($startYear == $currentYear) {
                            $endYear = (int)$currentYear;
                            $endMonth = (int)$currentMonth;
                        } else {
                            $endYear = $startYear; // End of the same year
                            // $endMonth is already 12 by default
                        }
                    }
                }

                if ($startYear && $endYear) {
                    // Validate the date range before calculation
                    if ($startYear > $endYear || ($startYear == $endYear && $startMonth > $endMonth)) {
                        // Invalid range (e.g., Dec 2023 - Jan 2023, or 2025 - 2023), duration is 0 or log error
                        // $totalMonths += 0; // Effectively no change
                    } else {
                        $monthsInRole = (($endYear - $startYear) * 12) + ($endMonth - $startMonth) + 1;
                        if ($monthsInRole > 0) { 
                           $totalMonths += $monthsInRole;
                        }
                    }
                }
            }
        }
        return round($totalMonths / 12, 2);
    }
    
    /**
     * Accessor to get total experience as a human-readable string (e.g., "2 years 9 months").
     *
     * @return string
     */
    public function getFormattedTotalExperienceAttribute(): string
    {
        $totalYearsFloat = $this->total_experience_years; // Uses the accessor we defined earlier

        if ($totalYearsFloat <= 0) {
            return "Less than a month"; // Or "No experience", depending on preference
        }

        $years = floor($totalYearsFloat);
        $remainingMonths = round(($totalYearsFloat - $years) * 12);

        $parts = [];
        if ($years > 0) {
            $parts[] = $years . ($years == 1 ? " year" : " years");
        }
        if ($remainingMonths > 0) {
            $parts[] = $remainingMonths . ($remainingMonths == 1 ? " month" : " months");
        }

        if (empty($parts)) { // Should not happen if $totalYearsFloat > 0
            return "N/A"; 
        }

        return implode(' ', $parts);
    }
    
    /**
     * Accessor to get the CGPA from the education section of parsed_data.
     *
     * @return float|null
     */
    public function getCgpaFromEducationAttribute(): ?float
    {
        if (!empty($this->parsed_data['education'])) {
            foreach ($this->parsed_data['education'] as $edu) {
                if (isset($edu['cgpa']) && is_numeric($edu['cgpa'])) {
                    return floatval($edu['cgpa']); // Return the first valid CGPA found
                }
            }
        }
        return null; // Return null if no CGPA is found
    }
    
    /**
     * Generate and store job recommendations based on parsed resume data and job requirements.
     */
    public function storeJobRecommendations(): void
    {
        Log::info("Starting storeJobRecommendations for resume ID: " . $this->id);

        if (empty($this->parsed_data) || empty($this->primary_field)) {
            Log::warning("Skipping job recommendations for resume ID: {$this->id} due to missing parsed_data or primary_field.");
            $this->analysis_data = array_merge($this->analysis_data ?? [], ['job_recommendations' => []]);
            $this->save();
            return;
        }

        $resumePrimaryField = $this->primary_field;
        $resumeSkillsGeneral = $this->parsed_data['skills']['general_skills'] ?? [];
        $resumeSkillsSoft = $this->parsed_data['skills']['soft_skills'] ?? [];
        
        $resumeTotalExperienceYears = $this->total_experience_years;

        $resumeCGPA = null;
        if (!empty($this->parsed_data['education'])) {
            foreach ($this->parsed_data['education'] as $edu) {
                if (isset($edu['cgpa']) && is_numeric($edu['cgpa'])) {
                    $resumeCGPA = floatval($edu['cgpa']);
                    break; // Use the first valid CGPA found
                }
            }
        }

        $jobRequirements = JobRequirement::where('primary_field', $resumePrimaryField)->get();
        $recommendations = [];

        Log::info("Found " . $jobRequirements->count() . " job requirements for primary field: {$resumePrimaryField}");

        foreach ($jobRequirements as $jobReq) {
            $scoreSkills = 0;
            $scoreExperience = 0;
            $scoreEducation = 0;

            // 1. Skills Score (40%)
            $requiredGeneral = $jobReq->required_skills_general ?? [];
            $requiredSoft = $jobReq->required_skills_soft ?? [];
            $totalRequiredSkills = count($requiredGeneral) + count($requiredSoft);
            $matchedSkillsCount = 0;
            $matchedGeneralSkillsList = [];
            $missingGeneralSkillsList = [];
            $matchedSoftSkillsList = [];
            $missingSoftSkillsList = [];

            if (!empty($resumeSkillsGeneral)) {
                foreach ($requiredGeneral as $reqSkill) {
                    if (in_array($reqSkill, $resumeSkillsGeneral, true)) {
                        $matchedSkillsCount++;
                        $matchedGeneralSkillsList[] = $reqSkill;
                    } else {
                        $missingGeneralSkillsList[] = $reqSkill;
                    }
                }
            } else {
                $missingGeneralSkillsList = $requiredGeneral;
            }

            if (!empty($resumeSkillsSoft)) {
                foreach ($requiredSoft as $reqSkill) {
                    if (in_array($reqSkill, $resumeSkillsSoft, true)) {
                        $matchedSkillsCount++;
                        $matchedSoftSkillsList[] = $reqSkill;
                    } else {
                        $missingSoftSkillsList[] = $reqSkill;
                    }
                }
            } else {
                $missingSoftSkillsList = $requiredSoft;
            }

            if ($totalRequiredSkills > 0) {
                $scoreSkills = ($matchedSkillsCount / $totalRequiredSkills) * 40;
            }

            // 2. Experience Score (30%)
            if ($jobReq->required_experience_years !== null && $resumeTotalExperienceYears >= $jobReq->required_experience_years) {
                $scoreExperience = 30;
            } elseif ($jobReq->required_experience_years === null || $jobReq->required_experience_years == 0) {
                $scoreExperience = 30;
            }

            // 3. Education Score (30%)
            if ($resumeCGPA !== null && $jobReq->required_cgpa !== null && $resumeCGPA >= $jobReq->required_cgpa) {
                $scoreEducation = 30;
            }

            $totalScore = $scoreSkills + $scoreExperience + $scoreEducation;

            Log::debug("Job: {$jobReq->job_title}, Resume: {$this->id}, Score: {$totalScore} (S:{$scoreSkills}, E:{$scoreExperience}, Ed:{$scoreEducation})");

            if ($totalScore >= 50) {
                $recommendations[] = [
                    'job_title' => $jobReq->job_title,
                    'score' => round($totalScore, 2),
                    'score_details' => [
                        'skills' => round($scoreSkills, 2),
                        'experience' => round($scoreExperience, 2),
                        'education' => round($scoreEducation, 2),
                    ],
                    'match_details' => [
                        'matched_general_skills' => $matchedGeneralSkillsList,
                        'missing_general_skills' => $missingGeneralSkillsList,
                        'matched_soft_skills' => $matchedSoftSkillsList,
                        'missing_soft_skills' => $missingSoftSkillsList,
                        'experience_met' => $scoreExperience > 0,
                        'education_met' => $scoreEducation > 0,
                        'required_experience_years' => $jobReq->required_experience_years,
                        'resume_total_experience_years' => $resumeTotalExperienceYears,
                        'resume_formatted_total_experience' => $this->formatted_total_experience,
                        'required_cgpa' => $jobReq->required_cgpa,
                        'resume_cgpa' => $resumeCGPA
                    ],
                    'primary_field' => $jobReq->primary_field,
                    'description' => $jobReq->description,
                ];
            }
        }

        // Sort recommendations by score DESC
        usort($recommendations, function ($a, $b) {
            return $b['score'] <=> $a['score'];
        });

        $currentAnalysisData = $this->analysis_data ?? [];
        $currentAnalysisData['job_recommendations'] = $recommendations;
        
        $this->analysis_data = $currentAnalysisData;
        $this->save();

        Log::info("Successfully stored " . count($recommendations) . " job recommendations for resume ID: " . $this->id);
    }
    
    // Business logic like calculateBoothMatches, generateJobRecommendations, 
    // determinePrimaryField, calculateJobMatchScore etc. 
    // will be moved to service classes later for better separation of concerns.
} 