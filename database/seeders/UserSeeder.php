<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use App\Models\User;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Admin User
        User::updateOrCreate(
            ['email' => 'admin@example.com'],
            [
                'name' => 'Admin User',
                'password' => Hash::make('password'),
                'role' => 'admin',
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );

        // Job Seeker Users (role 'user' is the default in model, but explicit here is fine)
        User::updateOrCreate(
            ['email' => 'asa@gmail.com'],
            [
                'name' => 'Asa JobSeeker',
                'password' => Hash::make('password'),
                'role' => 'user', // Changed from job_seeker to user for consistency
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );

        User::updateOrCreate(
            ['email' => 'bob@example.com'],
            [
                'name' => 'Bob The Seeker',
                'password' => Hash::make('password'),
                'role' => 'user', // Changed from job_seeker to user
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );

        // Approved Organizer User
        User::updateOrCreate(
            ['email' => 'organizer_active@example.com'],
            [
                'name' => 'Active Organizer Inc.',
                'password' => Hash::make('password'),
                'role' => 'organizer',
                'company_name' => 'Active Org Ltd.', // Added company name
                'is_active' => true, 
                'email_verified_at' => now(),
            ]
        );

        // Pending Organizer User (for admin approval testing)
        User::updateOrCreate(
            ['email' => 'organizer_pending@example.com'],
            [
                'name' => 'Pending Organizer Co.',
                'password' => Hash::make('password'),
                'role' => 'pending_organizer_approval', // Changed role
                'company_name' => 'Pending Solutions', // Added company name
                'is_active' => true, // Changed to true, role dictates access
                'email_verified_at' => now(), 
            ]
        );

        User::updateOrCreate(
            ['email' => 'another@example.com'],
            [
                'name' => 'Another JobSeeker',
                'password' => Hash::make('password'),
                'role' => 'user', // Changed from job_seeker to user
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
    }
}
