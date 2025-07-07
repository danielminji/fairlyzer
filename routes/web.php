<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Cookie;
use Illuminate\Http\Response;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::get('/test-cookie', function () {
    $cookie = cookie('test_laravel_cookie', 'hello_world', 60, '/', 'localhost', false, true, false, 'lax'); 
    return response('Cookie test! Check your browser dev tools.')->withCookie($cookie);
});

Route::get('/', function () {
    return view('welcome');
});

Route::get('/dashboard', function () {
    return view('dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

// Ensure login route is not duplicated here if it's an API route
// Route::post('/login', [App\Http\Controllers\Auth\LoginController::class, 'login']); // Removed from here

// require __DIR__.'/auth.php'; // Temporarily commented out to resolve server start issue
