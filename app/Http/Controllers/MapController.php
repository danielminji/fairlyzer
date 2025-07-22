<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Response;

class MapController extends Controller
{
    public function download($filename)
    {
        $path = storage_path('app/public/job_fair_maps/' . $filename);
        if (!file_exists($path)) {
            abort(404);
        }
        return response()->download($path, $filename);
    }
} 