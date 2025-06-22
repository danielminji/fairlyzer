<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Services\MailgunService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Validator;
use Illuminate\Auth\Events\Registered;

class RegisterController extends Controller
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
     * Handle a registration request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'string', 'email', 'max:255', 'unique:users'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
            'user_type' => ['sometimes', 'string', 'in:user,organizer_applicant'],
            'company_name' => ['nullable', 'string', 'max:255', 'required_if:user_type,organizer_applicant'],
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $userType = $request->input('user_type', 'user');
        $roleToSet = 'user';
        $message = 'User registered successfully.';

        if ($userType === 'organizer_applicant') {
            $roleToSet = 'pending_organizer_approval';
            $message = 'Organizer registration successful. Awaiting admin approval.';
        }

        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'role' => $roleToSet,
            'company_name' => $request->input('company_name'),
            'is_active' => true,
            'email_verified_at' => now(),
        ]);

        event(new Registered($user));
        
        // If this is an organizer application, notify admin and the organizer
        if ($userType === 'organizer_applicant') {
            $this->notifyAdminOfOrganizerApplication($user);
            $this->notifyOrganizerOfPendingApproval($user);
        }

        return response()->json([
            'message' => $message,
            'user' => $user,
        ], 201);
    }
    
    /**
     * Notify admin about a new organizer application
     *
     * @param User $user The user who applied to be an organizer
     * @return void
     */
    protected function notifyAdminOfOrganizerApplication(User $user)
    {
        try {
            // Get all admin users
            $admins = User::where('role', 'admin')->get();
            
            if ($admins->isEmpty()) {
                Log::warning("No admin users found to notify about new organizer application.");
                return;
            }
            
            foreach ($admins as $admin) {
                $this->emailService->sendOrganizerApplicationNotification(
                    $admin->email,
                    $admin->name,
                    $user->name,
                    $user->email,
                    $user->company_name ?? ''
                );
            }
            
            Log::info("Admin notification sent for new organizer application: User ID {$user->id}");
        } catch (\Exception $e) {
            Log::error("Failed to send admin notification: " . $e->getMessage());
        }
    }
    
    /**
     * Notify organizer that their application is pending approval
     *
     * @param User $user The user who applied to be an organizer
     * @return void
     */
    protected function notifyOrganizerOfPendingApproval(User $user)
    {
        try {
            $this->emailService->sendOrganizerApplicationReceived($user->email, $user->name);
            Log::info("Confirmation email sent to organizer applicant: User ID {$user->id}");
        } catch (\Exception $e) {
            Log::error("Failed to send organizer application confirmation: " . $e->getMessage());
        }
    }
} 