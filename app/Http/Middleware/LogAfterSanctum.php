<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class LogAfterSanctum
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Log detailed authentication information before processing
        $authUser = auth()->user();
        $authId = auth()->id();
        $path = $request->path();
        
        // Log for any API requests to help diagnose the issue
        if (strpos($path, 'api/') === 0) {
            Log::debug('[MIDDLEWARE] LogAfterSanctum before processing request', [
                'path' => $path,
                'user_authenticated' => auth()->check(),
                'auth_id' => $authId,
                'auth_user_email' => $authUser ? $authUser->email : 'null',
                'auth_guard' => auth()->getDefaultDriver(),
                'session_id' => session()->getId() ?? 'no-session-id',
                'session_has_data' => !empty(session()->all()),
                'request_has_token' => !empty($request->bearerToken()),
                'token_preview' => $request->bearerToken() ? substr($request->bearerToken(), 0, 10) . '...' : 'null',
                'cookie_count' => count($request->cookies->all()),
                'has_xsrf_token' => $request->cookies->has('XSRF-TOKEN'),
                'has_session_cookie' => $request->cookies->has('resume_analyzer_api_session'),
            ]);
        }
        
        // Process the request
        $response = $next($request);
        
        // Log again after processing to see if anything changed
        if (strpos($path, 'api/') === 0) {
            Log::debug('[MIDDLEWARE] LogAfterSanctum after processing request', [
                'path' => $path,
                'user_authenticated' => auth()->check(),
                'auth_id' => auth()->id(),
                'response_status' => $response->getStatusCode(),
                'session_id' => session()->getId() ?? 'no-session-id',
            ]);
        }
        
        return $response;
    }
}
