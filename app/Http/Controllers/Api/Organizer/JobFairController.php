<?php

namespace App\Http\Controllers\Api\Organizer;

use App\Http\Controllers\Controller;
use App\Models\JobFair;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Auth;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use App\Services\GeoapifyService;

class JobFairController extends Controller
{
    use AuthorizesRequests;

    protected GeoapifyService $geoapifyService;

    public function __construct(GeoapifyService $geoapifyService)
    {
        $this->geoapifyService = $geoapifyService;
    }

    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $organizer = Auth::user();
        $jobFairs = JobFair::where('organizer_id', $organizer->id)->orderBy('created_at', 'desc')->get();
        return response()->json($jobFairs);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $organizer = Auth::user();

        $validatedData = $request->validate([
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'start_datetime' => 'required|date_format:Y-m-d\TH:i:s',
            'end_datetime' => 'required|date_format:Y-m-d\TH:i:s|after:start_datetime',
            'location' => 'required_without_all:latitude,longitude|nullable|string|max:255',
            'latitude' => 'nullable|numeric|between:-90,90',
            'longitude' => 'nullable|numeric|between:-180,180',
            'map_image' => 'nullable|image|mimes:jpeg,png,jpg,gif,svg|max:2048',
            'status' => 'sometimes|string|in:draft,active,archived',
        ]);

        $jobFairData = $validatedData;
        $jobFairData['organizer_id'] = $organizer->id;

        // Handle Geolocation
        // Prioritize direct latitude/longitude input
        if ($request->filled('latitude') && $request->filled('longitude')) {
            $jobFairData['latitude'] = $validatedData['latitude'];
            $jobFairData['longitude'] = $validatedData['longitude'];
            // If coordinates are provided, we might want to reverse geocode to get a formatted_address and location_query
            // For simplicity now, if an address is also provided, it will be used for location_query and formatted_address
            // If no address text, these might remain null or be derived via reverse geocoding (optional enhancement)
            $jobFairData['location_query'] = $validatedData['location'] ?? 'Coordinates provided'; // Or reverse geocode
            $jobFairData['formatted_address'] = $validatedData['location'] ?? 'Coordinates provided'; // Or reverse geocode
        } elseif (!empty($validatedData['location'])) {
            // Geocode location text if coordinates are not provided
            $geocodeResult = $this->geoapifyService->geocodeAddress($validatedData['location']);
            if ($geocodeResult) {
                $jobFairData['latitude'] = $geocodeResult['latitude'];
                $jobFairData['longitude'] = $geocodeResult['longitude'];
                $jobFairData['formatted_address'] = $geocodeResult['formatted_address'];
                $jobFairData['location_query'] = $validatedData['location'];
            } else {
                // If geocoding fails, and no direct coords, set to null or handle error
                $jobFairData['latitude'] = null;
                $jobFairData['longitude'] = null;
                $jobFairData['formatted_address'] = null;
                $jobFairData['location_query'] = $validatedData['location']; // Keep the query text
            }
        } else {
            // No location text and no coordinates provided (should be caught by validation)
            // Or handle as an error / set defaults
            $jobFairData['latitude'] = null;
            $jobFairData['longitude'] = null;
            $jobFairData['formatted_address'] = null;
            $jobFairData['location_query'] = null;
        }

        if ($request->hasFile('map_image')) {
            $relativePath = $request->file('map_image')->store('job_fair_maps', 'public');
            $jobFairData['map_image_path'] = $relativePath;
        }

        if (!$request->filled('status')) {
            $jobFairData['status'] = 'draft';
        }

        $jobFair = JobFair::create($jobFairData);

