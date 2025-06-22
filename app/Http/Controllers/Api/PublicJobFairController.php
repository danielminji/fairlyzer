<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\JobFair;
use Illuminate\Http\Request;
use App\Services\GeoapifyService;
use Illuminate\Support\Facades\Validator;

class PublicJobFairController extends Controller
{
    protected GeoapifyService $geoapifyService;

    public function __construct(GeoapifyService $geoapifyService)
    {
        $this->geoapifyService = $geoapifyService;
    }

    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        // Fetch job fairs that are considered public (e.g., status is 'active' or 'published')
        // Adjust the status check as per your application's logic for public visibility.
        $jobFairs = JobFair::with('organizer:id,name') // Load organizer name
            ->withCount('booths') // Correctly count booths
            ->whereIn('status', ['active', 'published']) // Example statuses for public fairs
            ->orderBy('start_datetime', 'asc') // Corrected to 'start_datetime'
            ->get();

        return response()->json(['data' => $jobFairs]);
    }

    /**
     * Display the specified job fair.
     *
     * @param  \App\Models\JobFair  $jobFair
     * @return \Illuminate\Http\JsonResponse
     */
    public function show(JobFair $jobFair)
    {
        // Ensure only publicly visible job fairs are shown directly by ID
        if (!in_array($jobFair->status, ['active', 'published'])) {
            return response()->json(['message' => 'Job fair not found or not publicly available.'], 404);
        }

        $jobFair->load(['organizer:id,name', 'booths']); // Load booths for detail view

        return response()->json(['data' => $jobFair]);
    }

    /**
     * Get all job openings for a specific job fair.
     *
     * @param  \App\Models\JobFair  $jobFair
     * @return \Illuminate\Http\JsonResponse
     */
    public function getFairOpenings(Request $request, JobFair $jobFair)
    {
        if (!in_array($jobFair->status, ['active', 'published'])) {
            return response()->json(['message' => 'Job fair not found or not publicly available.'], 404);
        }

        // Eager load booths and their job openings, explicitly selecting necessary fields
        $jobFair->load([
            'booths.jobOpenings' => function ($query) {
                $query->select(['id', 'booth_id', 'job_title', 'description', 'primary_field', 'required_skills_general', 'required_skills_soft', 'required_experience_years', 'required_experience_entries', 'required_cgpa']); // Ensure all needed fields are here
            },
            'booths' => function ($query) {
                $query->select(['id', 'job_fair_id', 'company_name', 'booth_number_on_map']); // Select fields for booths
            }
        ]);

        return response()->json([
            'data' => [
                'job_fair_id' => $jobFair->id,
                'job_fair_title' => $jobFair->title,
                'job_fair_map_url' => $jobFair->map_image_path, // Use directly
                'booths_with_openings' => $jobFair->booths->map(function ($booth) {
                    return [
                        'booth_id' => $booth->id,
                        'company_name' => $booth->company_name,
                        'booth_number_on_map' => $booth->booth_number_on_map,
                        'job_openings' => $booth->jobOpenings->map(function ($opening) {
                            return [
                                'id' => $opening->id,
                                'job_title' => $opening->job_title,
                                'description' => $opening->description,
                                'primary_field' => $opening->primary_field,
                                'required_skills_general' => $opening->required_skills_general,
                                'required_skills_soft' => $opening->required_skills_soft,
                                'required_experience_years' => $opening->required_experience_years,
                                'required_experience_entries' => $opening->required_experience_entries,
                                'required_cgpa' => $opening->required_cgpa,
                            ];
                        })
                    ];
                })
            ]
        ]);
    }

    /**
     * Get directions to a job fair from user's location.
     *
     * @param Request $request
     * @param JobFair $jobFair
     * @return \Illuminate\Http\JsonResponse
     */
    public function getDirections(Request $request, JobFair $jobFair)
    {
        if (!in_array($jobFair->status, ['active', 'published'])) {
            return response()->json(['message' => 'Job fair not found or not publicly available.'], 404);
        }

        if (is_null($jobFair->latitude) || is_null($jobFair->longitude)) {
            return response()->json(['message' => 'Job fair location is not available.'], 404);
        }

        $validator = Validator::make($request->all(), [
            'user_lat' => 'required|numeric|min:-90|max:90',
            'user_lon' => 'required|numeric|min:-180|max:180',
            'mode' => 'sometimes|string|in:drive,walk,bicycle,motorcycle,truck,scooter,transit' // Common modes, check Geoapify for full list
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $validated = $validator->validated();

        $startCoords = [
            'lat' => (float)$validated['user_lat'],
            'lon' => (float)$validated['user_lon']
        ];
        $endCoords = [
            'lat' => $jobFair->latitude,
            'lon' => $jobFair->longitude
        ];
        $mode = $validated['mode'] ?? 'drive';

        $routeData = $this->geoapifyService->getRoute($startCoords, $endCoords, $mode);

        if ($routeData) {
            return response()->json(['data' => $routeData]);
        } else {
            return response()->json(['message' => 'Could not retrieve directions at this time.'], 500);
        }
    }
} 