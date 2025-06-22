<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\JobFair;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Storage;
use App\Services\GeoapifyService;

class JobFairController extends Controller
{
    protected GeoapifyService $geoapifyService;

    public function __construct(GeoapifyService $geoapifyService)
    {
        $this->geoapifyService = $geoapifyService;
    }

    /**
     * Display a listing of all job fairs (admin can see all)
     */
    public function index(Request $request)
    {
        $query = JobFair::with(['organizer:id,name,email', 'booths']);
        
        // Add search functionality
        if ($request->has('search')) {
            $search = $request->input('search');
            $query->where(function($q) use ($search) {
                $q->where('title', 'like', "%{$search}%")
                  ->orWhere('description', 'like', "%{$search}%")
                  ->orWhere('location', 'like', "%{$search}%");
            });
        }
        
        // Add status filter
        if ($request->has('status')) {
            $query->where('status', $request->input('status'));
        }
        
        // Add organizer filter
        if ($request->has('organizer_id')) {
            $query->where('organizer_id', $request->input('organizer_id'));
        }
        
        // Add date range filter
        if ($request->has('start_date')) {
            $query->whereDate('start_datetime', '>=', $request->input('start_date'));
        }
        if ($request->has('end_date')) {
            $query->whereDate('end_datetime', '<=', $request->input('end_date'));
        }
        
        $jobFairs = $query->orderBy('start_datetime', 'desc')->get();
        
        // Add booth count to each job fair
        $jobFairs->each(function ($jobFair) {
            $jobFair->booths_count = $jobFair->booths->count();
        });
        
        return response()->json(['data' => $jobFairs]);
    }

    /**
     * Store a newly created job fair (admin can create on behalf of organizers)
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'location' => 'required_without_all:latitude,longitude|nullable|string|max:255',
            'latitude' => 'nullable|numeric|between:-90,90',
            'longitude' => 'nullable|numeric|between:-180,180',
            'start_datetime' => 'required|date|after_or_equal:today',
            'end_datetime' => 'required|date|after:start_datetime',
            'status' => 'required|string|in:draft,active,archived,published,completed,cancelled',
            'organizer_id' => 'required|exists:users,id',
            'map_image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        // Verify the organizer has the correct role
        $organizer = User::find($request->organizer_id);
        if (!$organizer || !in_array($organizer->role, ['organizer', 'admin'])) {
            return response()->json(['error' => 'Selected user is not a valid organizer or admin'], 422);
        }

        $jobFairData = $validator->validated();
        
        // Handle Geolocation
        if ($request->filled('latitude') && $request->filled('longitude')) {
            $jobFairData['latitude'] = $jobFairData['latitude'];
            $jobFairData['longitude'] = $jobFairData['longitude'];
            $jobFairData['location_query'] = $jobFairData['location'] ?? 'Coordinates provided';
            $jobFairData['formatted_address'] = $jobFairData['location'] ?? ($this->geoapifyService->reverseGeocode($jobFairData['latitude'], $jobFairData['longitude'])['formatted_address'] ?? 'Coordinates provided');
        } elseif (!empty($jobFairData['location'])) {
            $geocodeResult = $this->geoapifyService->geocodeAddress($jobFairData['location']);
            if ($geocodeResult) {
                $jobFairData['latitude'] = $geocodeResult['latitude'];
                $jobFairData['longitude'] = $geocodeResult['longitude'];
                $jobFairData['formatted_address'] = $geocodeResult['formatted_address'];
                $jobFairData['location_query'] = $jobFairData['location'];
            } else {
                $jobFairData['latitude'] = null;
                $jobFairData['longitude'] = null;
                $jobFairData['formatted_address'] = null;
                $jobFairData['location_query'] = $jobFairData['location'];
            }
        } else {
            $jobFairData['latitude'] = null;
            $jobFairData['longitude'] = null;
            $jobFairData['formatted_address'] = null;
            $jobFairData['location_query'] = null;
        }
        
        // Handle map image upload
        if ($request->hasFile('map_image')) {
            $mapImagePath = $request->file('map_image')->store('job_fair_maps', 'public');
            $jobFairData['map_image_path'] = $mapImagePath;
        }

        $jobFair = JobFair::create($jobFairData);
        $jobFair->load('organizer:id,name,email');

        return response()->json(['data' => $jobFair], 201);
    }

    /**
     * Display the specified job fair
     */
    public function show(JobFair $jobFair)
    {
        $jobFair->load(['organizer:id,name,email', 'booths.jobOpenings']);
        $jobFair->booths_count = $jobFair->booths->count();
        
        return response()->json(['data' => $jobFair]);
    }

