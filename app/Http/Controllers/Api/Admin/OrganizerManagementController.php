<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Services\MailgunService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log; // For logging

class OrganizerManagementController extends Controller
{
    /**
     * Email Service instance
     */
    protected $emailService;

    /**
     * Create a new controller instance.
     */
    public function __construct(MailgunService $emailService)
    {
        $this->emailService = $emailService;
    }

    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(User $user)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, User $user)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(User $user)
    {
        //
    }

    /**
     * List users pending organizer approval.
     */
    public function listPending()
    {
        // Ensure only admins can access this - will be handled by route middleware
        $pendingOrganizers = User::where('role', 'pending_organizer_approval')->get();
        return response()->json(['data' => $pendingOrganizers]);
    }

    /**
     * Approve an organizer application.
     */
    public function approve(Request $request, User $user) // Type hint User for route model binding
    {
        if ($user->role !== 'pending_organizer_approval') {
            return response()->json(['message' => 'User is not pending organizer approval.'], 422);
        }

        $user->role = 'organizer';
        $user->save();

        // Send notification to the user about approval
        try {
            $this->emailService->sendOrganizerApproval($user->email, $user->name);
            Log::info("Approval email sent to organizer: User ID {$user->id}");
        } catch (\Exception $e) {
            Log::error("Failed to send organizer approval email: " . $e->getMessage());
        }

        Log::info("Organizer approved: User ID {$user->id}");

        return response()->json(['message' => 'Organizer approved successfully.', 'user' => $user]);
    }

    /**
     * Reject an organizer application.
     */
    public function reject(Request $request, User $user) // Type hint User for route model binding
    {
        if ($user->role !== 'pending_organizer_approval') {
            return response()->json(['message' => 'User is not pending organizer approval.'], 422);
        }

        // Option 1: Revert to a standard 'user' role
        $user->role = 'user'; 
        $user->save();

        // Send notification to the user about rejection
        try {
            $this->emailService->sendOrganizerRejection($user->email, $user->name);
            Log::info("Rejection email sent to user: User ID {$user->id}");
        } catch (\Exception $e) {
            Log::error("Failed to send organizer rejection email: " . $e->getMessage());
        }

        Log::info("Organizer rejected: User ID {$user->id}");

        return response()->json(['message' => 'Organizer application rejected.', 'user' => $user]);
    }

    /**
     * List all approved organizers.
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function listApproved()
    {
        $approvedOrganizers = User::where('role', 'organizer')->get();
        return response()->json(['data' => $approvedOrganizers]);
    }
}
