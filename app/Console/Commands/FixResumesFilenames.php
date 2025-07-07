<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Resume;
use Illuminate\Support\Facades\Log;

class FixResumesFilenames extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'app:fix-resumes-filenames';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Fix resume filenames to display the original filename';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $this->info('Starting to fix resume filenames...');
        
        // Get all resumes
        $resumes = Resume::all();
        $count = 0;
        
        foreach ($resumes as $resume) {
            try {
                // Get the current filename
                $filename = $resume->filename;
                
                // If filename is timestamp based, update it to something more user-friendly
                if (preg_match('/^resume_(\d+)\.pdf$/', $filename)) {
                    // Generate a better user-friendly name if original not available
                    $betterName = 'resume_' . date('Y-m-d_H-i-s', $resume->created_at->timestamp) . '.pdf';
                    
                    // Update the file_name to be more user-friendly
                    $resume->file_name = $betterName;
                    $resume->save();
                    
                    $this->info("Updated resume ID {$resume->id}: {$betterName}");
                    $count++;
                }
            } catch (\Exception $e) {
                $this->error("Error updating resume ID {$resume->id}: {$e->getMessage()}");
                Log::error("Error in FixResumesFilenames for resume ID {$resume->id}: {$e->getMessage()}");
            }
        }
        
        $this->info("Completed! Updated {$count} resume filenames.");
    }
}
