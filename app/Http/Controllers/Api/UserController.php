<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Resume;
use App\Models\JobFair;
use App\Services\MailgunService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;
use Carbon\Carbon;
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
     * Get the authenticated user's profile.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function profile(Request $request)
    {
        $user = $request->user();
        return response()->json([
            'status' => 'success',
            'data' => $user
        ]);
    }

    /**
     * Update the authenticated user's profile.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function updateProfile(Request $request)
    {
        $user = $request->user();

        // Separate validation for profile data and password for clarity
        $profileData = $request->except(['current_password', 'new_password']);
        $passwordData = $request->only(['current_password', 'new_password']);

        // --- Profile Data Update ---
        if (!empty($profileData)) {
            $profileValidator = Validator::make($profileData, [
                'name' => 'sometimes|required|string|max:255',
                'email' => [
                    'sometimes',
                    'required',
                    'string',
                    'email',
                    'max:255',
                    Rule::unique('users')->ignore($user->id),
                ],
                'phone' => 'nullable|string|max:20',
                'location' => 'nullable|string|max:255',
                'linkedin_url' => 'nullable|url|max:255',
                'github_url' => 'nullable|url|max:255',
                'industry' => 'nullable|string|max:255',
                'experience_level' => 'nullable|string|max:255',
                'bio' => 'nullable|string|max:1000',
            ]);

            if ($profileValidator->fails()) {
                return response()->json(['status' => 'error', 'message' => 'Validation error', 'errors' => $profileValidator->errors()], 422);
            }

            $user->fill($profileValidator->validated());
        }

        // --- Password Update ---
        if (!empty($passwordData['current_password']) || !empty($passwordData['new_password'])) {
            $passwordValidator = Validator::make($passwordData, [
                'current_password' => 'required|string|min:8',
                'new_password' => 'required|string|min:8',
            ]);

            if ($passwordValidator->fails()) {
                return response()->json(['status' => 'error', 'message' => 'Validation error', 'errors' => $passwordValidator->errors()], 422);
            }

            if (!Hash::check($passwordData['current_password'], $user->password)) {
                return response()->json(['status' => 'error', 'message' => 'Current password is incorrect'], 422);
            }

            $user->password = Hash::make($passwordData['new_password']);
        }

        if ($user->isDirty()) {
            $user->save();
            return response()->json(['status' => 'success', 'message' => 'Profile updated successfully', 'data' => $user]);
        }

        return response()->json(['status' => 'success', 'message' => 'No changes were made.', 'data' => $user]);
    }

    /**
     * Upload the user's profile photo.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function uploadProfilePhoto(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'profile_photo' => 'required|image|max:2048',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'status' => 'error',
                'message' => 'Validation error',
                'errors' => $validator->errors()
            ], 422);
        }

        $user = $request->user();

        // Delete old photo if exists
        if ($user->profile_photo_path) {
            Storage::disk('public')->delete($user->profile_photo_path);
        }

        // Store new photo
        $path = $request->file('profile_photo')->store('profile-photos', 'public');
        $user->profile_photo_path = $path;
        $user->save();

        return response()->json([
            'status' => 'success',
            'message' => 'Profile photo uploaded successfully',
            'data' => [
                'profile_photo_path' => $path,
                'photo_url' => url('storage/' . $path)
            ]
        ]);
    }

    /**
     * Get all users (admin only).
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        try {
            $users = User::all();
            return response()->json(['data' => $users]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to retrieve users: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Get a specific user
     */
    public function show($id)
    {
        try {
            $user = User::findOrFail($id);
            return response()->json(['data' => $user]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'User not found'], 404);
        }
    }

    /**
     * Create a new user (admin only)
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8',
            'role' => 'required|in:user,organizer,admin',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }
        
        try {
            $user = User::create([
                'name' => $request->name,
                'email' => $request->email,
                'password' => Hash::make($request->password),
                'role' => $request->role,
                'is_active' => true,
            ]);
            
            return response()->json([
                'message' => 'User created successfully',
                'data' => $user
            ], 201);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to create user: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Update user information
     */
    public function update(Request $request, $id)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'string|max:255',
            'email' => 'string|email|max:255|unique:users,email,' . $id,
            'phone' => 'nullable|string|max:20',
            'location' => 'nullable|string|max:255',
            'bio' => 'nullable|string',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }
        
        try {
            $user = User::findOrFail($id);
            
            // Update fields that are provided
            if ($request->has('name')) $user->name = $request->name;
            if ($request->has('email')) $user->email = $request->email;
            if ($request->has('phone')) $user->phone = $request->phone;
            if ($request->has('location')) $user->location = $request->location;
            if ($request->has('bio')) $user->bio = $request->bio;
            
            $user->save();
            
            return response()->json([
                'message' => 'User updated successfully',
                'data' => $user
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to update user: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Update user role
     */
    public function updateRole(Request $request, $id)
    {
        $validator = Validator::make($request->all(), [
            'role' => 'required|in:user,organizer,admin',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }
        
        try {
            $user = User::findOrFail($id);
            $oldRole = $user->role;
            $user->role = $request->role;
            $user->save();
            
            // Notify user via email
            try {
                $this->emailService->sendStatusChange($user->email, $user->name, "Your account role has been changed from {$oldRole} to {$user->role}.");
            } catch (\Exception $e) {
                // Log email error but continue
                \Log::error("Failed to send role change email: " . $e->getMessage());
            }
            
            return response()->json([
                'message' => 'User role updated successfully',
                'data' => $user
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to update user role: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Toggle user active status
     */
    public function toggleStatus(Request $request, $id)
    {
        $validator = Validator::make($request->all(), [
            'is_active' => 'required|boolean',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }
        
        try {
            $user = User::findOrFail($id);
            $oldStatus = $user->is_active;
            $user->is_active = $request->is_active;
            $user->save();
            
            // Notify user via email
            try {
                $status = $user->is_active ? 'activated' : 'deactivated';
                $this->emailService->sendStatusChange($user->email, $user->name, "Your account has been {$status}.");
            } catch (\Exception $e) {
                // Log email error but continue
                \Log::error("Failed to send status change email: " . $e->getMessage());
            }
            
            return response()->json([
                'message' => 'User status updated successfully',
                'data' => $user
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to update user status: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Reset user password
     */
    public function resetPassword(Request $request, $id)
    {
        $validator = Validator::make($request->all(), [
            'password' => 'required|string|min:8',
        ]);
        
        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }
        
        try {
            $user = User::findOrFail($id);
            $user->password = Hash::make($request->password);
            $user->save();
            
            // Notify user via email
            try {
                $this->emailService->sendPasswordReset($user->email, $user->name);
            } catch (\Exception $e) {
                // Log email error but continue
                \Log::error("Failed to send password reset email: " . $e->getMessage());
            }
            
            return response()->json([
                'message' => 'User password reset successfully'
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to reset password: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Delete a user
     */
    public function destroy($id)
    {
        try {
            $user = User::findOrFail($id);
            
            // Store email before deletion
            $userEmail = $user->email;
            $userName = $user->name;
            
            // Delete the user
            $user->delete();
            
            // Notify user via email
            try {
                $this->emailService->sendAccountDeletion($userEmail, $userName);
            } catch (\Exception $e) {
                // Log email error but continue
                \Log::error("Failed to send account deletion email: " . $e->getMessage());
            }
            
            return response()->json([
                'message' => 'User deleted successfully'
            ]);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to delete user: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Get system-wide user statistics (admin only).
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function getStatistics(Request $request)
    {
        // Check if user is admin
        if (!$request->user()->isAdmin()) {
            return response()->json([
                'status' => 'error',
                'message' => 'Unauthorized access'
            ], 403);
        }

        // Get counts of various user types
        $totalUsers = User::count();
        $adminCount = User::where('role', 'admin')->count();
        $organizerCount = User::where('role', 'organizer')->count();
        $userCount = User::where('role', 'user')->count();
        
        // Get counts of resumes and job fairs
        $totalResumes = Resume::count();
        $totalJobFairs = JobFair::count();
        
        // Get recent registrations (last 30 days)
        $recentUsers = User::where('created_at', '>=', Carbon::now()->subDays(30))->count();
        
        // Get active users (users with uploaded resumes)
        $activeUsers = Resume::distinct('user_id')->count('user_id');
        
        // Get user growth over time (monthly for the last 6 months)
        $userGrowth = [];
        for ($i = 5; $i >= 0; $i--) {
            $month = Carbon::now()->subMonths($i);
            $count = User::whereYear('created_at', $month->year)
                ->whereMonth('created_at', $month->month)
                ->count();
            $userGrowth[] = [
                'month' => $month->format('M Y'),
                'count' => $count
            ];
        }

        return response()->json([
            'status' => 'success',
            'data' => [
                'total_users' => $totalUsers,
                'admin_count' => $adminCount,
                'organizer_count' => $organizerCount,
                'job_seeker_count' => $userCount,
                'total_resumes' => $totalResumes,
                'total_job_fairs' => $totalJobFairs,
                'recent_users' => $recentUsers,
                'active_users' => $activeUsers,
                'user_growth' => $userGrowth
            ]
        ]);
    }

    /**
     * Get user activity details (admin only).
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function getUserActivity(Request $request, $id)
    {
        // Check if user is admin
        if (!$request->user()->isAdmin()) {
            return response()->json([
                'status' => 'error',
                'message' => 'Unauthorized access'
            ], 403);
        }

        $user = User::findOrFail($id);
        
        // Get user's resumes
        $resumes = Resume::where('user_id', $id)
            ->orderBy('created_at', 'desc')
            ->get();
        
        // Get user's job fairs (if organizer)
        $jobFairs = [];
        if ($user->role === 'organizer') {
            $jobFairs = JobFair::where('user_id', $id)
                ->orderBy('created_at', 'desc')
                ->get();
        }
        
        // Get login history (requires adding a table for login history)
        // This would be implemented if we add login history tracking
        
        return response()->json([
            'status' => 'success',
            'data' => [
                'user' => $user,
                'resumes' => $resumes,
                'job_fairs' => $jobFairs,
                'created_at' => $user->created_at,
                'last_updated' => $user->updated_at
            ]
        ]);
    }

    /**
     * Delete the authenticated user's account.
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function destroySelf(Request $request)
    {
        $user = $request->user();
        
        // Store email before deletion for notification
        $userEmail = $user->email;
        $userName = $user->name;
        
        // Revoke all tokens to force logout on all devices
        $user->tokens()->delete();
        
        // Delete the user
        $user->delete();
        
        // Notify user via email
        try {
            $this->emailService->sendAccountDeletion($userEmail, $userName);
        } catch (\Exception $e) {
            // Log email error but continue
            \Log::error("Failed to send account deletion email: " . $e->getMessage());
        }
        
        return response()->json([
            'status' => 'success',
            'message' => 'Account deleted successfully.'
        ]);
    }
} 