<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use App\Models\JobFair;
use App\Models\Booth;
use App\Models\BoothJobOpening;
use Illuminate\Support\Facades\Storage;
use Faker\Factory as Faker;
// No Str import needed if we are explicit

class UiTMBandarRayaJobFairSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $faker = Faker::create();

        // 1. Find or Create an Organizer User
        $organizer = User::where('role', 'organizer')->where('is_active', true)->first();
        if (!$organizer) {
            $organizer = User::factory()->create([
                'name' => 'UiTM JBandarRaya Melaka Event Team',
                'email' => 'organizer_uitmBRM@example.com',
                'role' => 'organizer',
                'is_active' => true,
                'company_name' => 'UiTM BandarRaya Melaka Career Center',
            ]);
        }

        // 2. Create the Job Fair
        $mapImageFileName = 'jobfairmap2.png';
        $sourceMapPath = database_path('seeders/assets/job_fair_maps/' . $mapImageFileName);
        $mapPathInPublicStorage = 'job_fair_maps/' . $mapImageFileName; // Relative to public disk root (storage/app/public)

        // Ensure the target directory exists in storage/app/public/job_fair_maps
        if (!Storage::disk('public')->exists('job_fair_maps')) {
            Storage::disk('public')->makeDirectory('job_fair_maps');
        }

        // Copy the file from the new source to public storage if it exists at the source
        if (file_exists($sourceMapPath)) {
            // Check if file already exists in public storage to avoid re-copying unnecessarily,
            // or decide to overwrite if that's the desired behavior.
            // For simplicity, this will overwrite if source exists.
            Storage::disk('public')->put($mapPathInPublicStorage, file_get_contents($sourceMapPath));
            $this->command->info("Map image '$mapImageFileName' copied to public storage.");
        } else {
            $this->command->warn("Map image '$mapImageFileName' not found at '$sourceMapPath'. Job fair will be created without a map image or with a previously existing one if available in public storage.");
            // Decide if $mapPathInPublicStorage should be null or an empty string if source not found
            // For now, we'll still try to set it, relying on a pre-existing file or an issue.
        }

        $jobFair = JobFair::create([
            'organizer_id' => $organizer->id,
            'title' => 'UiTM BandarRaya Melaka Job Fair 2025',
            'description' => 'The premier career fair connecting UiTM BandarRaya Melaka students and alumni with leading employers across various industries. Discover exciting job opportunities, internships, and network with professionals.',
            'start_datetime' => now()->addMonths(2)->setHour(9)->setMinute(0)->setSecond(0),
            'end_datetime' => now()->addMonths(2)->addDays(1)->setHour(17)->setMinute(0)->setSecond(0),
            'location_query' => 'Universiti Teknologi MARA (UiTM), Cawangan Melaka Kampus Bandaraya Melaka, 110 Off Jalan Hang Tuah, 75350 Melaka, Malaysia', // Specific address for UiTM Jasin Campus
            'latitude' => 2.2054125924514274, // User-provided latitude
            'longitude' => 102.24651852883584, // User-provided longitude
            'formatted_address' => 'Universiti Teknologi MARA (UiTM), Cawangan Melaka Kampus Bandaraya Melaka, 110 Off Jalan Hang Tuah, 75350 Melaka, Malaysia', // Expected formatted address for the query/coordinates
            'map_image_path' => Storage::disk('public')->exists($mapPathInPublicStorage) ? $mapPathInPublicStorage : null,
            'status' => 'active',
            // The 'location' field is being phased out but kept for any legacy seeder parts.
            // For new functionality, location_query, latitude, longitude, and formatted_address are primary.
            'location' => 'Universiti Teknologi MARA (UiTM), Cawangan Melaka Kampus Bandaraya Melaka, 110 Off Jalan Hang Tuah, 75350 Melaka, Malaysia',
        ]);

        // --- Helper function to create job openings ---
        $createOpening = function ($boothId, $orgId, $data, $fakerInstance) {
            BoothJobOpening::create(array_merge([
                'booth_id' => $boothId,
                'organizer_id' => $orgId,
                // If description is not in $data, Faker will be used. Otherwise, $data description takes precedence.
                'description' => $data['description'] ?? $fakerInstance->bs() . '. ' . $fakerInstance->text(150),
            ], $data));
        };

        // --- Booth 1: Computer Science (Aiman Faris) ---
        $booth1 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Cybertech Solutions', 'booth_number_on_map' => '1']);
        $createOpening($booth1->id, $organizer->id, [
            'job_title' => 'Junior Developer', 'primary_field' => 'Computer Science',
            'description' => 'Develop responsive web components using Laravel and Streamlit for backend and AI features. Work on debugging and testing for client-side modules in Agile sprints.',
            'required_skills_general' => ['Python', 'PHP', 'JavaScript', 'Laravel', 'Git', 'Debugging'],
            'required_skills_soft' => ['Problem-solving', 'Debugging', 'Communication', 'Teamwork'],
            'required_experience_years' => 1, 'required_experience_entries' => 1, 'required_cgpa' => 3.2,
        ], $faker);
        $createOpening($booth1->id, $organizer->id, [
            'job_title' => 'Full-Stack Web Developer', 'primary_field' => 'Computer Science',
            'description' => 'Build web-based career fair systems integrating resume parsing and booth matching. Use Laravel, MySQL, and Streamlit for backend and AI features.',
            'required_skills_general' => ['PHP', 'Laravel', 'MySQL', 'Python', 'Streamlit', 'Git'],
            'required_skills_soft' => ['Problem-solving', 'Adaptability', 'Team collaboration', 'Time management'],
            'required_experience_years' => 0, 'required_experience_entries' => 1, 'required_cgpa' => 3.0,
        ], $faker);

        // --- Booth 2: Finance (Daniel Rahman) ---
        $booth2 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'CIMB Group', 'booth_number_on_map' => '2']);
        $createOpening($booth2->id, $organizer->id, [
            'job_title' => 'Finance Intern', 'primary_field' => 'Finance',
            'description' => 'Prepare month-end financial reports and conduct variance analysis. Assist in budgeting and forecasting processes using Excel and Power BI.',
            'required_skills_general' => ['Excel', 'Power BI', 'Financial Analysis', 'Budgeting', 'Forecasting'],
            'required_skills_soft' => ['Assertive', 'Time-management', 'Organization', 'Analytical Skills'],
            'required_experience_years' => 1, 'required_experience_entries' => 1, 'required_cgpa' => 3.7,
        ], $faker);
        $createOpening($booth2->id, $organizer->id, [
            'job_title' => 'Investment Portfolio Analyst', 'primary_field' => 'Finance',
            'description' => 'Create diversified investment portfolios based on risk-return profiles. Use Excel and Tableau for financial modelling and performance tracking.',
            'required_skills_general' => ['Excel', 'Tableau', 'Financial Modeling', 'Investment Analysis', 'Risk Management'],
            'required_skills_soft' => ['Analytical Skills', 'Attention to Detail', 'Decision Making', 'Communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 1, 'required_cgpa' => 3.5,
        ], $faker);

        // --- Booth 3: Medical (Nur Izzati Hassan) ---
        $booth3 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Hospital Serdang', 'booth_number_on_map' => '3']);
        $createOpening($booth3->id, $organizer->id, [
            'job_title' => 'Clinical Posting Student', 'primary_field' => 'Medical',
            'description' => 'Assist in daily ward rounds, patient monitoring, and emergency procedures. Gain hands-on experience in Surgery, Pediatrics, Internal Medicine.',
            'required_skills_general' => ['Venepuncture', 'Suturing', 'CPR', 'Patient Monitoring', 'Medical Documentation'],
            'required_skills_soft' => ['Empathy', 'Counselling', 'Leadership', 'Communication', 'Teamwork'],
            'required_experience_years' => 1, 'required_experience_entries' => 2, 'required_cgpa' => 3.9,
        ], $faker);
        $createOpening($booth3->id, $organizer->id, [
            'job_title' => 'Medical Intern', 'primary_field' => 'Medical',
            'description' => 'Participate in patient assessments and develop preliminary care plans under supervision. Engage with patients and families for empathetic support.',
            'required_skills_general' => ['Patient Assessment', 'Medical History Taking', 'Clinical Examination', 'EMR Systems', 'Medical Terminology'],
            'required_skills_soft' => ['Empathy', 'Communication', 'Problem Solving', 'Attention to Detail', 'Stress Management'],
            'required_experience_years' => 0, 'required_experience_entries' => 1, 'required_cgpa' => 3.5,
        ], $faker);

        $this->command->info('UiTM Bandaraya Melaka Job Fair 2025 seeded with 3 booths (Computer Science, Finance, Medical) and relevant job openings.');

    }
} 