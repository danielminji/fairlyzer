<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\JobFair;
use App\Models\Booth;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log; // For logging

class BoothController extends Controller
{
    /**
     * Display a listing of booths for a specific job fair.
     */
    public function index(JobFair $jobFair)
    {
        // Eager load organizer to potentially display organizer info if needed, though not directly stored on booth
        $booths = $jobFair->booths()->with('jobFair.organizer')->get();
        return response()->json(['data' => $booths]);
    }

    /**
     * Store a newly created booth in storage for a specific job fair.
     */
    public function store(Request $request, JobFair $jobFair)
    {
        $validator = Validator::make($request->all(), [
            'company_name' => 'required|string|max:255',
            'booth_number_on_map' => 'required|integer|min:1|max:1000', // Assuming a reasonable max
            // 'description' => 'nullable|string', // Booth model doesn't have description, add if needed
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $validatedData = $validator->validated();
        
        // Automatically associate with the job fair
        $validatedData['job_fair_id'] = $jobFair->id;
        // The organizer_id is implicitly the jobFair's organizer_id. No direct organizer_id on Booth model.

        try {
            $booth = Booth::create($validatedData);
            Log::info("Admin created booth: " . $booth->id . " for job fair: " . $jobFair->id);
            return response()->json($booth, 201);
        } catch (\Exception $e) {
            Log::error("Error creating booth by admin: " . $e->getMessage());
            return response()->json(['error' => 'Failed to create booth. Please check logs.'], 500);
        }
    }

    /**
     * Display the specified booth.
     */
    public function show(Booth $booth)
    {
        // Eager load related data if needed
        $booth->load('jobFair.organizer', 'jobOpenings'); 
        return response()->json($booth);
    }

    /**
     * Update the specified booth in storage.
     */
    public function update(Request $request, Booth $booth)
    {
        $validator = Validator::make($request->all(), [
            'company_name' => 'sometimes|required|string|max:255',
            'booth_number_on_map' => 'sometimes|required|integer|min:1|max:1000',
            // 'description' => 'nullable|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        try {
            $booth->update($validator->validated());
            Log::info("Admin updated booth: " . $booth->id);
            return response()->json($booth);
        } catch (\Exception $e) {
            Log::error("Error updating booth by admin: " . $e->getMessage());
            return response()->json(['error' => 'Failed to update booth. Please check logs.'], 500);
        }
    }

    /**
     * Remove the specified booth from storage.
     */
    public function destroy(Booth $booth)
    {
        try {
            $jobFairId = $booth->job_fair_id; // For logging
            $boothId = $booth->id;
            
            // Consider what to do with BoothJobOpenings - cascade delete or prevent deletion if openings exist?
            // For now, assuming related job openings should be deleted or handled by DB foreign key constraints.
            // If BoothJobOpening has a foreign key constraint with cascade on delete, they will be auto-deleted.
            // Otherwise, you might need to delete them manually: $booth->jobOpenings()->delete();

            $booth->delete();
            Log::info("Admin deleted booth: " . $boothId . " from job fair: " . $jobFairId);
            return response()->json(null, 204);
        } catch (\Exception $e) {
            Log::error("Error deleting booth by admin: " . $e->getMessage());
            return response()->json(['error' => 'Failed to delete booth. It might be associated with other records or an internal error occurred.'], 500);
        }
    }
} 