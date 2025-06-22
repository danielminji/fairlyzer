<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;
use App\Services\MailgunService;
use Illuminate\Support\Facades\Log;

class UserController extends Controller
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
    public function index(Request $request)
    {
        $query = User::query();
        
        // Add search functionality
        if ($request->has('search')) {
            $search = $request->input('search');
            $query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%");
            });
        }
        
        // Add role filter
        if ($request->has('role')) {
            $query->where('role', $request->input('role'));
        }
        
        // Add status filter
        if ($request->has('is_active')) {
            $query->where('is_active', $request->boolean('is_active'));
        }
        
        $users = $query->orderBy('created_at', 'desc')->get();
        return response()->json(['data' => $users]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8',
            'role' => 'required|string|in:admin,organizer,user,pending_organizer_approval',
            'is_active' => 'boolean'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'role' => $request->role,
            'is_active' => $request->boolean('is_active', true),
            'email_verified_at' => now(), // Admin created users are auto-verified
        ]);

        return response()->json(['data' => $user], 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(User $user)
    {
        return response()->json(['data' => $user]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, User $user)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'sometimes|required|string|max:255',
            'email' => ['sometimes', 'required', 'string', 'email', 'max:255', Rule::unique('users')->ignore($user->id)],
            'role' => 'sometimes|required|string|in:admin,organizer,user,pending_organizer_approval',
            'is_active' => 'sometimes|boolean'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $user->update($validator->validated());
        return response()->json(['data' => $user]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(User $user)
    {
        // Prevent admin from deleting themselves
        if ($user->id === auth()->id()) {
            return response()->json(['error' => 'You cannot delete your own account'], 403);
        }

        $user->delete();
        return response()->json(['message' => 'User deleted successfully'], 200);
    }

    /**
     * Update user role
     */
    public function updateRole(Request $request, User $user)
    {
        $validator = Validator::make($request->all(), [
            'role' => 'required|string|in:admin,organizer,user,pending_organizer_approval'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        // Prevent admin from changing their own role
        if ($user->id === auth()->id()) {
            return response()->json(['error' => 'You cannot change your own role'], 403);
        }

        $oldRole = $user->role;
        $user->update(['role' => $request->role]);

        // Notify user if role changed
        if ($oldRole !== $request->role) {
            try {
                $message = "Your account role has been updated to " . $request->role . ".";
                $this->emailService->sendStatusChange($user->email, $user->name, $message);
            } catch (\Exception $e) {
                // Log but continue
                Log::error('Failed to send role change notification: ' . $e->getMessage());
            }
        }

        return response()->json(['data' => $user, 'message' => 'Role updated successfully']);
    }

    /**
     * Toggle user active status
     */
    public function toggleStatus(Request $request, User $user)
    {
        $validator = Validator::make($request->all(), [
            'is_active' => 'required|boolean'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        // Prevent admin from deactivating themselves
        if ($user->id === auth()->id()) {
            return response()->json(['error' => 'You cannot deactivate your own account'], 403);
        }

        $oldStatus = $user->is_active;
        $user->update(['is_active' => $request->boolean('is_active')]);
        $status = $request->boolean('is_active') ? 'activated' : 'deactivated';

        // Notify user if status changed
        if ($oldStatus !== $request->boolean('is_active')) {
            try {
                $message = "Your account has been {$status}.";
                $this->emailService->sendStatusChange($user->email, $user->name, $message);
            } catch (\Exception $e) {
                // Log but continue
                Log::error('Failed to send status change notification: ' . $e->getMessage());
            }
        }

        return response()->json(['data' => $user, 'message' => "User {$status} successfully"]);
    }

    /**
     * Reset user password
     */
    public function resetPassword(Request $request, User $user)
    {
        $validator = Validator::make($request->all(), [
            'password' => 'required|string|min:8|confirmed'
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $user->update([
            'password' => Hash::make($request->password)
        ]);

        // Notify user via EmailJS
        try {
            $this->emailService->sendPasswordReset($user->email, $user->name);
        } catch (\Exception $e) {
            // Log but continue
            Log::error('Failed to send password reset notification: ' . $e->getMessage());
        }

        return response()->json(['message' => 'Password reset successfully']);
    }

    /**
     * Get user statistics
     */
    public function statistics()
    {
        $stats = [
            'total_users' => User::count(),
            'active_users' => User::where('is_active', true)->count(),
            'inactive_users' => User::where('is_active', false)->count(),
            'admins' => User::where('role', 'admin')->count(),
            'organizers' => User::where('role', 'organizer')->count(),
            'job_seekers' => User::where('role', 'user')->count(),
            'pending_organizers' => User::where('role', 'pending_organizer_approval')->count(),
            'recent_registrations' => User::where('created_at', '>=', now()->subDays(7))->count(),
        ];

        return response()->json(['data' => $stats]);
    }
} 