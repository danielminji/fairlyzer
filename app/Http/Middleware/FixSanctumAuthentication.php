<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class FixSanctumAuthentication
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // Debug the incoming request auth headers
        $authHeader = $request->header('Authorization');
        Log::debug('Auth header in middleware', [
            'header' => $authHeader,
            'has_bearer' => str_starts_with($authHeader, 'Bearer '),
            'token_length' => $authHeader ? strlen($authHeader) : 0,
            'endpoint' => $request->path(),
        ]);

        // Fix for missing or malformed Authorization header
        if (!$authHeader && $request->cookie('token')) {
            $request->headers->set('Authorization', 'Bearer ' . $request->cookie('token'));
            Log::debug('Set Authorization header from cookie', ['token' => substr($request->cookie('token'), 0, 10) . '...']);
        }

        // Fix for some clients that don't properly send Bearer token
        if ($authHeader && !str_starts_with($authHeader, 'Bearer ')) {
            $request->headers->set('Authorization', 'Bearer ' . trim(str_replace('Bearer', '', $authHeader)));
            Log::debug('Fixed malformed Bearer token');
        }

        // Add a fixed debug token for emergency access (only in local env)
        if (app()->environment('local') && $request->header('X-Debug-Token') === config('app.debug_token')) {
            Log::warning('Using debug token for access!');
            // Do not actually implement this in production!
            // This is just for debugging authentication
        }

        return $next($request);
    }
} 