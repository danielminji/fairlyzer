<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\JobRequirement;
use Illuminate\Support\Facades\DB; // Required for DB::table if not using Eloquent exclusively

class JobRequirementSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        JobRequirement::truncate(); // Clear the table before seeding

        $jobRequirements = [];

        // Computer Science Job Requirements (10 examples)
        $cs_jobs = [
            [
                'job_title' => 'Software Engineer',
                'description' => 'Develop and maintain web applications.',
                'required_skills_general' => json_encode(['PHP', 'Laravel', 'Vue.js', 'MySQL', 'Git']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Teamwork']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Data Scientist',
                'description' => 'Analyze large datasets to extract meaningful insights.',
                'required_skills_general' => json_encode(['Python', 'R', 'SQL', 'Machine Learning', 'Statistics']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'DevOps Engineer',
                'description' => 'Automate and streamline operations and processes.',
                'required_skills_general' => json_encode(['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Linux']),
                'required_skills_soft' => json_encode(['Collaboration', 'Adaptability']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Frontend Developer',
                'description' => 'Build responsive and interactive user interfaces.',
                'required_skills_general' => json_encode(['HTML', 'CSS', 'JavaScript', 'React', 'Angular']),
                'required_skills_soft' => json_encode(['Creativity', 'Attention to Detail']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Backend Developer',
                'description' => 'Design and implement server-side logic.',
                'required_skills_general' => json_encode(['Node.js', 'Python', 'Django', 'MongoDB', 'REST APIs']),
                'required_skills_soft' => json_encode(['Logical Thinking', 'Problem Solving']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Cybersecurity Analyst',
                'description' => 'Protect systems and networks from threats.',
                'required_skills_general' => json_encode(['Network Security', 'Penetration Testing', 'SIEM', 'Cryptography']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Ethical Hacking']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'AI/ML Engineer',
                'description' => 'Develop and deploy machine learning models.',
                'required_skills_general' => json_encode(['TensorFlow', 'PyTorch', 'NLP', 'Computer Vision', 'Deep Learning']),
                'required_skills_soft' => json_encode(['Research Skills', 'Innovation']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Cloud Architect',
                'description' => 'Design and manage cloud infrastructure.',
                'required_skills_general' => json_encode(['Azure', 'GCP', 'AWS', 'Terraform', 'Serverless']),
                'required_skills_soft' => json_encode(['Strategic Thinking', 'Problem Solving']),
                'required_experience_years' => 5,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Mobile App Developer',
                'description' => 'Create applications for iOS and Android platforms.',
                'required_skills_general' => json_encode(['Swift', 'Kotlin', 'React Native', 'Flutter', 'Firebase']),
                'required_skills_soft' => json_encode(['User Empathy', 'Adaptability']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Full Stack Developer',
                'description' => 'Work on both frontend and backend components.',
                'required_skills_general' => json_encode(['JavaScript', 'Node.js', 'React', 'Express.js', 'MongoDB', 'HTML', 'CSS']),
                'required_skills_soft' => json_encode(['Versatility', 'Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
        ];
        foreach ($cs_jobs as $job) {
            $jobRequirements[] = array_merge($job, ['primary_field' => 'computer_science', 'created_at' => now(), 'updated_at' => now()]);
        }

        // Medical Job Requirements (10 examples)
        $medical_jobs = [
            [
                'job_title' => 'Registered Nurse',
                'description' => 'Provide patient care and support.',
                'required_skills_general' => json_encode(['Patient Assessment', 'Medication Administration', 'Wound Care', 'IV Therapy']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Critical Thinking']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Medical Doctor (General Practitioner)',
                'description' => 'Diagnose and treat common illnesses.',
                'required_skills_general' => json_encode(['Diagnosis', 'Treatment Planning', 'Patient Counseling', 'Pharmacology']),
                'required_skills_soft' => json_encode(['Compassion', 'Decision Making', 'Problem Solving']),
                'required_experience_years' => 5, // Includes residency
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Surgeon',
                'description' => 'Perform surgical procedures.',
                'required_skills_general' => json_encode(['Anatomy', 'Surgical Techniques', 'Sterilization', 'Post-operative Care']),
                'required_skills_soft' => json_encode(['Precision', 'Stress Management', 'Teamwork']),
                'required_experience_years' => 7, // Includes residency and fellowship
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Pharmacist',
                'description' => 'Dispense medications and provide drug information.',
                'required_skills_general' => json_encode(['Pharmacology', 'Medication Dispensing', 'Patient Counseling', 'Compounding']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Communication', 'Ethics']),
                'required_experience_years' => 0, // Entry level with degree
                'required_experience_entries' => 1,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Medical Laboratory Technician',
                'description' => 'Perform lab tests on patient samples.',
                'required_skills_general' => json_encode(['Microscopy', 'Sample Analysis', 'Quality Control', 'Lab Equipment Operation']),
                'required_skills_soft' => json_encode(['Accuracy', 'Organization', 'Problem Solving']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
             [
                'job_title' => 'Radiologic Technologist',
                'description' => 'Perform diagnostic imaging procedures (X-rays, CT scans).',
                'required_skills_general' => json_encode(['Medical Imaging', 'Patient Positioning', 'Radiation Safety', 'Image Processing']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Interpersonal Skills', 'Calmness']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Physical Therapist',
                'description' => 'Help patients recover from injuries and illnesses through physical rehabilitation.',
                'required_skills_general' => json_encode(['Therapeutic Exercise', 'Manual Therapy', 'Gait Training', 'Patient Education']),
                'required_skills_soft' => json_encode(['Motivation', 'Patience', 'Communication']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Healthcare Administrator',
                'description' => 'Manage the operations of healthcare facilities.',
                'required_skills_general' => json_encode(['Healthcare Management', 'Budgeting', 'Policy Development', 'Staff Supervision']),
                'required_skills_soft' => json_encode(['Leadership', 'Organizational Skills', 'Decision Making']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Dental Hygienist',
                'description' => 'Provide preventative dental care and patient education.',
                'required_skills_general' => json_encode(['Oral Prophylaxis', 'Dental Radiography', 'Periodontal Charting', 'Patient Education']),
                'required_skills_soft' => json_encode(['Gentleness', 'Communication', 'Attention to Detail']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Paramedic',
                'description' => 'Provide emergency medical care in pre-hospital settings.',
                'required_skills_general' => json_encode(['Advanced Life Support (ALS)', 'Trauma Care', 'Emergency Pharmacology', 'Patient Triage']),
                'required_skills_soft' => json_encode(['Quick Thinking', 'Stress Resilience', 'Compassion']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ]
        ];
        foreach ($medical_jobs as $job) {
            $jobRequirements[] = array_merge($job, ['primary_field' => 'medical', 'created_at' => now(), 'updated_at' => now()]);
        }

        // Finance Job Requirements (10 examples)
        $finance_jobs = [
            [
                'job_title' => 'Financial Analyst',
                'description' => 'Analyze financial data and provide insights.',
                'required_skills_general' => json_encode(['Financial Modeling', 'Valuation', 'Excel', 'PowerPoint', 'Bloomberg']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Attention to Detail', 'Communication']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Accountant',
                'description' => 'Manage financial records and prepare statements.',
                'required_skills_general' => json_encode(['GAAP', 'IFRS', 'Auditing', 'Taxation', 'QuickBooks']),
                'required_skills_soft' => json_encode(['Accuracy', 'Integrity', 'Organizational Skills']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Investment Banker',
                'description' => 'Advise companies on mergers, acquisitions, and capital raising.',
                'required_skills_general' => json_encode(['Mergers & Acquisitions', 'Capital Markets', 'Financial Modeling', 'Due Diligence']),
                'required_skills_soft' => json_encode(['Negotiation', 'Presentation Skills', 'Resilience']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Financial Advisor',
                'description' => 'Provide financial planning and investment advice to clients.',
                'required_skills_general' => json_encode(['Investment Management', 'Retirement Planning', 'Estate Planning', 'Risk Management']),
                'required_skills_soft' => json_encode(['Interpersonal Skills', 'Trustworthiness', 'Client Focus']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Risk Manager',
                'description' => 'Identify and mitigate financial risks for an organization.',
                'required_skills_general' => json_encode(['Risk Assessment', 'Quantitative Analysis', 'Regulatory Compliance', 'Hedging']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Strategic Thinking', 'Decision Making']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Auditor',
                'description' => 'Examine financial records for accuracy and compliance.',
                'required_skills_general' => json_encode(['Internal Controls', 'Audit Standards (GAAS)', 'Forensic Accounting', 'Data Analysis']),
                'required_skills_soft' => json_encode(['Skepticism', 'Objectivity', 'Attention to Detail']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Corporate Treasurer',
                'description' => 'Manage an organization\'s cash flow, debt, and investments.',
                'required_skills_general' => json_encode(['Cash Management', 'Debt Financing', 'Capital Budgeting', 'Foreign Exchange']),
                'required_skills_soft' => json_encode(['Strategic Planning', 'Negotiation', 'Leadership']),
                'required_experience_years' => 7,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Budget Analyst',
                'description' => 'Develop and manage organizational budgets.',
                'required_skills_general' => json_encode(['Budgeting Software', 'Variance Analysis', 'Forecasting', 'Cost-Benefit Analysis']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Communication', 'Organizational Skills']),
                'required_experience_years' => 3,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Credit Analyst',
                'description' => 'Assess the creditworthiness of individuals or businesses.',
                'required_skills_general' => json_encode(['Financial Statement Analysis', 'Credit Scoring Models', 'Loan Origination', 'Debt Collection']),
                'required_skills_soft' => json_encode(['Judgment', 'Attention to Detail', 'Decision Making']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Compliance Officer (Finance)',
                'description' => 'Ensure adherence to financial regulations and internal policies.',
                'required_skills_general' => json_encode(['AML/KYC', 'Regulatory Reporting', 'Policy Development', 'Internal Audit']),
                'required_skills_soft' => json_encode(['Integrity', 'Ethical Judgment', 'Communication']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ]
        ];
        foreach ($finance_jobs as $job) {
            $jobRequirements[] = array_merge($job, ['primary_field' => 'finance', 'created_at' => now(), 'updated_at' => now()]);
        }

        // Batch insert
        JobRequirement::insert($jobRequirements);
    }
}