    /**
     * Update the specified job fair (admin can update any job fair)
     */
    public function update(Request $request, JobFair $jobFair)
    {
        $validator = Validator::make($request->all(), [
            'title' => 'sometimes|required|string|max:255',
            'description' => 'sometimes|nullable|string',
            'location' => 'nullable|string|max:255',
            'latitude' => 'nullable|numeric|between:-90,90',
            'longitude' => 'nullable|numeric|between:-180,180',
            'start_datetime' => 'sometimes|required|date',
            'end_datetime' => 'sometimes|required|date|after:start_datetime',
            'status' => 'sometimes|required|string|in:draft,active,archived,published,completed,cancelled',
            'organizer_id' => 'sometimes|required|exists:users,id',
            'map_image' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:2048'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $updateData = $validator->validated();
        
        // Verify the organizer has the correct role if organizer_id is being updated
        if (isset($updateData['organizer_id'])) {
            $organizer = User::find($updateData['organizer_id']);
            if (!$organizer || !in_array($organizer->role, ['organizer', 'admin'])) {
                return response()->json(['error' => 'Selected user is not a valid organizer or admin'], 422);
            }
        }
        
        // Geocode location if it's being updated
        if ($request->filled('latitude') && $request->filled('longitude')) {
            $updateData['latitude'] = $updateData['latitude'];
            $updateData['longitude'] = $updateData['longitude'];
            $updateData['location_query'] = $request->filled('location') ? $updateData['location'] : ($jobFair->location_query ?? 'Coordinates updated');
            $updateData['formatted_address'] = $request->filled('location') ? $updateData['location'] : ($this->geoapifyService->reverseGeocode($updateData['latitude'], $updateData['longitude'])['formatted_address'] ?? $jobFair->formatted_address ?? 'Coordinates updated');
        } elseif ($request->filled('location')) {
            $geocodeResult = $this->geoapifyService->geocodeAddress($updateData['location']);
            if ($geocodeResult) {
                $updateData['latitude'] = $geocodeResult['latitude'];
                $updateData['longitude'] = $geocodeResult['longitude'];
                $updateData['formatted_address'] = $geocodeResult['formatted_address'];
                $updateData['location_query'] = $updateData['location'];
            } else {
                $updateData['latitude'] = null;
                $updateData['longitude'] = null;
                $updateData['formatted_address'] = null;
                $updateData['location_query'] = $updateData['location'];
            }
        } elseif ($request->exists('location') && is_null($request->input('location')) && !($request->filled('latitude') && $request->filled('longitude'))) {
            $updateData['latitude'] = null;
            $updateData['longitude'] = null;
            $updateData['formatted_address'] = null;
            $updateData['location_query'] = null;
        }
        
        // Handle map image upload
        if ($request->hasFile('map_image')) {
            // Delete old image if exists
            if ($jobFair->map_image_path) {
                $oldImagePath = $jobFair->map_image_path;
                if (str_starts_with($oldImagePath, '/storage/')) {
                    $oldImagePath = str_replace('/storage/', '', $oldImagePath);
                }
                Storage::disk('public')->delete($oldImagePath);
            }
            
            $mapImagePath = $request->file('map_image')->store('job_fair_maps', 'public');
            $updateData['map_image_path'] = $mapImagePath;
        } elseif ($request->exists('map_image') && is_null($request->input('map_image'))){
             if ($jobFair->map_image_path) {
                Storage::disk('public')->delete($jobFair->map_image_path);
                $updateData['map_image_path'] = null;
            }
        }

        $jobFair->update($updateData);
        $jobFair->load('organizer:id,name,email');

        return response()->json(['data' => $jobFair]);
    }

    /**
     * Remove the specified job fair (admin can delete any job fair)
     */
    public function destroy(JobFair $jobFair)
    {
        // Delete associated map image if exists
        if ($jobFair->map_image_path) {
            Storage::disk('public')->delete($jobFair->map_image_path);
        }

        $jobFair->delete();
        return response()->json(['message' => 'Job fair deleted successfully'], 200);
    }

    /**
     * Get job fair statistics
     */
    public function statistics()
    {
        $stats = [
            'total_job_fairs' => JobFair::count(),
            'active_job_fairs' => JobFair::where('status', 'active')->count(),
            'published_job_fairs' => JobFair::where('status', 'published')->count(),
            'draft_job_fairs' => JobFair::where('status', 'draft')->count(),
            'completed_job_fairs' => JobFair::where('status', 'completed')->count(),
            'cancelled_job_fairs' => JobFair::where('status', 'cancelled')->count(),
            'upcoming_job_fairs' => JobFair::where('start_datetime', '>', now())->count(),
            'current_job_fairs' => JobFair::where('start_datetime', '<=', now())
                                          ->where('end_datetime', '>=', now())
                                          ->count(),
            'total_booths' => \App\Models\Booth::count(),
            'total_job_openings' => \App\Models\BoothJobOpening::count(),
        ];

        return response()->json(['data' => $stats]);
    }

    /**
     * Get all organizers for dropdown selection
     */
    public function getOrganizers()
    {
        $organizers = User::whereIn('role', ['organizer', 'admin'])
                         ->select('id', 'name', 'email', 'role')
                         ->orderBy('name')
                         ->get();

        return response()->json(['data' => $organizers]);
    }

    /**
     * Bulk update job fair status
     */
    public function bulkUpdateStatus(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'job_fair_ids' => 'required|array',
            'job_fair_ids.*' => 'exists:job_fairs,id',
            'status' => 'required|string|in:draft,published,active,completed,cancelled'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $updated = JobFair::whereIn('id', $request->job_fair_ids)
                         ->update(['status' => $request->status]);

        return response()->json([
            'message' => "Updated {$updated} job fair(s) to status: {$request->status}",
            'updated_count' => $updated
        ]);
    }
} 