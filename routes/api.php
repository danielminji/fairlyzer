<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\Api\EnhancedResumeController;
use App\Http\Controllers\Api\Organizer\JobFairController as OrganizerJobFairController;
use App\Http\Controllers\Api\Organizer\BoothController as OrganizerBoothController;
use App\Http\Controllers\Api\Organizer\BoothJobOpeningController as OrganizerBoothJobOpeningController;
use App\Http\Controllers\Api\Admin\OrganizerManagementController;
use Illuminate\Support\Facades\Log;
use App\Http\Controllers\Api\UserProfileController;
use App\Http\Controllers\Auth\RegisterController;
use App\Http\Controllers\Api\UserController;
use App\Http\Controllers\Dev\ReferenceResumeController;
use Illuminate\Session\Middleware\StartSession;
use App\Models\User;
use App\Http\Controllers\Api\PublicJobFairController;
use App\Http\Controllers\Api\JobSeeker\PersonalizedBoothRecommendationController;
// Make sure BoothRecommendationController is removed if the file is deleted, or comment out if file remains for other reasons.
// use App\Http\Controllers\Api\JobSeeker\BoothRecommendationController;

// Test route - place it high for visibility during testing
Route::post('approve_user_test/{user}', function (User $user) {
    Log::info("Direct approve_user_test reached for user ID: " . $user->id);
    if ($user->role !== 'pending_organizer_approval') {
        // return response()->json(['message' => 'User is not pending organizer approval for direct test.'], 422); // Optional check
    }
    $user->role = 'organizer'; 
    $user->save();
    return response()->json(['message' => 'Direct approve_user_test successful', 'user' => $user]);
})->whereNumber('user');

// Authentication routes (no middleware, CSRF exempt)
Route::post('/register', [RegisterController::class, 'register']);
Route::post('/login', [LoginController::class, 'login'])->middleware([StartSession::class, \App\Http\Middleware\LogSessionStatus::class]);
Route::post('/logout', [LoginController::class, 'logout'])->middleware(['auth:sanctum']);
Route::get('/user', [UserController::class, 'profile'])->middleware('auth:sanctum');

// Resume analysis debug route - uses exact same middleware as the actual endpoint
Route::get('/debug-resume-analysis/{resume}', function(\App\Models\Resume $resume) {
    $user = auth()->user();
    
    return response()->json([
        'status' => 'debug_info',
        'auth_check' => auth()->check(),
        'user_id' => $user ? $user->id : null,
        'resume_owner_id' => $resume->user_id,
        'is_owner' => $user && $user->id === $resume->user_id,
        'auth_guard' => auth()->getDefaultDriver(),
        'session_id' => session()->getId(),
        'cookies' => request()->cookies->all(),
        'user_token' => request()->bearerToken() ? 'Present' : 'Missing',
    ]);
})->middleware(['auth:sanctum']);

// Public routes
Route::get('/resumes/{resume}/recommendations', [EnhancedResumeController::class, 'recommendations']);
Route::get('/resumes/{resume}/detailed-analysis', [EnhancedResumeController::class, 'detailedAnalysis']);
Route::get('/job-fairs/{jobFair}/booths-list', [\App\Http\Controllers\Api\Organizer\JobFairController::class, 'listBooths']);

// New Public Job Fair Routes
Route::get('/public/job-fairs', [PublicJobFairController::class, 'index'])->name('public.job-fairs.index');
Route::get('/public/job-fairs/{jobFair}', [PublicJobFairController::class, 'show'])->name('public.job-fairs.show');
Route::get('/public/job-fairs/{jobFair}/directions', [PublicJobFairController::class, 'getDirections'])->name('public.job-fairs.directions');

// Debug routes
Route::get('/auth-debug', function() {
    $token = request()->bearerToken();
    $authHeader = request()->header('Authorization');
    
    Log::debug('Auth debug endpoint called', [
        'has_token' => !empty($token),
        'token_preview' => $token ? substr($token, 0, 10) . '...' : 'None',
        'token_length' => $token ? strlen($token) : 0,
        'auth_header' => $authHeader ? substr($authHeader, 0, 20) . '...' : 'None',
        'auth_header_length' => $authHeader ? strlen($authHeader) : 0,
        'all_headers' => request()->headers->all(),
    ]);
    
    return response()->json([
        'auth_header_exists' => !empty($authHeader),
        'token_exists' => !empty($token),
        'auth_check' => auth()->check(),
        'auth_user' => auth()->user(),
        'auth_id' => auth()->id(),
        'message' => 'Authentication debug information',
    ]);
});

