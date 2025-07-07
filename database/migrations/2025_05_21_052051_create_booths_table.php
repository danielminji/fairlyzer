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
        Schema::create('booths', function (Blueprint $table) {
            $table->id();
            $table->foreignId('job_fair_id')->constrained('job_fairs')->onDelete('cascade');
            $table->string('company_name');
            $table->string('booth_number_on_map')->nullable(); // Can be alphanumeric like 'A21' or '103'
            $table->json('map_coordinates')->nullable(); // For storing booth location/bounding box on the map image
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('booths');
    }
};
