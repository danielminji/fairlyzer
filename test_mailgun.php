<?php

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

// Test Mailgun configuration
$emailService = app('App\Services\MailgunService');

echo "Testing Mailgun Configuration:\n";
echo "Domain: " . config('services.mailgun.domain') . "\n";
echo "From Email: " . config('services.mailgun.from_email') . "\n";
echo "API Key Present: " . (!empty(config('services.mailgun.secret')) ? 'Yes' : 'No') . "\n";

// You can test sending an email by uncommenting the line below
// and replacing 'your-email@example.com' with an authorized email address
echo "\nEnter an authorized email address to test (or press Enter to skip): ";
$handle = fopen("php://stdin", "r");
$testEmail = trim(fgets($handle));
fclose($handle);

if (!empty($testEmail)) {
    echo "Testing email send to: $testEmail\n";
    $result = $emailService->send($testEmail, 'Test User', 'Mailgun Test', ['message' => 'This is a test email from Mailgun sandbox.']);
    echo "Email send result: " . ($result ? 'Success' : 'Failed') . "\n";
    echo "Check the Laravel logs for detailed error information if it failed.\n";
}

echo "\nTo test email sending:\n";
echo "1. Add your email to Mailgun authorized recipients in the dashboard\n";
echo "2. Run this script and enter your authorized email when prompted\n";
