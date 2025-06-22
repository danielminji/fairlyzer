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
        Schema::create('booth_job_openings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('booth_id')->constrained('booths')->onDelete('cascade');
            $table->foreignId('organizer_id')->constrained('users')->onDelete('cascade'); // The organizer who defined this job opening
            $table->string('job_title');
            $table->string('primary_field'); // e.g., Computer Science, Medical, Finance, General
            $table->text('description')->nullable();
            $table->json('required_skills_general'); // Array of strings
            $table->json('required_skills_soft'); // Array of strings
            $table->integer('required_experience_years')->unsigned();
            $table->integer('required_experience_entries')->unsigned(); // Number of distinct experience entries expected
            $table->decimal('required_cgpa', 3, 2); // Assuming 0.00 to 4.00 or similar
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('booth_job_openings');
    }
};
