<?php

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\Http;

echo "=== COMPREHENSIVE MAILGUN TEST ===\n\n";

// Configuration
$domain = config('services.mailgun.domain');
$apiKey = config('services.mailgun.secret');
$fromEmail = config('services.mailgun.from_email');

echo "Configuration:\n";
echo "Domain: $domain\n";
echo "From Email: $fromEmail\n";
echo "API Key: " . substr($apiKey, 0, 10) . "...\n\n";

// Test 1: Check domain info
echo "=== TEST 1: Domain Information ===\n";
try {
    $response = Http::withBasicAuth('api', $apiKey)
        ->get("https://api.mailgun.net/v3/domains/$domain");
    
    if ($response->successful()) {
        $data = $response->json();
        echo "✓ Domain is valid\n";
        echo "Domain State: " . ($data['domain']['state'] ?? 'unknown') . "\n";
        echo "Domain Type: " . ($data['domain']['type'] ?? 'unknown') . "\n";
    } else {
        echo "✗ Failed to get domain info: " . $response->status() . "\n";
        echo "Response: " . $response->body() . "\n";
    }
} catch (Exception $e) {
    echo "✗ Error: " . $e->getMessage() . "\n";
}

echo "\n=== TEST 2: Send Test Email ===\n";
echo "Enter your email address: ";
$handle = fopen("php://stdin", "r");
$testEmail = trim(fgets($handle));
fclose($handle);

if (!empty($testEmail)) {
    try {
        $response = Http::withBasicAuth('api', $apiKey)
            ->asForm()
            ->post("https://api.mailgun.net/v3/$domain/messages", [
                'from' => "Test <$fromEmail>",
                'to' => $testEmail,
                'subject' => 'Mailgun Direct Test - ' . date('Y-m-d H:i:s'),
                'text' => "This is a direct test of Mailgun API.\n\nSent at: " . date('Y-m-d H:i:s') . "\n\nIf you receive this, Mailgun is working correctly.",
                'html' => "<h3>Mailgun Direct Test</h3><p>This is a direct test of Mailgun API.</p><p><strong>Sent at:</strong> " . date('Y-m-d H:i:s') . "</p><p>If you receive this, Mailgun is working correctly.</p>"
            ]);

        if ($response->successful()) {
            $data = $response->json();
            echo "✓ Email sent successfully!\n";
            echo "Mailgun ID: " . ($data['id'] ?? 'unknown') . "\n";
            echo "Message: " . ($data['message'] ?? 'unknown') . "\n";
            echo "\nCheck your email (including spam folder) in a few minutes.\n";
        } else {
            echo "✗ Failed to send email\n";
            echo "Status: " . $response->status() . "\n";
            echo "Response: " . $response->body() . "\n";
        }
    } catch (Exception $e) {
        echo "✗ Error: " . $e->getMessage() . "\n";
    }
}

echo "\n=== TROUBLESHOOTING TIPS ===\n";
echo "1. Check your Gmail spam/junk folder\n";
echo "2. Go to https://app.mailgun.com/app/sending/domains/$domain/authorized-recipients\n";
echo "   and make sure your email is listed as an authorized recipient\n";
echo "3. Check Mailgun logs at: https://app.mailgun.com/app/logs\n";
echo "4. For sandbox domains, emails can only be sent to authorized recipients\n";
