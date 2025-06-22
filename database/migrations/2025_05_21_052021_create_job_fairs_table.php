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
        Schema::create('job_fairs', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organizer_id')->constrained('users')->onDelete('cascade'); // Assuming 'users' table and organizers are users
            $table->string('title');
            $table->text('description')->nullable();
            $table->date('date')->nullable();
            $table->text('location')->nullable();
            $table->string('map_image_path')->nullable();
            $table->string('status')->default('draft'); // e.g., draft, active, archived
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('job_fairs');
    }
};