// CSRF Token route
Route::get('/csrf-token', function () {
    return response()->json([
        'token' => csrf_token()
    ]);
});

// Enhanced parser test route (development only)
Route::get('/dev/test-enhanced-parser', [EnhancedResumeController::class, 'testEnhancedParser']);

// Mail Configuration Check route
Route::get('/check-mail-config', function () {
    $mailConfig = config('mail');
    $mailDriverConfigured = !empty($mailConfig['default']) && $mailConfig['default'] != 'log';
    $fromAddressConfigured = !empty($mailConfig['from']['address']) && $mailConfig['from']['address'] != 'hello@example.com';
    
    return response()->json([
        'mail_configured' => $mailDriverConfigured && $fromAddressConfigured,
        'mail_driver' => $mailConfig['default'],
        'from_address' => $mailConfig['from']['address'],
        'from_name' => $mailConfig['from']['name'],
    ]);
});

// Protected routes
Route::middleware(['auth:sanctum'])->group(function () {
    // Debug route to test authorization
    Route::get('/auth-test', function() {
        return response()->json([
            'message' => 'You are authenticated!',
            'user' => auth()->user()
        ]);
    });
    
    // Resume routes
    Route::get('/resumes', [EnhancedResumeController::class, 'index']);
    Route::post('/resumes', [EnhancedResumeController::class, 'upload']);
    Route::get('/resumes/{resume}', [EnhancedResumeController::class, 'show']);
    Route::delete('/resumes/{resume}', [EnhancedResumeController::class, 'destroy']);
    Route::get('/resumes/{resume}/analysis', [EnhancedResumeController::class, 'analysis']);
    Route::get('/my-resumes-list', [EnhancedResumeController::class, 'listForSelection']);

    // Job Seeker: Personalized Booth Recommendations for a specific resume and job fair
    Route::get('/resumes/{resume}/job-fairs/{jobFair}/personalized-booth-recommendations',
        [PersonalizedBoothRecommendationController::class, 'getRecommendations'])
        ->name('jobseeker.personalized.booth.recommendations')
        ->whereNumber(['resume', 'jobFair']); // Ensures resume and jobFair are numeric IDs for route model binding

    // Endpoint for job seekers to get openings for a specific job fair
    Route::get('/job-fairs/{jobFair}/openings', [PublicJobFairController::class, 'getFairOpenings'])
        ->name('job-fairs.openings')
        ->whereNumber('jobFair'); // Ensure jobFair ID is a number

    // Job Seeker: Booth Recommendations - ROUTE REMOVED
    // Route::get('/resumes/{resume_id}/job-fairs/{job_fair_id}/booth-recommendations',
    //     [\App\Http\Controllers\Api\JobSeeker\BoothRecommendationController::class, 'getBoothRecommendations'])
    //     ->name('jobseeker.booth.recommendations')
    //     ->whereNumber(['resume_id', 'job_fair_id']);

    Route::put('/user', [UserController::class, 'updateProfile']);
    Route::post('/user/photo', [UserController::class, 'uploadProfilePhoto']);
    Route::delete('/user', [UserController::class, 'destroySelf']);
});
    
