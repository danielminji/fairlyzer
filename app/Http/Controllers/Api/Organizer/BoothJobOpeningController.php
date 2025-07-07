<?php

namespace App\Http\Controllers\Api\Organizer;

use App\Models\BoothJobOpening;
use App\Models\Booth;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests; // For policy checks

class BoothJobOpeningController extends Controller
{
    use AuthorizesRequests;

    /**
     * Display a listing of the job openings for a specific booth.
     */
    public function index(Booth $booth)
    {
        // Authorize that the current user can view the parent booth (which implies viewing its job openings)
        // This relies on BoothPolicy or JobFairPolicy being set up correctly to check ownership.
        $this->authorize('view', $booth->jobFair); 

        return response()->json($booth->jobOpenings()->orderBy('created_at', 'desc')->get());
    }

    /**
     * Store a newly created job opening in storage for a specific booth.
     */
    public function store(Request $request, Booth $booth)
    {
        // Authorize that the current user can update the parent booth (i.e., add job openings to it)
        $this->authorize('update', $booth->jobFair);

        $validatedData = $request->validate([
            'job_title' => 'required|string|max:255',
            'primary_field' => 'required|string|in:computer_science,medical,finance,engineering,real_estate,environmental_science,marketing,design,logistics,urban_planning,architecture,general',
            'description' => 'nullable|string',
            'required_skills_general' => 'required|array',
            'required_skills_general.*' => 'string|max:100',
            'required_skills_soft' => 'required|array',
            'required_skills_soft.*' => 'string|max:100',
            'required_experience_years' => 'required|integer|min:0',
            'required_experience_entries' => 'required|integer|min:0',
            'required_cgpa' => 'required|numeric|min:0|max:4.00', // Assuming max CGPA is 4.00
        ]);

        // Laravel's $casts on the model should handle array conversion for JSON fields automatically
        // when creating/updating if the input is already an array (e.g., from JSON request body).

        $jobOpening = $booth->jobOpenings()->create([
            'organizer_id' => Auth::id(), // Assign the currently authenticated organizer
            'job_title' => $validatedData['job_title'],
            'primary_field' => $validatedData['primary_field'],
            'description' => $validatedData['description'],
            'required_skills_general' => $validatedData['required_skills_general'],
            'required_skills_soft' => $validatedData['required_skills_soft'],
            'required_experience_years' => $validatedData['required_experience_years'],
            'required_experience_entries' => $validatedData['required_experience_entries'],
            'required_cgpa' => $validatedData['required_cgpa'],
        ]);

        return response()->json($jobOpening, 201);
    }

    /**
     * Display the specified job opening.
     */
    public function show(BoothJobOpening $boothJobOpening)
    {
        // Authorize that the current user can view the job opening (indirectly via its parent booth's job fair)
        $this->authorize('view', $boothJobOpening->booth->jobFair);
        
        return response()->json($boothJobOpening);
    }

    /**
     * Update the specified job opening in storage.
     */
    public function update(Request $request, BoothJobOpening $boothJobOpening)
    {
        // Authorize that the current user can update the job opening
        $this->authorize('update', $boothJobOpening->booth->jobFair);

        // Additional check: ensure the current user is the one who created this job opening
        if ($boothJobOpening->organizer_id !== Auth::id()) {
            return response()->json(['message' => 'Forbidden: You did not create this job opening.'], 403);
        }

        $validatedData = $request->validate([
            'job_title' => 'sometimes|required|string|max:255',
            'primary_field' => 'sometimes|required|string|in:computer_science,medical,finance,engineering,real_estate,environmental_science,marketing,design,logistics,urban_planning,architecture,general',
            'description' => 'sometimes|nullable|string',
            'required_skills_general' => 'sometimes|required|array',
            'required_skills_general.*' => 'string|max:100',
            'required_skills_soft' => 'sometimes|required|array',
            'required_skills_soft.*' => 'string|max:100',
            'required_experience_years' => 'sometimes|required|integer|min:0',
            'required_experience_entries' => 'sometimes|required|integer|min:0',
            'required_cgpa' => 'sometimes|required|numeric|min:0|max:4.00',
        ]);

        // Model $casts will handle JSON conversion for array fields.
        $boothJobOpening->update($validatedData);

        return response()->json($boothJobOpening);
    }

    /**
     * Remove the specified job opening from storage.
     */
    public function destroy(BoothJobOpening $boothJobOpening)
    {
        // Authorize deletion
        $this->authorize('delete', $boothJobOpening->booth->jobFair);
        // Policy for 'delete' on JobFair might be too broad. 
        // We might need a BoothJobOpeningPolicy or check organizer_id.

        if ($boothJobOpening->organizer_id !== Auth::id()) {
            return response()->json(['message' => 'Forbidden: You did not create this job opening.'], 403);
        }

        $boothJobOpening->delete();

        return response()->json(null, 204);
    }
}
