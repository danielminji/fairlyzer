<?php

namespace App\Http\Controllers\Api\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Log;

class SystemController extends Controller
{
    public function clearCache(Request $request)
    {
        try {
            Log::info('Admin requested cache clear.');
            Artisan::call('cache:clear');
            Artisan::call('config:clear');
            Artisan::call('route:clear');
            Artisan::call('view:clear');
            Log::info('Cache, config, route, and view caches cleared successfully.');
            return response()->json(['message' => 'System caches (application, config, route, view) cleared successfully.'], 200);
        } catch (\Exception $e) {
            Log::error('Error clearing cache: ' . $e->getMessage());
            return response()->json(['error' => 'Failed to clear system caches.', 'details' => $e->getMessage()], 500);
        }
    }
} 