        return response()->json($jobFair, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(JobFair $jobFair)
    {
        $this->authorize('view', $jobFair); // Policy check
        return response()->json($jobFair);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, JobFair $jobFair)
    {
        $this->authorize('update', $jobFair); // Policy check

        $validatedData = $request->validate([
            'title' => 'sometimes|required|string|max:255',
            'description' => 'nullable|string',
            'start_datetime' => 'sometimes|required|date_format:Y-m-d\TH:i:s',
            'end_datetime' => 'sometimes|required|date_format:Y-m-d\TH:i:s|after:start_datetime',
            'location' => 'nullable|string|max:255',
            'latitude' => 'nullable|numeric|between:-90,90',
            'longitude' => 'nullable|numeric|between:-180,180',
            'map_image' => 'nullable|image|mimes:jpeg,png,jpg,gif,svg|max:2048',
            'status' => 'sometimes|string|in:draft,active,archived',
        ]);
        
        $updateData = $validatedData;

        // Handle Geolocation update
        if ($request->filled('latitude') && $request->filled('longitude')) {
            $updateData['latitude'] = $validatedData['latitude'];
            $updateData['longitude'] = $validatedData['longitude'];
            // Similar to store: if an address is also provided, use it.
            // Otherwise, could reverse geocode or use a placeholder.
            $updateData['location_query'] = $request->filled('location') ? $validatedData['location'] : ($jobFair->location_query ?? 'Coordinates updated');
            $updateData['formatted_address'] = $request->filled('location') ? $validatedData['location'] : ($jobFair->formatted_address ?? 'Coordinates updated');
        } elseif ($request->filled('location')) {
            // Geocode location text if new location text is provided and no direct coords
            $geocodeResult = $this->geoapifyService->geocodeAddress($validatedData['location']);
            if ($geocodeResult) {
                $updateData['latitude'] = $geocodeResult['latitude'];
                $updateData['longitude'] = $geocodeResult['longitude'];
                $updateData['formatted_address'] = $geocodeResult['formatted_address'];
                $updateData['location_query'] = $validatedData['location'];
            } else {
                // If geocoding fails on new address text, clear coordinates
                $updateData['latitude'] = null;
                $updateData['longitude'] = null;
                $updateData['formatted_address'] = null;
                $updateData['location_query'] = $validatedData['location']; // Still save the query text
            }
        } elseif ($request->exists('location') && is_null($request->input('location')) && !($request->filled('latitude') && $request->filled('longitude'))) {
            // If location text is explicitly cleared, and no new coordinates are provided, clear all geo fields
            $updateData['latitude'] = null;
            $updateData['longitude'] = null;
            $updateData['formatted_address'] = null;
            $updateData['location_query'] = null;
        }
        // If only location text is cleared BUT new lat/lon are provided, the first block handles it.
        // If no location fields are sent, existing geo data remains unchanged.

        if ($request->hasFile('map_image')) {
            if ($jobFair->map_image_path) {
                Storage::disk('public')->delete($jobFair->map_image_path);
            }
            $relativePath = $request->file('map_image')->store('job_fair_maps', 'public');
            $updateData['map_image_path'] = $relativePath;
        } elseif ($request->exists('map_image') && is_null($request->input('map_image'))) {
            // If map_image is explicitly set to null (e.g., to remove it)
            if ($jobFair->map_image_path) {
                Storage::disk('public')->delete($jobFair->map_image_path);
                $updateData['map_image_path'] = null;
            }
        }

        $jobFair->update($updateData);

        return response()->json($jobFair);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(JobFair $jobFair)
    {
        $this->authorize('delete', $jobFair); // Policy check

        // Delete map image if exists
        if ($jobFair->map_image_path) {
            // Assuming map_image_path stores the relative path on the 'public' disk
            Storage::disk('public')->delete($jobFair->map_image_path);
        }

        $jobFair->delete();

        return response()->json(null, 204);
    }

    public function listBooths(JobFair $jobFair)
    {
        // No authorization needed here as this is a public listing of booths for a job fair
        // However, ensure the job fair itself is queryable (e.g., active)
        // Add status check for jobFair if needed: e.g., if ($jobFair->status !== 'active') return response()->json(['error' => 'Job fair not found or not active.'], 404);

        $booths = $jobFair->booths()->select(['id', 'company_name', 'booth_number_on_map', 'map_coordinates'])->get();
        return response()->json($booths);
    }
}
