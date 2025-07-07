<?php

namespace App\Http\Controllers\Api\Organizer;

use App\Http\Controllers\Controller;
use App\Models\JobFair;
use App\Models\Booth;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class BoothController extends Controller
{
    use AuthorizesRequests;

    /**
     * Display a listing of booths for a specific job fair.
     * This is the primary index method used by routes.
     */
    public function indexForJobFair(JobFair $jobFair)
    {
        $this->authorize('view', $jobFair);
        // Load booths with their job openings eager-loaded for efficiency if needed by frontend
        // $booths = $jobFair->booths()->with('jobOpenings')->orderBy('booth_number_on_map', 'asc')->get();
        // For now, just booths. Frontend can fetch job openings per booth if/when needed.
        $booths = $jobFair->booths()->orderBy('id', 'asc')->get();
        return response()->json($booths);
    }

    /**
     * Store a newly created booth in storage.
     */
    public function store(Request $request, JobFair $jobFair)
    {
        $this->authorize('update', $jobFair);

        $validatedData = $request->validate([
            'company_name' => 'required|string|max:255',
            'booth_number_on_map' => 'required|numeric|max:255',
            // 'map_coordinates' => 'nullable|json' // Removed
        ]);

        $booth = new Booth($validatedData);
        $booth->job_fair_id = $jobFair->id;
        $booth->save();

        return response()->json($booth, 201);
    }

    /**
     * Display the specified booth.
     */
    public function show(JobFair $jobFair, Booth $booth)
    {
        $this->authorize('view', $booth->jobFair); // Authorize view against the parent job fair

        if ($booth->job_fair_id !== $jobFair->id && request()->route('jobFair')) { // Second condition is to ensure jobFair is from route if present
             // This check is a bit redundant if the route is /organizer/booths/{booth} and $jobFair is not part of it.
             // If routes are /organizer/job-fairs/{jobFair}/booths/{booth}
             // then check $booth->job_fair_id !== $jobFair->id
             // For /organizer/booths/{booth} this specific check might be removed or rethought.
        } // Keeping original check in case route structure implies it
        
        return response()->json($booth);
    }

    /**
     * Update the specified booth in storage.
     */
    public function update(Request $request, Booth $booth)
    {
        $jobFair = $booth->jobFair; 
        $this->authorize('update', $jobFair);

        $validatedData = $request->validate([
            'company_name' => 'sometimes|required|string|max:255',
            'booth_number_on_map' => 'sometimes|required|numeric|max:255',
            // 'map_coordinates' => 'sometimes|nullable|json' // Removed
        ]);

        $booth->fill($validatedData);
        $booth->save();

        return response()->json($booth);
    }

    /**
     * Remove the specified booth from storage.
     */
    public function destroy(Booth $booth)
    {
        $jobFair = $booth->jobFair;
        $this->authorize('update', $jobFair); // Deleting a booth is an update-like action on the job fair

        // Associated booth_job_openings will be deleted by database cascade if set up correctly.
        // If not, they should be manually deleted here: $booth->jobOpenings()->delete();
        // The onDelete('cascade') in the migration should handle this.
        $booth->delete();

        return response()->json(null, 204);
    }
}
