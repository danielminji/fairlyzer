<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;

class LoginController extends Controller
{
    public function login(Request $request)
    {
        Log::info('Login attempt', ['email' => $request->email]);
        
        $credentials = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required'],
        ]);

        if (Auth::attempt($credentials, $request->filled('remember'))) {
            $user = Auth::user();
            
            if (!$user->isActive()) {
                Auth::logout();
                Log::warning('Login attempt by inactive user', ['email' => $request->email]);
                
                $message = $user->isOrganizer() 
                    ? 'Your organizer account is pending approval. You will receive an email when your account is approved.'
                    : 'Your account is inactive. Please contact the administrator.';
                return response()->json(['message' => $message], 403);
            }
            
            // --- BEGIN TEMPORARY DEBUG LOGS ---
            Log::debug('SESSION DEBUG: Before session regenerate', [
                'request_has_session' => $request->hasSession(),
                'session_manager_bound' => app()->bound('session'),
                'session_driver_config' => config('session.driver'),
                'route_middleware' => $request->route() ? $request->route()->gatherMiddleware() : 'No route resolved for middleware check'
            ]);

            if (app()->bound('session')) {
                Log::debug('SESSION DEBUG: Session store details', [
                    'session_store_id_before_start_check' => app('session')->getId(), // May error if not started
                    'session_is_started' => app('session')->isStarted(),
                ]);
            }
            // --- END TEMPORARY DEBUG LOGS ---
            
            $request->session()->regenerate();
            Log::info('User authenticated and session regenerated', ['user_id' => $user->id, 'role' => $user->role, 'session_id' => $request->session()->getId()]);
            
            // Create a new Sanctum token for API access
            $token = $user->createToken('auth-token')->plainTextToken;
            Log::info('Token created for user', ['user_id' => $user->id, 'token_preview' => substr($token, 0, 10) . '...']);
            
            return response()->json([
                'message' => 'Successfully logged in',
                'user' => $user,
                'token' => $token
            ]);
        }

        Log::warning('Login failed for credentials', ['email' => $request->email]);
        return response()->json([
            'message' => 'Invalid credentials'
        ], 401);
    }

    public function logout(Request $request)
    {
        // For token-based authentication, revoke the token that was used to authenticate the request
        if ($request->user() && $request->user()->currentAccessToken()) {
            $request->user()->currentAccessToken()->delete();
            Log::info('User token revoked', ['user_id' => $request->user()->id]);
        }

        // For web-based auth, logout the user
        Auth::guard('web')->logout();
        
        // Invalidate the session to clear any stateful auth
        if ($request->hasSession()) {
            $request->session()->invalidate();
            $request->session()->regenerateToken();
        }

        return response()->json([
            'message' => 'Successfully logged out'
        ]);
    }
} 