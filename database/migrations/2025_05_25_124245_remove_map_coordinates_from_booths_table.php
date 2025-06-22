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
        Schema::table('booths', function (Blueprint $table) {
            if (Schema::hasColumn('booths', 'map_coordinates')) {
                $table->dropColumn('map_coordinates');
            }
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('booths', function (Blueprint $table) {
            $table->json('map_coordinates')->nullable()->after('booth_number_on_map'); // Or whatever its original definition was
        });
    }
};
