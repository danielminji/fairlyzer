<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Config;

class CustomSessionMiddleware
{
    public function handle(Request $request, Closure $next)
    {
        // Make sure sessions work for API routes
        Config::set('session.driver', 'database'); // Explicitly set to database
        Config::set('session.lifetime', 24 * 60); // 24 hours
        Config::set('session.expire_on_close', false);
        Config::set('session.same_site', 'lax');
        Config::set('session.secure', false); // Set to false for local development
        
        // Ensure session cookie is always set for API routes
        $response = $next($request);
        
        // Make sure session ID cookie is set properly
        $config = config('session');
        $minutes = $config['lifetime'];
        
        if ($request->session()->isStarted()) {
            $cookie = cookie(
                $config['cookie'],
                $request->session()->getId(),
                $minutes,
                $config['path'],
                $config['domain'],
                $config['secure'] ?? false,
                $config['http_only'] ?? true,
                false,
                'lax'
            );
            
            return $response->withCookie($cookie);
        }
        
        return $response;
    }
} 