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

class UiTMJasinJobFairSeeder extends Seeder
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
                'name' => 'UiTM Jasin Event Team',
                'email' => 'organizer_uitmjasin@example.com',
                'role' => 'organizer',
                'is_active' => true,
                'company_name' => 'UiTM Jasin Career Center',
            ]);
        }

        // 2. Create the Job Fair
        $mapImageFileName = 'jobfairmap.png';
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
            'title' => 'UiTM Jasin Job Fair 2025',
            'description' => 'The premier career fair connecting UiTM Jasin students and alumni with leading employers across various industries. Discover exciting job opportunities, internships, and network with professionals.',
            'start_datetime' => now()->addMonths(1)->setHour(9)->setMinute(0)->setSecond(0),
            'end_datetime' => now()->addMonths(1)->addDays(1)->setHour(17)->setMinute(0)->setSecond(0),
            'location_query' => 'Universiti Teknologi MARA (UiTM) Cawangan Melaka Kampus Jasin, 77300 Merlimau, Melaka, Malaysia', // Specific address for UiTM Jasin Campus
            'latitude' => 2.2279554003677084, // User-provided latitude
            'longitude' => 102.45680294373673, // User-provided longitude
            'formatted_address' => 'Universiti Teknologi MARA (UiTM) Cawangan Melaka Kampus Jasin, 77300 Merlimau, Melaka, Malaysia', // Expected formatted address for the query/coordinates
            'map_image_path' => Storage::disk('public')->exists($mapPathInPublicStorage) ? $mapPathInPublicStorage : null,
            'status' => 'active',
            // The 'location' field is being phased out but kept for any legacy seeder parts.
            // For new functionality, location_query, latitude, longitude, and formatted_address are primary.
            'location' => 'Universiti Teknologi MARA (UiTM) Cawangan Melaka Kampus Jasin, 77300 Merlimau, Melaka, Malaysia',
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

        // --- Booth 1-3: Computer Science (Aiman Faris) ---
        $booth1 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Tech Solutions Inc.', 'booth_number_on_map' => '1']);
        $createOpening($booth1->id, $organizer->id, [
            'job_title' => 'Junior Software Engineer (Backend)', 'primary_field' => 'Computer Science',
            'description' => 'Develop and maintain server-side logic, APIs, and database schemas for our core products. Collaborate with frontend developers and product managers.',
            'required_skills_general' => ['Python', 'Django', 'REST APIs', 'PostgreSQL', 'Git', 'Docker Basics'],
            'required_skills_soft' => ['Problem-solving', 'Teamwork', 'Code documentation', 'Attention to Detail'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth1->id, $organizer->id, [
            'job_title' => 'Graduate Developer Program (Java)', 'primary_field' => 'Computer Science',
            'description' => 'Join our intensive graduate program to become a proficient Java developer. Work on real-world projects involving Spring Boot and microservices.',
            'required_skills_general' => ['Java', 'Spring Boot', 'Microservices Concepts', 'Maven/Gradle', 'SQL Basics'],
            'required_skills_soft' => ['Continuous learning', 'Adaptability', 'Collaboration', 'Strong work ethic'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);

        $booth2 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'AI Innovations Ltd.', 'booth_number_on_map' => '2']);
        $createOpening($booth2->id, $organizer->id, [
            'job_title' => 'AI Developer Intern', 'primary_field' => 'Computer Science',
            'description' => 'Contribute to cutting-edge AI projects. Assist in developing and training machine learning models, focusing on NLP and computer vision.',
            'required_skills_general' => ['Python', 'TensorFlow', 'PyTorch', 'NLP Libraries (NLTK, spaCy)', 'Machine Learning Algorithms'],
            'required_skills_soft' => ['Analytical thinking', 'Innovation', 'Research skills', 'Proactive'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.4,
        ], $faker);
        $createOpening($booth2->id, $organizer->id, [
            'job_title' => 'Data Science Trainee', 'primary_field' => 'Computer Science',
            'description' => 'Analyze large datasets to extract meaningful insights. Develop predictive models and create data visualizations to support business decisions.',
            'required_skills_general' => ['Python', 'R', 'SQL', 'Pandas', 'NumPy', 'Scikit-learn', 'Data Visualization Tools (e.g., Matplotlib, Seaborn)'],
            'required_skills_soft' => ['Data interpretation', 'Attention to detail', 'Effective communication', 'Curiosity'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);

        $booth3 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Web Wizards Co.', 'booth_number_on_map' => '3']);
        $createOpening($booth3->id, $organizer->id, [
            'job_title' => 'Full-Stack Web Developer (Junior)', 'primary_field' => 'Computer Science',
            'description' => 'Work on both frontend and backend development of dynamic web applications. Utilize modern frameworks and best practices in an agile environment.',
            'required_skills_general' => ['PHP', 'Laravel', 'JavaScript', 'Vue.js/React', 'MySQL', 'Git', 'HTML5', 'CSS3'],
            'required_skills_soft' => ['Good communication', 'Adaptability', 'Debugging skills', 'Time management', 'Team player'],
            'required_experience_years' => 0, 'required_experience_entries' => 1, 'required_cgpa' => 3.1,
        ], $faker);
         $createOpening($booth3->id, $organizer->id, [
            'job_title' => 'Frontend Developer Intern (React)', 'primary_field' => 'Computer Science',
            'description' => 'Focus on building responsive and interactive user interfaces using React. Collaborate with UI/UX designers and backend developers.',
            'required_skills_general' => ['HTML5', 'CSS3', 'JavaScript (ES6+)', 'React', 'Redux/Context API', 'Responsive Design Principles', 'Git'],
            'required_skills_soft' => ['Creativity', 'User-centric thinking', 'Team collaboration', 'Pixel-perfect attention to detail'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        // --- Booth 4-6: Finance (Daniel Rahman) ---
        $booth4 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Capital Investments Group', 'booth_number_on_map' => '4']);
        $createOpening($booth4->id, $organizer->id, [
            'job_title' => 'Finance Analyst Intern', 'primary_field' => 'Finance',
            'description' => 'Support senior analysts in financial modeling, market research, and preparation of investment reports. Gain exposure to various asset classes.',
            'required_skills_general' => ['Excel (Advanced)', 'Financial Modeling (DCF, LBO basics)', 'PowerPoint', 'Bloomberg Terminal (basic knowledge preferred)', 'Financial Statement Analysis'],
            'required_skills_soft' => ['Strong attention to detail', 'Excellent analytical skills', 'Clear report writing', 'Proactive learner'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);
        $createOpening($booth4->id, $organizer->id, [
            'job_title' => 'Investment Research Trainee', 'primary_field' => 'Finance',
            'description' => 'Conduct in-depth research on companies and industries. Assist in generating investment ideas and present findings to the team.',
            'required_skills_general' => ['Data Analysis', 'Market Research Techniques', 'Excel', 'Statistics (Basic)', 'Valuation Methodologies'],
            'required_skills_soft' => ['Deep curiosity', 'Critical thinking ability', 'Effective presentation skills', 'Self-motivated'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.4,
        ], $faker);

        $booth5 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Global Audit Partners LLP', 'booth_number_on_map' => '5']);
        $createOpening($booth5->id, $organizer->id, [
            'job_title' => 'Junior Auditor (Graduate Scheme)', 'primary_field' => 'Finance',
            'description' => 'Participate in audit engagements for diverse clients. Perform audit procedures, document findings, and learn from experienced auditors.',
            'required_skills_general' => ['Accounting Principles (IFRS/GAAP)', 'Audit Procedures', 'MS Excel', 'QuickBooks/Xero (familiarity)', 'Internal Controls Concepts'],
            'required_skills_soft' => ['High ethical standards', 'Meticulousness', 'Good interpersonal skills', 'Team-oriented'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);
        $createOpening($booth5->id, $organizer->id, [
            'job_title' => 'Forensic Accounting Intern', 'primary_field' => 'Finance',
            'description' => 'Assist in forensic investigations, analyze financial records for discrepancies, and support litigation support projects.',
            'required_skills_general' => ['Investigative Techniques', 'Data Analysis (Excel, IDEA preferred)', 'Financial Reporting Standards', 'Report Writing (clear & concise)'],
            'required_skills_soft' => ['Professional skepticism', 'Advanced problem-solving', 'Utmost discretion', 'Resilience'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.5,
        ], $faker);

        $booth6 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'FinTech Innovators Hub', 'booth_number_on_map' => '6']);
        $createOpening($booth6->id, $organizer->id, [
            'job_title' => 'Business Intelligence Trainee (Finance Focus)', 'primary_field' => 'Finance',
            'description' => 'Develop dashboards and reports using BI tools to provide actionable insights for financial products. Work with large datasets and data pipelines.',
            'required_skills_general' => ['Power BI', 'SQL', 'Tableau', 'Data Warehousing Concepts', 'Excel (Pivot Tables, Power Query)', 'ETL Basics'],
            'required_skills_soft' => ['Strong data visualization skills', 'Storytelling with data', 'Good business acumen', 'Collaborative'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.1,
        ], $faker);
        $createOpening($booth6->id, $organizer->id, [
            'job_title' => 'Quantitative Analyst Intern (Algorithmic Trading)', 'primary_field' => 'Finance',
            'description' => 'Research and develop quantitative models for trading strategies. Backtest models and assist in their implementation.',
            'required_skills_general' => ['Python (Pandas, NumPy, SciPy)', 'Statistical Modeling', 'R', 'Financial Derivatives (basic understanding)', 'Time Series Analysis'],
            'required_skills_soft' => ['Strong mathematical aptitude', 'Advanced logical reasoning', 'High precision', 'Ability to work under pressure'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.6,
        ], $faker);

        // --- Booth 7-9: Medical (Nur Izzati Hassan) ---
        $booth7 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'City General Hospital & Trauma Center', 'booth_number_on_map' => '7']);
        $createOpening($booth7->id, $organizer->id, [
            'job_title' => 'Medical Intern (Clinical Support & Rotations)', 'primary_field' => 'Medical',
            'description' => 'Gain hands-on experience in various hospital departments. Assist physicians and nurses with patient care, record keeping, and procedures under supervision.',
            'required_skills_general' => ['Patient Care Basics', 'EMR Systems (Cerner/Epic familiarity a plus)', 'Vital Signs Monitoring', 'Medical Terminology', 'Basic Life Support (BLS) certified'],
            'required_skills_soft' => ['Empathy', 'Effective communication with patients and staff', 'Teamwork in healthcare settings', 'Resilience'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.5,
        ], $faker);
        $createOpening($booth7->id, $organizer->id, [
            'job_title' => 'Hospital Administration Trainee', 'primary_field' => 'Medical',
            'description' => 'Support hospital operations, assist with patient scheduling, records management, and learn about healthcare administration processes.',
            'required_skills_general' => ['Healthcare Management Basics', 'MS Office Suite (Word, Excel, Outlook)', 'Hospital Information Systems (Basic User)', 'Medical Billing Codes (Intro)'],
            'required_skills_soft' => ['Excellent organization skills', 'Interdepartmental coordination', 'Problem-solving abilities', 'Professional demeanor'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);

        $booth8 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'PharmaResearch Global Solutions', 'booth_number_on_map' => '8']);
        $createOpening($booth8->id, $organizer->id, [
            'job_title' => 'Clinical Research Assistant (Entry Level)', 'primary_field' => 'Medical',
            'description' => 'Support clinical trial operations, including data collection, patient interaction (under supervision), and maintenance of trial documentation according to GCP.',
            'required_skills_general' => ['Data Collection & Entry', 'Good Clinical Practice (GCP) awareness', 'Case Report Forms (CRF) completion', 'Microsoft Excel', 'Clinical Trial Terminology'],
            'required_skills_soft' => ['Meticulous attention to detail', 'Strong organizational skills', 'Maintaining confidentiality', 'Team collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.4,
        ], $faker);
        $createOpening($booth8->id, $organizer->id, [
            'job_title' => 'Pharmacovigilance Intern (Drug Safety)', 'primary_field' => 'Medical',
            'description' => 'Assist in monitoring and reporting adverse drug reactions. Learn about drug safety databases and regulatory reporting requirements.',
            'required_skills_general' => ['Adverse Event Reporting Procedures', 'Medical Databases (e.g., Argus, ARISg - familiarity)', 'Regulatory Guidelines (FDA, EMA)', 'Medical Literature Review'],
            'required_skills_soft' => ['Strong analytical skills', 'High accuracy in data handling', 'Clear report writing', 'Ethical judgment'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.6,
        ], $faker);

        $booth9 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Wellness Tech Solutions Ltd.', 'booth_number_on_map' => '9']);
        $createOpening($booth9->id, $organizer->id, [
            'job_title' => 'Healthcare Project Coordinator (Intern)', 'primary_field' => 'Medical',
            'description' => 'Assist in planning and executing projects related to healthcare technology. Coordinate with development teams, clinicians, and stakeholders.',
            'required_skills_general' => ['Project Management Basics (Agile/Scrum awareness)', 'Figma (for UI/UX mockups review)', 'MS Project (or similar tools like Asana, Jira)', 'Healthcare IT Concepts'],
            'required_skills_soft' => ['Excellent teamwork skills', 'Leadership potential', 'Effective communication with technical & non-technical teams', 'Proactive problem-solver'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);
        $createOpening($booth9->id, $organizer->id, [
            'job_title' => 'Medical Scribe (Remote Part-Time)', 'primary_field' => 'Medical',
            'description' => 'Accurately document patient encounters in real-time as dictated by physicians using EHR/EMR systems. Ensure completeness and accuracy of medical records.',
            'required_skills_general' => ['Strong Medical Terminology', 'Typing speed (65+ WPM with accuracy)', 'EHR/EMR Software proficiency (e.g., Epic, Cerner, AthenaHealth)', 'HIPAA Compliance'],
            'required_skills_soft' => ['Exceptional active listening skills', 'High accuracy and attention to detail', 'Excellent time management', 'Ability to work independently'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        
        // --- Booth 10: Engineering & Manufacturing ---
        $booth10 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Precision Engineering Works Sdn Bhd', 'booth_number_on_map' => '10']);
        $createOpening($booth10->id, $organizer->id, [
            'job_title' => 'Mechanical Design Intern', 'primary_field' => 'Engineering', 
            'description' => 'Assist senior engineers in designing and developing mechanical parts and assemblies using CAD software. Participate in prototyping and testing.',
            'required_skills_general' => ['AutoCAD', 'SolidWorks', 'GD&T Basics', 'Finite Element Analysis (FEA) basics', 'Material Science (Intro)'],
            'required_skills_soft' => ['Detail-oriented', 'Strong problem-solving skills', 'Creativity in design', 'Team collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth10->id, $organizer->id, [
            'job_title' => 'Production Trainee (Manufacturing)', 'primary_field' => 'Engineering',
            'description' => 'Learn all aspects of the manufacturing production floor, from machine operation (under supervision) to quality control and lean manufacturing principles.',
            'required_skills_general' => ['Lean Manufacturing Basics', 'Quality Control Introduction', 'Reading Technical Drawings', 'Safety Procedures (OSHA awareness)'],
            'required_skills_soft' => ['Process-oriented thinking', 'Team player', 'Adaptability to shift work', 'Willingness to learn'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);

        // Placeholder for booths 11-30 to be added in next interactions
        $this->command->info('UiTM Jasin Job Fair 2025 seeded with Batch 1 (Booths 1-10) and job openings.');

        // --- Batch 2: Booths 11-20 ---

        // --- Booths 11-13: Computer Science (Continued) ---
        $booth11 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'MobileFirst Devs', 'booth_number_on_map' => '11']);
        $createOpening($booth11->id, $organizer->id, [
            'job_title' => 'Junior Mobile App Developer (iOS)', 'primary_field' => 'Computer Science',
            'description' => 'Develop and maintain native iOS applications using Swift. Collaborate with UI/UX designers to create a seamless user experience.',
            'required_skills_general' => ['Swift', 'Xcode', 'iOS SDK', 'UIKit/SwiftUI', 'REST APIs', 'Git'],
            'required_skills_soft' => ['Problem-solving', 'Attention to UI/UX details', 'Teamwork', 'Adaptability'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.1,
        ], $faker);
        $createOpening($booth11->id, $organizer->id, [
            'job_title' => 'Android Developer Intern', 'primary_field' => 'Computer Science',
            'description' => 'Learn to build and maintain Android applications using Kotlin/Java. Work on exciting features for our flagship apps.',
            'required_skills_general' => ['Kotlin', 'Java', 'Android Studio', 'Android SDK', 'XML Layouts', 'Git'],
            'required_skills_soft' => ['Eagerness to learn', 'Debugging skills', 'Collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth12 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'DevOps Engineers Inc.', 'booth_number_on_map' => '12']);
        $createOpening($booth12->id, $organizer->id, [
            'job_title' => 'Junior DevOps Engineer', 'primary_field' => 'Computer Science',
            'description' => 'Assist in managing CI/CD pipelines, cloud infrastructure (AWS/Azure), and implement automation scripts. Monitor system performance and troubleshoot issues.',
            'required_skills_general' => ['Linux Administration', 'Shell Scripting (Bash)', 'Docker', 'Kubernetes (basic)', 'AWS/Azure (basic)', 'Git', 'Jenkins/GitLab CI (familiarity)'],
            'required_skills_soft' => ['Problem-solving', 'Automation mindset', 'Communication', 'Collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 1, 'required_cgpa' => 3.2,
        ], $faker);
        $createOpening($booth12->id, $organizer->id, [
            'job_title' => 'Cloud Support Intern', 'primary_field' => 'Computer Science',
            'description' => 'Provide support for cloud-based services, assist with user account management, and learn about cloud security best practices.',
            'required_skills_general' => ['Cloud Computing Concepts (AWS, Azure, GCP)', 'Networking Basics', 'Operating Systems (Windows, Linux)', 'Customer Service Skills'],
            'required_skills_soft' => ['Troubleshooting', 'Patience', 'Clear communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.9,
        ], $faker);

        $booth13 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'QualityAssure Tech', 'booth_number_on_map' => '13']);
        $createOpening($booth13->id, $organizer->id, [
            'job_title' => 'Software Quality Assurance Intern', 'primary_field' => 'Computer Science',
            'description' => 'Perform manual and automated testing of web and mobile applications. Write test cases, report bugs, and verify fixes.',
            'required_skills_general' => ['Software Testing Life Cycle (STLC)', 'Test Case Design', 'Bug Tracking Tools (Jira)', 'Selenium/Appium (Basic)', 'SQL (for data verification)'],
            'required_skills_soft' => ['Attention to detail', 'Analytical skills', 'Systematic approach', 'Good communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth13->id, $organizer->id, [
            'job_title' => 'Automation Test Developer (Trainee)', 'primary_field' => 'Computer Science',
            'description' => 'Learn to develop and maintain automated test scripts using Python and Selenium. Contribute to our test automation framework.',
            'required_skills_general' => ['Python (Basic scripting)', 'Selenium WebDriver', 'TestNG/PyTest (familiarity)', 'Web Technologies (HTML, CSS, JavaScript)', 'Git'],
            'required_skills_soft' => ['Logical thinking', 'Problem-solving', 'Persistence'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);

        // --- Booths 14-16: Finance (Continued) ---
        $booth14 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'CorporateFinance Advisors', 'booth_number_on_map' => '14']);
        $createOpening($booth14->id, $organizer->id, [
            'job_title' => 'Corporate Finance Analyst Intern', 'primary_field' => 'Finance',
            'description' => 'Assist in due diligence, company valuation, and preparation of pitch books and financial models for M&A transactions.',
            'required_skills_general' => ['Financial Modeling (Advanced Excel)', 'Valuation Techniques (DCF, Comps)', 'PowerPoint', 'Capital IQ/FactSet (familiarity)', 'Accounting Principles'],
            'required_skills_soft' => ['Analytical rigor', 'Attention to detail', 'Presentation skills', 'Ability to work under pressure'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.5,
        ], $faker);
        $createOpening($booth14->id, $organizer->id, [
            'job_title' => 'Mergers & Acquisitions Trainee', 'primary_field' => 'Finance',
            'description' => 'Support the M&A team with market research, target identification, and financial analysis. Gain exposure to the full deal lifecycle.',
            'required_skills_general' => ['Financial Statement Analysis', 'Industry Research', 'Excel', 'Database skills (PitchBook, etc.)'],
            'required_skills_soft' => ['Proactive', 'Strong work ethic', 'Discretion', 'Team player'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.4,
        ], $faker);

        $booth15 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'RiskReady Consultants', 'booth_number_on_map' => '15']);
        $createOpening($booth15->id, $organizer->id, [
            'job_title' => 'Financial Risk Management Intern', 'primary_field' => 'Finance',
            'description' => 'Assist in developing risk models, analyzing market and credit risk, and preparing risk reports for financial clients.',
            'required_skills_general' => ['Quantitative Analysis', 'Statistics (R or Python)', 'Excel (VBA a plus)', 'Financial Regulations (Basel Accords - awareness)', 'Risk Metrics (VaR, Stress Testing)'],
            'required_skills_soft' => ['Analytical mind', 'Problem-solving', 'Attention to detail', 'Report writing'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);
        $createOpening($booth15->id, $organizer->id, [
            'job_title' => 'Compliance Trainee (Financial Services)', 'primary_field' => 'Finance',
            'description' => 'Learn about financial regulations and assist in compliance testing, policy updates, and regulatory filings.',
            'required_skills_general' => ['Legal/Regulatory Research', 'MS Office', 'Understanding of AML/KYC an advantage'],
            'required_skills_soft' => ['Integrity', 'Meticulous', 'Good communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth16 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'WealthWise Planners', 'booth_number_on_map' => '16']);
        $createOpening($booth16->id, $organizer->id, [
            'job_title' => 'Junior Financial Planner Assistant', 'primary_field' => 'Finance',
            'description' => 'Support financial planners with client onboarding, data gathering, preparing financial plans, and client communication.',
            'required_skills_general' => ['Financial Planning Software (e.g., eMoney, NaviPlan - familiarity)', 'MS Excel', 'Investment Products Knowledge (Basic)', 'Retirement Planning Concepts'],
            'required_skills_soft' => ['Excellent interpersonal skills', 'Client-focused', 'Trustworthy', 'Organized'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth16->id, $organizer->id, [
            'job_title' => 'Paraplanner Trainee', 'primary_field' => 'Finance',
            'description' => 'Assist in research, analysis, and preparation of Statement of Advice documents. Ensure compliance and accuracy in financial plans.',
            'required_skills_general' => ['Financial Product Research', 'Report Writing (SoA)', 'Taxation Basics', 'Superannuation Knowledge'],
            'required_skills_soft' => ['Detail-oriented', 'Technical proficiency', 'Ethical'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);

        // --- Booths 17-20: Medical (Focus) ---
        $booth17 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Community Health Clinics Network', 'booth_number_on_map' => '17']);
        $createOpening($booth17->id, $organizer->id, [
            'job_title' => 'Clinic Operations Assistant (Intern)', 'primary_field' => 'Medical',
            'description' => 'Support daily clinic operations, patient registration, appointment scheduling, managing medical supplies, and ensuring smooth patient flow.',
            'required_skills_general' => ['Patient Administration Systems', 'MS Office Suite', 'Medical Inventory Management (Basic)', 'Customer Service in Healthcare', 'HIPAA Awareness'],
            'required_skills_soft' => ['Compassion', 'Efficiency', 'Problem-solving', 'Multitasking'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);
        $createOpening($booth17->id, $organizer->id, [
            'job_title' => 'Health Education Trainee', 'primary_field' => 'Medical',
            'description' => 'Assist in developing and delivering health education programs for the community. Create informational materials and support outreach events.',
            'required_skills_general' => ['Public Health Principles', 'Presentation Skills', 'Content Creation (Brochures, Slides)', 'Community Engagement Strategies'],
            'required_skills_soft' => ['Communication (clear & engaging)', 'Cultural sensitivity', 'Passion for health promotion'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth18 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'MediTech Devices Ltd.', 'booth_number_on_map' => '18']);
        $createOpening($booth18->id, $organizer->id, [
            'job_title' => 'Biomedical Engineering Intern', 'primary_field' => 'Medical',
            'description' => 'Assist in the design, development, and testing of medical devices. Work with R&D team on prototypes and documentation.',
            'required_skills_general' => ['CAD Software (SolidWorks, AutoCAD)', 'Medical Device Regulations (ISO 13485 awareness)', 'Prototyping Skills', 'Electronics/Mechanics Basics'],
            'required_skills_soft' => ['Innovative thinking', 'Analytical skills', 'Attention to detail', 'Team collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);
        $createOpening($booth18->id, $organizer->id, [
            'job_title' => 'Regulatory Affairs Trainee (Medical Devices)', 'primary_field' => 'Medical',
            'description' => 'Learn about regulatory submission processes for medical devices. Assist in preparing documentation and ensuring compliance with FDA/CE mark requirements.',
            'required_skills_general' => ['Technical Writing', 'Understanding of Regulatory Standards', 'Quality Management Systems (QMS) Intro'],
            'required_skills_soft' => ['Meticulous record-keeping', 'Research skills', 'Organizational skills'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.1,
        ], $faker);

        $booth19 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Allied Health Professionals Group', 'booth_number_on_map' => '19']);
        $createOpening($booth19->id, $organizer->id, [
            'job_title' => 'Physical Therapy Aide (Trainee)', 'primary_field' => 'Medical',
            'description' => 'Assist physical therapists with patient exercises, equipment setup, and maintaining a clean and organized therapy environment. Observe and learn treatment techniques.',
            'required_skills_general' => ['Anatomy & Physiology Basics', 'Patient Handling Techniques', 'Exercise Principles', 'CPR/First Aid Certified'],
            'required_skills_soft' => ['Supportive', 'Encouraging', 'Good communication', 'Physical stamina'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.7,
        ], $faker);
        $createOpening($booth19->id, $organizer->id, [
            'job_title' => 'Occupational Therapy Assistant Intern', 'primary_field' => 'Medical',
            'description' => 'Support occupational therapists in implementing treatment plans for patients with various needs. Assist with activities of daily living (ADL) training.',
            'required_skills_general' => ['Understanding of OT Principles', 'Adaptive Equipment Knowledge (Basic)', 'Patient Progress Documentation'],
            'required_skills_soft' => ['Patience', 'Creativity in therapy', 'Empathetic'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.9,
        ], $faker);

        $booth20 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'TeleHealth Connect Services', 'booth_number_on_map' => '20']);
        $createOpening($booth20->id, $organizer->id, [
            'job_title' => 'Telehealth Support Specialist (Entry)', 'primary_field' => 'Medical',
            'description' => 'Assist patients and healthcare providers with using telehealth platforms, troubleshoot technical issues, and ensure smooth virtual consultations.',
            'required_skills_general' => ['Video Conferencing Software (Zoom, MS Teams)', 'Customer Service via Phone/Chat', 'Basic IT Troubleshooting', 'EHR/EMR (for appointment integration)'],
            'required_skills_soft' => ['Excellent communication', 'Problem-solving under pressure', 'Patience with technology users', 'Tech-savvy'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);
        $createOpening($booth20->id, $organizer->id, [
            'job_title' => 'Patient Data Coordinator (Telehealth)', 'primary_field' => 'Medical',
            'description' => 'Manage and organize patient data collected through telehealth platforms. Ensure data accuracy, privacy, and assist in generating reports.',
            'required_skills_general' => ['Data Entry (High Accuracy)', 'MS Excel/Google Sheets', 'HIPAA Regulations', 'Database Management Basics'],
            'required_skills_soft' => ['Organizational skills', 'Attention to detail', 'Confidentiality', 'Data integrity focus'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        // Placeholder for booths 21-30 to be added in the next interaction
        $this->command->info('UiTM Jasin Job Fair 2025 seeded with Batch 2 (Booths 11-20) and job openings.');

        // --- Batch 3: Booths 21-30 ---

        // --- Booths 21-22: Computer Science (Completing CS quota) ---
        $booth21 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'CyberGuard Solutions', 'booth_number_on_map' => '21']);
        $createOpening($booth21->id, $organizer->id, [
            'job_title' => 'Junior Cybersecurity Analyst', 'primary_field' => 'Computer Science',
            'description' => 'Monitor security alerts, investigate incidents, and assist in vulnerability assessments. Learn about SIEM tools and threat hunting techniques.',
            'required_skills_general' => ['Networking Fundamentals', 'Operating Systems Security (Windows, Linux)', 'SIEM tools (basic understanding, e.g., Splunk, ELK)', 'Vulnerability Scanning tools', 'Security Concepts (Firewalls, IDS/IPS)'],
            'required_skills_soft' => ['Analytical thinking', 'Problem-solving', 'Attention to detail', 'Ethical conduct'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);
        $createOpening($booth21->id, $organizer->id, [
            'job_title' => 'IT Security Intern', 'primary_field' => 'Computer Science',
            'description' => 'Support the security team with policy documentation, security awareness training materials, and incident response preparation.',
            'required_skills_general' => ['MS Office Suite', 'Basic understanding of ISO 27001', 'Technical Writing'],
            'required_skills_soft' => ['Good communication', 'Organizational skills', 'Discretion'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth22 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'GameDev Creators Studio', 'booth_number_on_map' => '22']);
        $createOpening($booth22->id, $organizer->id, [
            'job_title' => 'Junior Game Developer (Unity)', 'primary_field' => 'Computer Science',
            'description' => 'Develop game mechanics, UI, and features using Unity and C#. Collaborate with artists and designers to bring game concepts to life.',
            'required_skills_general' => ['Unity Engine', 'C# Programming', 'Game Physics Basics', 'Version Control (Git)', 'Problem-solving in game logic'],
            'required_skills_soft' => ['Creativity', 'Teamwork', 'Passion for games', 'Adaptability'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth22->id, $organizer->id, [
            'job_title' => 'Game QA Tester Intern', 'primary_field' => 'Computer Science',
            'description' => 'Playtest games, identify bugs and glitches, document issues clearly, and work with developers to ensure a polished gaming experience.',
            'required_skills_general' => ['Attention to Detail', 'Bug Reporting Software (e.g., Jira, Mantis)', 'Understanding of Game Genres', 'Systematic Testing'],
            'required_skills_soft' => ['Patience', 'Thoroughness', 'Good written communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);

        // --- Booths 23-24: Finance (Completing Finance quota) ---
        $booth23 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Impact Investment Partners', 'booth_number_on_map' => '23']);
        $createOpening($booth23->id, $organizer->id, [
            'job_title' => 'ESG Analyst Intern (Finance)', 'primary_field' => 'Finance',
            'description' => 'Research and analyze companies based on Environmental, Social, and Governance (ESG) criteria. Prepare reports and support investment decision-making.',
            'required_skills_general' => ['ESG Frameworks (GRI, SASB - awareness)', 'Data Analysis', 'Report Writing', 'Sustainability Concepts', 'Financial Statement Analysis (basic)'],
            'required_skills_soft' => ['Ethical mindset', 'Research skills', 'Communication', 'Passion for sustainability'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.3,
        ], $faker);
        $createOpening($booth23->id, $organizer->id, [
            'job_title' => 'Social Impact Finance Trainee', 'primary_field' => 'Finance',
            'description' => 'Explore innovative financing models for social enterprises. Assist in due diligence and impact measurement.',
            'required_skills_general' => ['Financial Modeling (basic)', 'Impact Measurement Frameworks', 'Excel'],
            'required_skills_soft' => ['Passion for social change', 'Analytical skills', 'Adaptability'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.1,
        ], $faker);

        $booth24 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Prime Real Estate Investments REIT', 'booth_number_on_map' => '24']);
        $createOpening($booth24->id, $organizer->id, [
            'job_title' => 'Real Estate Analyst Intern', 'primary_field' => 'Finance',
            'description' => 'Support the acquisitions and asset management teams. Conduct market research, financial modeling for property valuations, and prepare investment memos.',
            'required_skills_general' => ['Excel (Advanced - Real Estate Modeling)', 'Argus Enterprise (familiarity a plus)', 'Market Research', 'Property Valuation Methods', 'PowerPoint'],
            'required_skills_soft' => ['Analytical skills', 'Attention to detail', 'Communication skills', 'Interest in real estate'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);
        $createOpening($booth24->id, $organizer->id, [
            'job_title' => 'Property Management Trainee', 'primary_field' => 'Real Estate',
            'description' => 'Learn the operations of property management, including tenant relations, lease administration, and vendor management.',
            'required_skills_general' => ['MS Office Suite', 'Customer Service Skills', 'Basic Accounting'],
            'required_skills_soft' => ['Organizational skills', 'Problem-solving', 'Interpersonal skills'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.9,
        ], $faker);
        
        // --- Booth 25: Medical (Completing Medical quota) ---
        $booth25 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'DentalCare Associates Group', 'booth_number_on_map' => '25']);
        $createOpening($booth25->id, $organizer->id, [
            'job_title' => 'Dental Assistant Trainee', 'primary_field' => 'Medical',
            'description' => 'Assist dentists during procedures, prepare treatment rooms, sterilize instruments, and help with patient record keeping. X-ray certification support provided.',
            'required_skills_general' => ['Dental Terminology', 'Infection Control Procedures', 'Chairside Assisting Basics', 'Patient Comfort Techniques'],
            'required_skills_soft' => ['Manual dexterity', 'Attention to detail', 'Caring attitude', 'Teamwork'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.7,
        ], $faker);
        $createOpening($booth25->id, $organizer->id, [
            'job_title' => 'Dental Clinic Receptionist/Admin', 'primary_field' => 'Medical', // Admin role in a medical setting
            'description' => 'Manage patient appointments, handle billing and insurance claims, maintain patient records, and provide excellent customer service.',
            'required_skills_general' => ['Dental Practice Management Software (e.g., Dentrix, OpenDental - familiarity)', 'MS Office', 'Medical Billing Basics', 'Phone Etiquette'],
            'required_skills_soft' => ['Excellent organizational skills', 'Customer service focus', 'Multitasking', 'Confidentiality'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);

        // --- Booths 26-30: General/Diverse Fields (Completing General/Diverse quota) ---
        $booth26 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'GreenTech Environmental Consultants', 'booth_number_on_map' => '26']);
        $createOpening($booth26->id, $organizer->id, [
            'job_title' => 'Environmental Science Intern', 'primary_field' => 'Environmental Science',
            'description' => 'Assist with environmental site assessments, data collection (soil, water sampling under supervision), report writing, and GIS mapping.',
            'required_skills_general' => ['Environmental Regulations (awareness)', 'Field Data Collection Techniques', 'GIS Software (ArcGIS/QGIS basics)', 'Technical Report Writing', 'MS Excel'],
            'required_skills_soft' => ['Analytical skills', 'Attention to detail', 'Fieldwork aptitude', 'Teamwork'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth26->id, $organizer->id, [
            'job_title' => 'Sustainability Project Assistant', 'primary_field' => 'Environmental Science',
            'description' => 'Support sustainability projects, research green initiatives, and assist with carbon footprint analysis and reporting.',
            'required_skills_general' => ['Sustainability Principles', 'Research Skills', 'Data Analysis (basic)', 'MS Office'],
            'required_skills_soft' => ['Passion for environment', 'Communication', 'Organizational skills'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth27 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Creative Media House', 'booth_number_on_map' => '27']);
        $createOpening($booth27->id, $organizer->id, [
            'job_title' => 'Digital Marketing Intern', 'primary_field' => 'Marketing',
            'description' => 'Assist with social media management, content creation (blog posts, social updates), SEO keyword research, and campaign performance analysis.',
            'required_skills_general' => ['Social Media Platforms (Facebook, Instagram, LinkedIn, Twitter)', 'Content Writing Basics', 'SEO Fundamentals (Keyword Research)', 'Google Analytics (Basic)', 'Canva/Adobe Spark (for simple graphics)'],
            'required_skills_soft' => ['Creativity', 'Good communication', 'Adaptability', 'Analytical thinking (basic)'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.9,
        ], $faker);
        $createOpening($booth27->id, $organizer->id, [
            'job_title' => 'Graphic Design Trainee', 'primary_field' => 'Design',
            'description' => 'Support the design team in creating visuals for digital campaigns, websites, and print materials. Learn about branding and visual communication.',
            'required_skills_general' => ['Adobe Creative Suite (Photoshop, Illustrator, InDesign - Basic)', 'Design Principles (Color, Typography, Layout)', 'Portfolio of Work (even student projects)'],
            'required_skills_soft' => ['Creativity', 'Attention to detail', 'Willingness to learn', 'Collaboration'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);

        $booth28 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Global Logistics Solutions', 'booth_number_on_map' => '28']);
        $createOpening($booth28->id, $organizer->id, [
            'job_title' => 'Logistics Coordinator Trainee', 'primary_field' => 'Logistics',
            'description' => 'Learn to coordinate shipments, track inventory, communicate with carriers and clients, and prepare shipping documentation.',
            'required_skills_general' => ['MS Excel', 'Supply Chain Basics', 'Geography Knowledge (helpful)', 'Communication Systems (Email, Phone)'],
            'required_skills_soft' => ['Organizational skills', 'Problem-solving', 'Attention to detail', 'Ability to work in a fast-paced environment'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);
        $createOpening($booth28->id, $organizer->id, [
            'job_title' => 'Supply Chain Analyst Intern', 'primary_field' => 'Logistics',
            'description' => 'Analyze supply chain data to identify inefficiencies, support process improvements, and assist with demand forecasting.',
            'required_skills_general' => ['Data Analysis (Excel, SQL basic)', 'Process Mapping', 'Inventory Management Concepts'],
            'required_skills_soft' => ['Analytical thinking', 'Problem-solving', 'Communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.1,
        ], $faker);

        $booth29 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Hospitality Group International', 'booth_number_on_map' => '29']);
        $createOpening($booth29->id, $organizer->id, [
            'job_title' => 'Hotel Operations Intern (Front Office)', 'primary_field' => 'Marketing',
            'description' => 'Gain experience in front desk operations, guest check-in/out, reservations, and concierge services. Provide excellent customer service to guests.',
            'required_skills_general' => ['Customer Service Excellence', 'Property Management Systems (PMS - Opera, Fidelio familiarity a plus)', 'Communication Skills (Multilingual a plus)', 'Problem Resolution'],
            'required_skills_soft' => ['Friendly and outgoing personality', 'Professional demeanor', 'Adaptability', 'Team player'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.7,
        ], $faker);
        $createOpening($booth29->id, $organizer->id, [
            'job_title' => 'Events & Banqueting Trainee', 'primary_field' => 'Marketing',
            'description' => 'Assist in planning and executing events, from corporate meetings to weddings. Support a_second_one_setup, client communication, and on-site coordination.',
            'required_skills_general' => ['Event Planning Basics', 'MS Office Suite', 'Vendor Coordination (basic)'],
            'required_skills_soft' => ['Organizational skills', 'Creativity', 'Customer focus', 'Ability to work under pressure'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 2.8,
        ], $faker);

        $booth30 = Booth::create(['job_fair_id' => $jobFair->id, 'company_name' => 'Urban Planners & Developers Co.', 'booth_number_on_map' => '30']);
        $createOpening($booth30->id, $organizer->id, [
            'job_title' => 'Urban Planning Assistant (Intern)', 'primary_field' => 'Urban Planning',
            'description' => 'Support senior planners with research, data analysis for urban development projects, GIS mapping, and preparation of planning documents.',
            'required_skills_general' => ['Urban Planning Principles', 'GIS Software (ArcGIS/QGIS)', 'Data Analysis (Excel, SPSS basic)', 'Community Engagement (awareness)', 'Report Writing'],
            'required_skills_soft' => ['Critical thinking', 'Interest in urban issues', 'Research skills', 'Communication'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.0,
        ], $faker);
        $createOpening($booth30->id, $organizer->id, [
            'job_title' => 'Architectural Design Intern', 'primary_field' => 'Architecture',
            'description' => 'Assist architects with design development, drafting (CAD/Revit), model making, and project documentation for urban and building projects.',
            'required_skills_general' => ['AutoCAD', 'Revit (or similar BIM software)', 'SketchUp', 'Adobe Creative Suite (Photoshop, Illustrator)', 'Architectural Design Principles', 'Portfolio required'],
            'required_skills_soft' => ['Creativity', 'Design sensibility', 'Attention to detail', 'Teamwork'],
            'required_experience_years' => 0, 'required_experience_entries' => 0, 'required_cgpa' => 3.2,
        ], $faker);

        $this->command->info('UiTM Jasin Job Fair 2025 seeded with Batch 3 (Booths 21-30) and job openings. All 30 booths are now seeded.');
    }
} 