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
            $table->decimal('latitude', 10, 7)->nullable()->after('location');
            $table->decimal('longitude', 10, 7)->nullable()->after('latitude');
            $table->string('formatted_address')->nullable()->after('longitude');
            $table->text('location_query')->nullable()->after('formatted_address');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('job_fairs', function (Blueprint $table) {
            if (Schema::hasColumn('job_fairs', 'location_query')) {
                 $table->dropColumn('location_query');
            }
            if (Schema::hasColumn('job_fairs', 'formatted_address')) {
                 $table->dropColumn('formatted_address');
            }
            if (Schema::hasColumn('job_fairs', 'longitude')) {
                 $table->dropColumn('longitude');
            }
            if (Schema::hasColumn('job_fairs', 'latitude')) {
                 $table->dropColumn('latitude');
            }
        });
    }
};
