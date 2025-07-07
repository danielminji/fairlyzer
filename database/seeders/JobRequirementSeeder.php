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
            // Additional 30 Computer Science Jobs
            [
                'job_title' => 'Database Administrator',
                'description' => 'Maintain and optimize database systems.',
                'required_skills_general' => json_encode(['SQL', 'Oracle', 'PostgreSQL', 'MongoDB', 'Database Design']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Detail Oriented']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Systems Analyst',
                'description' => 'Analyze and design information systems.',
                'required_skills_general' => json_encode(['Systems Analysis', 'UML', 'Business Process Modeling', 'Requirements Gathering']),
                'required_skills_soft' => json_encode(['Communication', 'Analytical Thinking']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Network Engineer',
                'description' => 'Design and maintain network infrastructure.',
                'required_skills_general' => json_encode(['Cisco', 'Routing', 'Switching', 'TCP/IP', 'Network Security']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Technical Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'QA Engineer',
                'description' => 'Ensure software quality through testing.',
                'required_skills_general' => json_encode(['Test Automation', 'Selenium', 'JUnit', 'Manual Testing', 'Bug Tracking']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Critical Thinking']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Product Manager (Tech)',
                'description' => 'Manage product development lifecycle.',
                'required_skills_general' => json_encode(['Agile', 'Scrum', 'Product Strategy', 'Market Research', 'Analytics']),
                'required_skills_soft' => json_encode(['Leadership', 'Strategic Thinking']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Blockchain Developer',
                'description' => 'Develop blockchain applications and smart contracts.',
                'required_skills_general' => json_encode(['Solidity', 'Ethereum', 'Web3', 'Smart Contracts', 'Cryptography']),
                'required_skills_soft' => json_encode(['Innovation', 'Problem Solving']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Game Developer',
                'description' => 'Create video games and interactive entertainment.',
                'required_skills_general' => json_encode(['Unity', 'Unreal Engine', 'C#', 'C++', 'Game Design']),
                'required_skills_soft' => json_encode(['Creativity', 'Collaboration']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'UI/UX Designer',
                'description' => 'Design user interfaces and experiences.',
                'required_skills_general' => json_encode(['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research']),
                'required_skills_soft' => json_encode(['Creativity', 'Empathy']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'IT Support Specialist',
                'description' => 'Provide technical support and troubleshooting.',
                'required_skills_general' => json_encode(['Windows', 'Linux', 'Hardware Troubleshooting', 'Active Directory', 'Help Desk']),
                'required_skills_soft' => json_encode(['Patience', 'Communication']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 2.8
            ],
            [
                'job_title' => 'Business Intelligence Analyst',
                'description' => 'Analyze business data to provide insights.',
                'required_skills_general' => json_encode(['Tableau', 'Power BI', 'SQL', 'Data Warehousing', 'ETL']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Site Reliability Engineer',
                'description' => 'Ensure system reliability and performance.',
                'required_skills_general' => json_encode(['Monitoring', 'Kubernetes', 'Prometheus', 'Grafana', 'Incident Response']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Stress Management']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Software Architect',
                'description' => 'Design high-level software system architecture.',
                'required_skills_general' => json_encode(['System Design', 'Microservices', 'Design Patterns', 'Scalability', 'Architecture']),
                'required_skills_soft' => json_encode(['Strategic Thinking', 'Leadership']),
                'required_experience_years' => 6,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Computer Vision Engineer',
                'description' => 'Develop computer vision and image processing systems.',
                'required_skills_general' => json_encode(['OpenCV', 'Deep Learning', 'Image Processing', 'Python', 'TensorFlow']),
                'required_skills_soft' => json_encode(['Research Skills', 'Innovation']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Embedded Systems Engineer',
                'description' => 'Develop software for embedded systems.',
                'required_skills_general' => json_encode(['C', 'C++', 'Microcontrollers', 'RTOS', 'Hardware Integration']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Attention to Detail']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Technical Writer',
                'description' => 'Create technical documentation and guides.',
                'required_skills_general' => json_encode(['Technical Writing', 'Documentation Tools', 'API Documentation', 'Content Management']),
                'required_skills_soft' => json_encode(['Communication', 'Clarity']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Information Security Analyst',
                'description' => 'Protect information systems from security threats.',
                'required_skills_general' => json_encode(['Security Frameworks', 'Risk Assessment', 'Incident Response', 'Compliance']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Thinking']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Robotics Engineer',
                'description' => 'Design and develop robotic systems.',
                'required_skills_general' => json_encode(['ROS', 'Control Systems', 'Sensors', 'Actuators', 'Automation']),
                'required_skills_soft' => json_encode(['Innovation', 'Problem Solving']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Data Engineer',
                'description' => 'Build and maintain data pipelines and infrastructure.',
                'required_skills_general' => json_encode(['Apache Spark', 'Kafka', 'Airflow', 'Data Warehousing', 'Big Data']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Attention to Detail']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Platform Engineer',
                'description' => 'Build and maintain development platforms.',
                'required_skills_general' => json_encode(['Infrastructure as Code', 'Terraform', 'CI/CD', 'Cloud Platforms', 'Automation']),
                'required_skills_soft' => json_encode(['Collaboration', 'Problem Solving']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'AR/VR Developer',
                'description' => 'Develop augmented and virtual reality applications.',
                'required_skills_general' => json_encode(['Unity', 'Unreal Engine', 'ARCore', 'ARKit', '3D Modeling']),
                'required_skills_soft' => json_encode(['Creativity', 'Innovation']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'IoT Developer',
                'description' => 'Develop Internet of Things applications.',
                'required_skills_general' => json_encode(['IoT Protocols', 'Sensors', 'Edge Computing', 'MQTT', 'Cloud Integration']),
                'required_skills_soft' => json_encode(['Innovation', 'Problem Solving']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Enterprise Architect',
                'description' => 'Design enterprise-wide IT architecture.',
                'required_skills_general' => json_encode(['Enterprise Architecture', 'TOGAF', 'Business Analysis', 'Strategic Planning']),
                'required_skills_soft' => json_encode(['Strategic Thinking', 'Leadership']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Performance Engineer',
                'description' => 'Optimize application and system performance.',
                'required_skills_general' => json_encode(['Performance Testing', 'Load Testing', 'JMeter', 'Profiling', 'Optimization']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Problem Solving']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'API Developer',
                'description' => 'Design and develop APIs and web services.',
                'required_skills_general' => json_encode(['REST APIs', 'GraphQL', 'API Design', 'Microservices', 'API Security']),
                'required_skills_soft' => json_encode(['Problem Solving', 'Communication']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Machine Learning Engineer',
                'description' => 'Deploy and maintain ML models in production.',
                'required_skills_general' => json_encode(['MLOps', 'Model Deployment', 'Feature Engineering', 'A/B Testing', 'Model Monitoring']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Problem Solving']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Security Engineer',
                'description' => 'Implement security measures and protocols.',
                'required_skills_general' => json_encode(['Security Architecture', 'Penetration Testing', 'Vulnerability Assessment', 'Secure Coding']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Ethical Thinking']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Solutions Architect',
                'description' => 'Design technical solutions for business problems.',
                'required_skills_general' => json_encode(['Solution Design', 'Cloud Architecture', 'Integration Patterns', 'Scalability']),
                'required_skills_soft' => json_encode(['Strategic Thinking', 'Communication']),
                'required_experience_years' => 5,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Research Scientist (AI)',
                'description' => 'Conduct research in artificial intelligence.',
                'required_skills_general' => json_encode(['Research Methodology', 'Machine Learning', 'Deep Learning', 'Publications', 'Statistics']),
                'required_skills_soft' => json_encode(['Research Skills', 'Innovation']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Technical Lead',
                'description' => 'Lead technical teams and projects.',
                'required_skills_general' => json_encode(['Leadership', 'Project Management', 'Code Review', 'Mentoring', 'Architecture']),
                'required_skills_soft' => json_encode(['Leadership', 'Communication']),
                'required_experience_years' => 5,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Scrum Master',
                'description' => 'Facilitate agile development processes.',
                'required_skills_general' => json_encode(['Scrum', 'Agile Methodologies', 'Facilitation', 'Jira', 'Team Coaching']),
                'required_skills_soft' => json_encode(['Leadership', 'Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.1
            ]
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
            ],
                // Additional 30 Medical Jobs
                [
                    'job_title' => 'Anesthesiologist',
                    'description' => 'Administer anesthesia during surgical procedures.',
                    'required_skills_general' => json_encode(['Anesthesia Administration', 'Patient Monitoring', 'Pain Management', 'Critical Care']),
                    'required_skills_soft' => json_encode(['Precision', 'Stress Management', 'Quick Decision Making']),
                'required_experience_years' => 8, // Includes residency
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Cardiologist',
                'description' => 'Diagnose and treat heart-related conditions.',
                'required_skills_general' => json_encode(['Cardiology', 'Echocardiography', 'Cardiac Catheterization', 'ECG Interpretation']),
                'required_skills_soft' => json_encode(['Empathy', 'Precision', 'Communication']),
                'required_experience_years' => 9, // Includes fellowship
                'required_experience_entries' => 3,
                'required_cgpa' => 3.9
            ],
            [
                'job_title' => 'Neurologist',
                'description' => 'Treat disorders of the nervous system.',
                'required_skills_general' => json_encode(['Neurology', 'EEG Interpretation', 'Neuroimaging', 'Diagnostic Testing']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Patience', 'Empathy']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Psychiatrist',
                'description' => 'Diagnose and treat mental health disorders.',
                'required_skills_general' => json_encode(['Mental Health Assessment', 'Psychopharmacology', 'Therapy', 'Crisis Intervention']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Patience']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Orthopedic Surgeon',
                'description' => 'Perform surgery on musculoskeletal system.',
                'required_skills_general' => json_encode(['Orthopedic Surgery', 'Bone Repair', 'Joint Replacement', 'Sports Medicine']),
                'required_skills_soft' => json_encode(['Precision', 'Physical Stamina', 'Problem Solving']),
                'required_experience_years' => 10,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Pediatrician',
                'description' => 'Provide medical care to infants, children, and adolescents.',
                'required_skills_general' => json_encode(['Pediatric Medicine', 'Child Development', 'Immunizations', 'Growth Assessment']),
                'required_skills_soft' => json_encode(['Patience', 'Communication', 'Gentle Manner']),
                'required_experience_years' => 6,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Dermatologist',
                'description' => 'Diagnose and treat skin, hair, and nail conditions.',
                'required_skills_general' => json_encode(['Dermatology', 'Skin Biopsy', 'Dermatologic Surgery', 'Cosmetic Procedures']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Patient Communication', 'Aesthetic Sense']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Radiologist',
                'description' => 'Interpret medical images for diagnosis.',
                'required_skills_general' => json_encode(['Medical Imaging', 'CT Interpretation', 'MRI Reading', 'Interventional Radiology']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Thinking', 'Concentration']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Pathologist',
                'description' => 'Diagnose diseases through laboratory analysis.',
                'required_skills_general' => json_encode(['Histopathology', 'Autopsy', 'Laboratory Medicine', 'Microscopy']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Thinking', 'Precision']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Emergency Medicine Physician',
                'description' => 'Provide emergency medical care.',
                'required_skills_general' => json_encode(['Emergency Medicine', 'Trauma Care', 'Resuscitation', 'Triage']),
                'required_skills_soft' => json_encode(['Quick Thinking', 'Stress Management', 'Leadership']),
                'required_experience_years' => 6,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Oncologist',
                'description' => 'Treat cancer patients.',
                'required_skills_general' => json_encode(['Oncology', 'Chemotherapy', 'Radiation Therapy', 'Palliative Care']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Emotional Resilience']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Obstetrician-Gynecologist',
                'description' => 'Provide women\'s reproductive health care.',
                'required_skills_general' => json_encode(['Obstetrics', 'Gynecology', 'Prenatal Care', 'Surgical Procedures']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Gentle Care']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Ophthalmologist',
                'description' => 'Diagnose and treat eye and vision disorders.',
                'required_skills_general' => json_encode(['Ophthalmology', 'Eye Surgery', 'Vision Testing', 'Retinal Examination']),
                'required_skills_soft' => json_encode(['Precision', 'Patience', 'Attention to Detail']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'ENT Specialist',
                'description' => 'Treat ear, nose, and throat disorders.',
                'required_skills_general' => json_encode(['Otolaryngology', 'Endoscopy', 'Hearing Tests', 'Head and Neck Surgery']),
                'required_skills_soft' => json_encode(['Precision', 'Patient Care', 'Communication']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Urologist',
                'description' => 'Treat urinary tract and male reproductive system disorders.',
                'required_skills_general' => json_encode(['Urology', 'Endoscopic Surgery', 'Kidney Stone Treatment', 'Prostate Care']),
                'required_skills_soft' => json_encode(['Precision', 'Patient Communication', 'Empathy']),
                'required_experience_years' => 8,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Gastroenterologist',
                'description' => 'Treat digestive system disorders.',
                'required_skills_general' => json_encode(['Gastroenterology', 'Endoscopy', 'Colonoscopy', 'Liver Disease']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Patient Care', 'Communication']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Pulmonologist',
                'description' => 'Treat respiratory system disorders.',
                'required_skills_general' => json_encode(['Pulmonology', 'Bronchoscopy', 'Sleep Studies', 'Ventilator Management']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Patient Care', 'Communication']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Endocrinologist',
                'description' => 'Treat hormone and endocrine system disorders.',
                'required_skills_general' => json_encode(['Endocrinology', 'Diabetes Management', 'Hormone Therapy', 'Metabolic Disorders']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Patient Education', 'Empathy']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Rheumatologist',
                'description' => 'Treat autoimmune and inflammatory diseases.',
                'required_skills_general' => json_encode(['Rheumatology', 'Autoimmune Diseases', 'Joint Injections', 'Immunosuppressive Therapy']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Patient Care', 'Empathy']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Infectious Disease Specialist',
                'description' => 'Diagnose and treat infectious diseases.',
                'required_skills_general' => json_encode(['Infectious Diseases', 'Antibiotic Therapy', 'Infection Control', 'Epidemiology']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Problem Solving', 'Communication']),
                'required_experience_years' => 9,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.8
            ],
            [
                'job_title' => 'Clinical Pharmacist',
                'description' => 'Provide pharmaceutical care in clinical settings.',
                'required_skills_general' => json_encode(['Clinical Pharmacy', 'Drug Interactions', 'Dosing', 'Patient Counseling']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Communication', 'Critical Thinking']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Occupational Therapist',
                'description' => 'Help patients develop skills for daily living.',
                'required_skills_general' => json_encode(['Occupational Therapy', 'Activity Analysis', 'Adaptive Equipment', 'Rehabilitation']),
                'required_skills_soft' => json_encode(['Patience', 'Creativity', 'Empathy']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Speech-Language Pathologist',
                'description' => 'Treat communication and swallowing disorders.',
                'required_skills_general' => json_encode(['Speech Therapy', 'Language Assessment', 'Swallowing Evaluation', 'Articulation']),
                'required_skills_soft' => json_encode(['Patience', 'Communication', 'Creativity']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Respiratory Therapist',
                'description' => 'Provide respiratory care and therapy.',
                'required_skills_general' => json_encode(['Respiratory Therapy', 'Ventilator Management', 'Oxygen Therapy', 'Pulmonary Function']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Patient Care', 'Quick Thinking']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Medical Social Worker',
                'description' => 'Provide social services in healthcare settings.',
                'required_skills_general' => json_encode(['Social Work', 'Case Management', 'Discharge Planning', 'Resource Coordination']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Problem Solving']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Dietitian/Nutritionist',
                'description' => 'Provide nutrition counseling and meal planning.',
                'required_skills_general' => json_encode(['Nutrition Science', 'Meal Planning', 'Dietary Assessment', 'Counseling']),
                'required_skills_soft' => json_encode(['Communication', 'Empathy', 'Motivation']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Medical Technologist',
                'description' => 'Perform complex laboratory tests.',
                'required_skills_general' => json_encode(['Laboratory Testing', 'Hematology', 'Chemistry', 'Microbiology']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Accuracy', 'Problem Solving']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Surgical Technologist',
                'description' => 'Assist in surgical procedures.',
                'required_skills_general' => json_encode(['Surgical Procedures', 'Sterile Technique', 'Surgical Instruments', 'Patient Positioning']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Teamwork', 'Stress Management']),
                'required_experience_years' => 1,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Perfusionist',
                'description' => 'Operate heart-lung machines during surgery.',
                'required_skills_general' => json_encode(['Perfusion Technology', 'Heart-Lung Machine', 'Blood Management', 'Cardiac Surgery']),
                'required_skills_soft' => json_encode(['Precision', 'Stress Management', 'Attention to Detail']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Genetic Counselor',
                'description' => 'Provide guidance on genetic conditions.',
                'required_skills_general' => json_encode(['Genetics', 'Counseling', 'Risk Assessment', 'Family History']),
                'required_skills_soft' => json_encode(['Empathy', 'Communication', 'Analytical Thinking']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
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
                'required_cgpa' => 3.4,
            ],
            // Additional 30 Finance Jobs
            [
                'job_title' => 'Portfolio Manager',
                'description' => 'Manage investment portfolios for clients.',
                'required_skills_general' => json_encode(['Portfolio Management', 'Asset Allocation', 'Risk Management', 'Performance Analysis']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Decision Making', 'Client Relations']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Equity Research Analyst',
                'description' => 'Research and analyze stocks and equity markets.',
                'required_skills_general' => json_encode(['Equity Research', 'Financial Modeling', 'Industry Analysis', 'Report Writing']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Communication', 'Attention to Detail']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Fixed Income Analyst',
                'description' => 'Analyze bonds and fixed income securities.',
                'required_skills_general' => json_encode(['Bond Analysis', 'Interest Rate Models', 'Credit Analysis', 'Duration Analysis']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Attention to Detail', 'Problem Solving']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Quantitative Analyst',
                'description' => 'Use mathematical models for financial analysis.',
                'required_skills_general' => json_encode(['Quantitative Analysis', 'Python', 'R', 'Statistical Modeling', 'Derivatives']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Problem Solving', 'Attention to Detail']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Private Equity Associate',
                'description' => 'Analyze and execute private equity investments.',
                'required_skills_general' => json_encode(['Private Equity', 'LBO Modeling', 'Due Diligence', 'Valuation']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Communication', 'Work Ethic']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.7
            ],
            [
                'job_title' => 'Venture Capital Analyst',
                'description' => 'Evaluate startup investment opportunities.',
                'required_skills_general' => json_encode(['Venture Capital', 'Startup Analysis', 'Market Research', 'Financial Modeling']),
                'required_skills_soft' => json_encode(['Innovation', 'Risk Assessment', 'Communication']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Hedge Fund Analyst',
                'description' => 'Conduct research for hedge fund investments.',
                'required_skills_general' => json_encode(['Hedge Fund Strategies', 'Alternative Investments', 'Risk Management', 'Performance Attribution']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Stress Management', 'Quick Thinking']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Corporate Finance Manager',
                'description' => 'Manage corporate financial planning and analysis.',
                'required_skills_general' => json_encode(['Corporate Finance', 'FP&A', 'Capital Structure', 'M&A Analysis']),
                'required_skills_soft' => json_encode(['Leadership', 'Strategic Thinking', 'Communication']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Treasury Analyst',
                'description' => 'Manage cash flow and liquidity.',
                'required_skills_general' => json_encode(['Cash Management', 'Liquidity Planning', 'Banking Relations', 'Foreign Exchange']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Skills', 'Organization']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Tax Analyst',
                'description' => 'Prepare and analyze tax returns and strategies.',
                'required_skills_general' => json_encode(['Tax Preparation', 'Tax Law', 'Tax Planning', 'Compliance']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Skills', 'Organization']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Forensic Accountant',
                'description' => 'Investigate financial fraud and disputes.',
                'required_skills_general' => json_encode(['Forensic Accounting', 'Fraud Investigation', 'Litigation Support', 'Data Analysis']),
                'required_skills_soft' => json_encode(['Investigative Skills', 'Attention to Detail', 'Integrity']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Actuary',
                'description' => 'Assess risk and uncertainty using mathematics and statistics.',
                'required_skills_general' => json_encode(['Actuarial Science', 'Risk Assessment', 'Statistics', 'Insurance']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Problem Solving', 'Attention to Detail']),
                'required_experience_years' => 3,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Insurance Underwriter',
                'description' => 'Evaluate insurance applications and determine coverage.',
                'required_skills_general' => json_encode(['Underwriting', 'Risk Assessment', 'Insurance Products', 'Policy Analysis']),
                'required_skills_soft' => json_encode(['Decision Making', 'Analytical Skills', 'Attention to Detail']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.1
            ],
            [
                'job_title' => 'Loan Officer',
                'description' => 'Evaluate and approve loan applications.',
                'required_skills_general' => json_encode(['Loan Processing', 'Credit Analysis', 'Underwriting', 'Customer Service']),
                'required_skills_soft' => json_encode(['Communication', 'Decision Making', 'Customer Focus']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.0
            ],
            [
                'job_title' => 'Commercial Banker',
                'description' => 'Provide banking services to businesses.',
                'required_skills_general' => json_encode(['Commercial Banking', 'Business Development', 'Credit Analysis', 'Relationship Management']),
                'required_skills_soft' => json_encode(['Relationship Building', 'Communication', 'Sales Skills']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.2
            ],
            [
                'job_title' => 'Wealth Manager',
                'description' => 'Provide comprehensive financial planning for high-net-worth clients.',
                'required_skills_general' => json_encode(['Wealth Management', 'Estate Planning', 'Tax Planning', 'Investment Advisory']),
                'required_skills_soft' => json_encode(['Client Relations', 'Trust Building', 'Communication']),
                'required_experience_years' => 5,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Real Estate Analyst',
                'description' => 'Analyze real estate investments and markets.',
                'required_skills_general' => json_encode(['Real Estate Analysis', 'Property Valuation', 'Market Research', 'REIT Analysis']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Market Awareness', 'Attention to Detail']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Commodities Trader',
                'description' => 'Trade commodities and manage trading positions.',
                'required_skills_general' => json_encode(['Commodities Trading', 'Market Analysis', 'Risk Management', 'Derivatives']),
                'required_skills_soft' => json_encode(['Quick Decision Making', 'Stress Management', 'Risk Taking']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Pension Fund Manager',
                'description' => 'Manage pension fund investments and operations.',
                'required_skills_general' => json_encode(['Pension Management', 'Asset Allocation', 'Liability Matching', 'Regulatory Compliance']),
                'required_skills_soft' => json_encode(['Strategic Thinking', 'Analytical Skills', 'Responsibility']),
                'required_experience_years' => 7,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'Financial Controller',
                'description' => 'Oversee accounting operations and financial reporting.',
                'required_skills_general' => json_encode(['Financial Reporting', 'Management Accounting', 'Budgeting', 'Internal Controls']),
                'required_skills_soft' => json_encode(['Leadership', 'Attention to Detail', 'Organization']),
                'required_experience_years' => 6,
                'required_experience_entries' => 3,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'CFO (Chief Financial Officer)',
                'description' => 'Lead financial strategy and operations.',
                'required_skills_general' => json_encode(['Strategic Finance', 'Leadership', 'Financial Planning', 'Investor Relations']),
                'required_skills_soft' => json_encode(['Executive Leadership', 'Strategic Vision', 'Communication']),
                'required_experience_years' => 10,
                'required_experience_entries' => 4,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Financial Consultant',
                'description' => 'Provide financial advice and consulting services.',
                'required_skills_general' => json_encode(['Financial Consulting', 'Business Analysis', 'Strategic Planning', 'Client Management']),
                'required_skills_soft' => json_encode(['Consulting Skills', 'Communication', 'Problem Solving']),
                'required_experience_years' => 4,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Mergers & Acquisitions Analyst',
                'description' => 'Analyze and execute M&A transactions.',
                'required_skills_general' => json_encode(['M&A Analysis', 'Valuation', 'Due Diligence', 'Transaction Execution']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Attention to Detail', 'Work Ethic']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Derivatives Trader',
                'description' => 'Trade financial derivatives and manage risk.',
                'required_skills_general' => json_encode(['Derivatives Trading', 'Options', 'Futures', 'Risk Management']),
                'required_skills_soft' => json_encode(['Quick Thinking', 'Risk Management', 'Stress Tolerance']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.5
            ],
            [
                'job_title' => 'ESG Analyst',
                'description' => 'Analyze environmental, social, and governance factors.',
                'required_skills_general' => json_encode(['ESG Analysis', 'Sustainability Reporting', 'Impact Investing', 'Stakeholder Engagement']),
                'required_skills_soft' => json_encode(['Ethical Thinking', 'Research Skills', 'Communication']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Cryptocurrency Analyst',
                'description' => 'Analyze cryptocurrency markets and blockchain technology.',
                'required_skills_general' => json_encode(['Cryptocurrency', 'Blockchain', 'DeFi', 'Market Analysis']),
                'required_skills_soft' => json_encode(['Innovation', 'Risk Assessment', 'Adaptability']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Financial Data Scientist',
                'description' => 'Apply data science to financial problems.',
                'required_skills_general' => json_encode(['Data Science', 'Machine Learning', 'Financial Modeling', 'Python']),
                'required_skills_soft' => json_encode(['Analytical Thinking', 'Innovation', 'Problem Solving']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.6
            ],
            [
                'job_title' => 'Regulatory Affairs Specialist',
                'description' => 'Ensure compliance with financial regulations.',
                'required_skills_general' => json_encode(['Regulatory Compliance', 'Policy Analysis', 'Reporting', 'Risk Assessment']),
                'required_skills_soft' => json_encode(['Attention to Detail', 'Analytical Skills', 'Communication']),
                'required_experience_years' => 3,
                'required_experience_entries' => 2,
                'required_cgpa' => 3.3
            ],
            [
                'job_title' => 'Capital Markets Analyst',
                'description' => 'Analyze capital markets and debt/equity financing.',
                'required_skills_general' => json_encode(['Capital Markets', 'Debt Financing', 'Equity Markets', 'Market Research']),
                'required_skills_soft' => json_encode(['Analytical Skills', 'Market Awareness', 'Communication']),
                'required_experience_years' => 2,
                'required_experience_entries' => 1,
                'required_cgpa' => 3.4
            ],
            [
                'job_title' => 'Financial Technology Specialist',
                'description' => 'Develop and implement financial technology solutions.',
                'required_skills_general' => json_encode(['FinTech', 'Financial Systems', 'API Integration', 'Digital Payments']),
                'required_skills_soft' => json_encode(['Innovation', 'Problem Solving', 'Adaptability']),
                'required_experience_years' => 3,
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
