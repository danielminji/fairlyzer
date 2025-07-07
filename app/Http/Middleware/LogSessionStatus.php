<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class LogSessionStatus
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure(\Illuminate\Http\Request): (\Illuminate\Http\Response|\Illuminate\Http\RedirectResponse)  $next
     * @return \Illuminate\Http\Response|\Illuminate\Http\RedirectResponse
     */
    public function handle(Request $request, Closure $next)
    {
        Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Entered.');
        
        if ($request->hasSession()) {
            Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Request has session.');
            if ($request->session()->isStarted()) {
                Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Session is started. Session ID: ' . $request->session()->getId());
                // Log all session data
                Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): All session data: ', $request->session()->all());
            } else {
                Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Session is NOT started, attempting to start.');
                try {
                    $request->session()->start();
                    Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Session started manually. Session ID: ' . $request->session()->getId());
                    Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): All session data after manual start: ', $request->session()->all());
                } catch (\Exception $e) {
                    Log::error('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Error starting session manually: ' . $e->getMessage());
                }
            }
        } else {
            Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Request does NOT have session.');
        }
        
        // Log cookies received by Laravel from the request
        Log::debug('DIAGNOSTIC MIDDLEWARE (LogSessionStatus): Cookies received by Laravel: ', $request->cookies->all());

        return $next($request);
    }
} 