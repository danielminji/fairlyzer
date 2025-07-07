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
        Schema::create('job_requirements', function (Blueprint $table) {
            $table->id();
            $table->string('job_title');
            $table->string('primary_field'); // e.g., Computer Science, Medical, Finance
            $table->text('description')->nullable();
            $table->json('required_skills_general'); // Array of general skills
            $table->json('required_skills_soft'); // Array of soft skills
            $table->integer('required_experience_years'); // Minimum years of experience
            $table->integer('required_experience_entries'); // Minimum number of distinct work experiences
            $table->decimal('required_cgpa', 3, 2); // Minimum CGPA (e.g., 3.50)
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('job_requirements');
    }
};
