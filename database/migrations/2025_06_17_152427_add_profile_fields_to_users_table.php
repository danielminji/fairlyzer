<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('phone')->nullable()->after('company_name');
            $table->string('location')->nullable()->after('phone');
            $table->string('industry')->nullable()->after('location');
            $table->string('experience_level')->nullable()->after('industry');
            $table->text('bio')->nullable()->after('experience_level');
            $table->string('linkedin_url')->nullable()->after('bio');
            $table->string('github_url')->nullable()->after('linkedin_url');
            $table->string('profile_photo_path', 2048)->nullable()->after('github_url');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn([
                'phone',
                'location',
                'industry',
                'experience_level',
                'bio',
                'linkedin_url',
                'github_url',
                'profile_photo_path',
                'notification_preferences',
                'profile_visibility',
                'share_data',
            ]);
        });
    }
};
