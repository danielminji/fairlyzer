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
        Schema::table('job_fairs', function (Blueprint $table) {
            // Drop the old 'date' column if it exists
            if (Schema::hasColumn('job_fairs', 'date')) {
                $table->dropColumn('date');
            }

            // Add new datetime columns
            // Placing them after 'description' for logical order, can be adjusted
            if (!Schema::hasColumn('job_fairs', 'start_datetime')) {
                $table->dateTime('start_datetime')->after('description')->comment('Start date and time of the job fair');
            }
            if (!Schema::hasColumn('job_fairs', 'end_datetime')) {
                $table->dateTime('end_datetime')->after('start_datetime')->comment('End date and time of the job fair');
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('job_fairs', function (Blueprint $table) {
            // Drop the new datetime columns
            if (Schema::hasColumn('job_fairs', 'start_datetime')) {
                $table->dropColumn('start_datetime');
            }
            if (Schema::hasColumn('job_fairs', 'end_datetime')) {
                $table->dropColumn('end_datetime');
            }

            // Re-add the old 'date' column if it doesn't exist (for rollback safety)
            if (!Schema::hasColumn('job_fairs', 'date')) {
                $table->date('date')->nullable()->after('description');
            }
        });
    }
};
