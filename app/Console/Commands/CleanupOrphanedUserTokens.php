<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Laravel\Sanctum\PersonalAccessToken;
use App\Models\User;

class CleanupOrphanedUserTokens extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'user:cleanup-tokens';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Cleanup orphaned user tokens that might still be active but have no valid user';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $this->info('Starting cleanup of orphaned user tokens...');

        // Find tokens with non-existent users
        $orphanedTokens = PersonalAccessToken::whereNotIn('tokenable_id', function($query) {
            $query->select('id')->from('users');
        })->where('tokenable_type', 'App\\Models\\User');

        $count = $orphanedTokens->count();
        $this->info("Found {$count} orphaned tokens");

        if ($count > 0) {
            $orphanedTokens->delete();
            $this->info("Successfully deleted {$count} orphaned tokens");
        }

        $this->info('Completed token cleanup');

        return Command::SUCCESS;
    }
} 