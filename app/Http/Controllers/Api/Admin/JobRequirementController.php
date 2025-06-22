<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\JobRequirement;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class JobRequirementController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        // Basic pagination and filtering by primary_field if provided
        $query = JobRequirement::query();
        if ($request->has('primary_field')) {
            $query->where('primary_field', $request->input('primary_field'));
        }
        $query->orderBy('primary_field')->orderBy('job_title');

        if ($request->input('per_page') === 'all' || $request->input('per_page') === -1) {
            $jobRequirements = $query->get();
            // Wrap in a structure similar to paginator for consistency if frontend expects it
            return response()->json(['data' => $jobRequirements]); 
        } else {
            $perPage = $request->input('per_page', 25); // Default to 25 if not specified
            $jobRequirements = $query->paginate($perPage);
            return response()->json($jobRequirements);
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
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

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $jobRequirement = JobRequirement::create($validator->validated());
        return response()->json($jobRequirement, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(JobRequirement $jobRequirement)
    {
        return response()->json($jobRequirement);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, JobRequirement $jobRequirement)
    {
        $validator = Validator::make($request->all(), [
            'job_title' => 'sometimes|required|string|max:255',
            'primary_field' => 'sometimes|required|string|in:computer_science,medical,finance,engineering,real_estate,environmental_science,marketing,design,logistics,urban_planning,architecture,general',
            'description' => 'nullable|string',
            'required_skills_general' => 'sometimes|required|array',
            'required_skills_general.*' => 'string|max:100',
            'required_skills_soft' => 'sometimes|required|array',
            'required_skills_soft.*' => 'string|max:100',
            'required_experience_years' => 'sometimes|required|integer|min:0',
            'required_experience_entries' => 'sometimes|required|integer|min:0',
            'required_cgpa' => 'sometimes|required|numeric|min:0|max:4.00',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $jobRequirement->update($validator->validated());
        return response()->json($jobRequirement);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(JobRequirement $jobRequirement)
    {
        $jobRequirement->delete();
        return response()->json(null, 204);
    }
} 