// Admin routes
Route::middleware(['auth:sanctum', \App\Http\Middleware\AdminMiddleware::class])
    ->prefix('admin')
    ->name('admin.')
    ->group(function () {
        Route::apiResource('job-requirements', \App\Http\Controllers\Api\Admin\JobRequirementController::class);
        
        // Specific User routes BEFORE apiResource
        Route::get('users/statistics', [\App\Http\Controllers\Api\Admin\UserController::class, 'statistics']);
        // Add other specific user routes here if they exist and are defined later, e.g., role, status, reset-password
        Route::put('users/{user}/role', [\App\Http\Controllers\Api\Admin\UserController::class, 'updateRole'])->whereNumber('user');
        Route::put('users/{user}/status', [\App\Http\Controllers\Api\Admin\UserController::class, 'toggleStatus'])->whereNumber('user');
        Route::post('users/{user}/reset-password', [\App\Http\Controllers\Api\Admin\UserController::class, 'resetPassword'])->whereNumber('user');
        
        Route::apiResource('users', \App\Http\Controllers\Api\Admin\UserController::class);
        
        // Specific Job Fair routes BEFORE apiResource to avoid conflict
        Route::get('job-fairs/statistics', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'statistics']);
        Route::get('job-fairs/organizers', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'getOrganizers']);
        Route::post('job-fairs/bulk-update-status', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'bulkUpdateStatus']);

        Route::apiResource('job-fairs', \App\Http\Controllers\Api\Admin\JobFairController::class);
        
        // Additional Job Fair Management Routes
        Route::get('job-fairs/statistics', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'statistics']);
        Route::get('job-fairs/organizers', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'getOrganizers']);
        Route::post('job-fairs/bulk-update-status', [\App\Http\Controllers\Api\Admin\JobFairController::class, 'bulkUpdateStatus']);
        
        // Organizer Management Routes - More explicit definitions
        Route::get('organizers/pending', [\App\Http\Controllers\Api\Admin\OrganizerManagementController::class, 'listPending']);
        Route::get('organizers/approved', [\App\Http\Controllers\Api\Admin\OrganizerManagementController::class, 'listApproved']);
        Route::post('organizers/{user}/approve', [\App\Http\Controllers\Api\Admin\OrganizerManagementController::class, 'approve'])->whereNumber('user')->name('organizers.approve.specific');
        Route::post('organizers/{user}/reject', [\App\Http\Controllers\Api\Admin\OrganizerManagementController::class, 'reject'])->whereNumber('user');

        // System utility routes
        Route::post('system/clear-cache', [\App\Http\Controllers\Api\Admin\SystemController::class, 'clearCache']);

        // Booths Admin Routes (New)
        Route::get('/job-fairs/{jobFair}/booths', [\App\Http\Controllers\Api\Admin\BoothController::class, 'index'])->name('admin.job-fairs.booths.index');
        Route::post('/job-fairs/{jobFair}/booths', [\App\Http\Controllers\Api\Admin\BoothController::class, 'store'])->name('admin.job-fairs.booths.store');
        Route::get('/booths/{booth}', [\App\Http\Controllers\Api\Admin\BoothController::class, 'show'])->name('admin.booths.show');
        Route::put('/booths/{booth}', [\App\Http\Controllers\Api\Admin\BoothController::class, 'update'])->name('admin.booths.update');
        Route::delete('/booths/{booth}', [\App\Http\Controllers\Api\Admin\BoothController::class, 'destroy'])->name('admin.booths.destroy');
    });

// New Organizer Specific Routes
Route::middleware(['auth:sanctum', \Laravel\Sanctum\Http\Middleware\CheckAbilities::class . ':organizer'])
    ->prefix('organizer')
    ->name('organizer.')
    ->group(function () {
        Route::apiResource('job-fairs', OrganizerJobFairController::class);
        
        // Routes for Booths within a JobFair
        Route::get('job-fairs/{jobFair}/booths', [OrganizerBoothController::class, 'indexForJobFair'])->name('job-fairs.booths.index');
        Route::post('job-fairs/{jobFair}/booths', [OrganizerBoothController::class, 'store'])->name('job-fairs.booths.store');
        
        // Routes for individual Booth management (show, update, delete)
        // Note: 'booths' is already singular in the resource controller method parameters e.g. Booth $booth
        Route::apiResource('booths', OrganizerBoothController::class)->except(['index', 'store']);

        // Routes for Booth Job Openings (nested under a specific booth)
        // GET /organizer/booths/{booth}/job-openings - Index for a booth's job openings
        // POST /organizer/booths/{booth}/job-openings - Store a new job opening for a booth
        Route::get('booths/{booth}/job-openings', [OrganizerBoothJobOpeningController::class, 'index'])->name('booths.job-openings.index');
        Route::post('booths/{booth}/job-openings', [OrganizerBoothJobOpeningController::class, 'store'])->name('booths.job-openings.store');
        
        // Routes for individual Job Opening management (show, update, delete)
        // These are not nested under /booths/{booth}/ because the {boothJobOpening} ID is globally unique.
        // The controller methods will use $boothJobOpening->booth to get parent context if needed.
        // GET /organizer/job-openings/{boothJobOpening}
        // PUT/PATCH /organizer/job-openings/{boothJobOpening}
        // DELETE /organizer/job-openings/{boothJobOpening}
        Route::apiResource('job-openings', OrganizerBoothJobOpeningController::class)->except(['index', 'store'])->parameters([
            'job-openings' => 'boothJobOpening' // Map 'job-openings' parameter to 'boothJobOpening' for route model binding
        ]);
    });

Route::middleware(['auth:sanctum', 'ability:job_seeker,admin'])->group(function () {
    // Booth Recommendations for Job Seekers - SECTION REMOVED
    // Route::get('/resumes/{resumeId}/job-fairs/{jobFairId}/booth-recommendations', [BoothRecommendationController::class, 'getBoothRecommendations'])
    //     ->name('jobseeker.booth.recommendations');
});
