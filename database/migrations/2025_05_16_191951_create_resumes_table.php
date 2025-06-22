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
        Schema::create('resumes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->string('original_filename');
            $table->string('filepath'); // Path to the stored resume file
            $table->string('primary_field')->nullable(); // e.g., Computer Science, Medical, Finance
            $table->json('parsed_data')->nullable(); // To store the full JSON output from the Python parser
            $table->text('raw_text')->nullable(); // To store the extracted raw text
            $table->json('analysis_data')->nullable(); // To store job recommendations and other analysis results
            $table->string('parsing_status')->default('pending'); // pending, processing, completed, failed
            $table->text('parser_error_message')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('resumes');
    }
};
