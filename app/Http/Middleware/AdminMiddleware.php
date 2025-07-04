<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class AdminMiddleware
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
        // Check if user is authenticated and is an admin
        if (!$request->user() || $request->user()->role !== 'admin') {
            return response()->json([
                'error' => 'Unauthorized. Admin access required.'
            ], 403);
        }

        return $next($request);
    }
} 