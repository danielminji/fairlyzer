<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class MailgunService
{
    /**
     * Mailgun API URL
     */
    protected $apiUrl;
    
    /**
     * Mailgun API Key
     */
    protected $apiKey;
    
    /**
     * Mailgun Domain
     */
    protected $domain;
    
    /**
     * From email address
     */
    protected $fromEmail;
    
    /**
     * From name
     */
    protected $fromName;

    /**
     * Create a new Mailgun Service instance.
     */
    public function __construct()
    {
        $this->apiKey = config('services.mailgun.secret');
        $this->domain = config('services.mailgun.domain');
        $this->apiUrl = "https://api.mailgun.net/v3/{$this->domain}/messages";
        $this->fromEmail = config('services.mailgun.from_email', 'noreply@' . $this->domain);
        $this->fromName = config('services.mailgun.from_name', 'Resume System');
    }

    /**
     * Send an email using Mailgun service.
     *
     * @param string $to_email Recipient email
     * @param string $to_name Recipient name
     * @param string $subject Email subject
     * @param array $templateParams Additional parameters
     * @return bool Success status
     */
    public function send(string $to_email, string $to_name, string $subject, array $templateParams = [])
    {
        try {
            // Extract message from template params
            $message = $templateParams['message'] ?? '';
            
            // Create recipient with name
            $to = "{$to_name} <{$to_email}>";
            
            // Prepare data for Mailgun API
            $data = [
                'from' => "{$this->fromName} <{$this->fromEmail}>",
                'to' => $to,
                'subject' => $subject,
                'text' => $message,
                // Optional HTML version can be added here if needed
                // 'html' => $html_message,
            ];
            
            // If you want to use Mailgun templates, you'd add template parameters here
            
            // Make API call to Mailgun
            $response = Http::withBasicAuth('api', $this->apiKey)->asForm()->post($this->apiUrl, $data);

            if ($response->successful()) {
                Log::info('Email sent successfully via Mailgun', ['to' => $to_email, 'subject' => $subject]);
                return true;
            }
            
            Log::error('Mailgun Error: ' . $response->body());
            return false;
        } catch (\Exception $e) {
            Log::error('Mailgun Exception: ' . $e->getMessage());
            return false;
        }
    }

    /**
     * Get template message for password reset
     *
     * @return string
     */
    protected function getPasswordResetMessage() 
    {
        return "Your password has been reset by an administrator. If you did not request this change, " .
               "please contact our support team immediately as your account may have been compromised.";
    }
    
    /**
     * Get template message for user status change
     * 
     * @param string $status New status description
     * @return string
     */
    protected function getStatusChangeMessage($status)
    {
        return "Your account status has been updated: {$status}. " . 
               "If you have any questions, please contact our support team.";
    }
    
    /**
     * Get template message for account deletion
     *
     * @return string
     */
    protected function getAccountDeletionMessage()
    {
        return "Your account has been deleted. We're sorry to see you go! " . 
               "If this was done in error, please contact our support team immediately.";
    }

    /**
     * Send a password reset notification.
     *
     * @param string $to_email Recipient email
     * @param string $to_name Recipient name
     * @return bool Success status
     */
    public function sendPasswordReset(string $to_email, string $to_name)
    {
        return $this->send(
            $to_email, 
            $to_name, 
            'Your Password Has Been Reset',
            [
                'message' => $this->getPasswordResetMessage()
            ]
        );
    }

    /**
     * Send a user status change notification.
     *
     * @param string $to_email Recipient email
     * @param string $to_name Recipient name
     * @param string $status_message Status change message
     * @return bool Success status
     */
    public function sendStatusChange(string $to_email, string $to_name, string $status_message)
    {
        return $this->send(
            $to_email, 
            $to_name, 
            'Your Account Status Has Been Updated',
            [
                'message' => $status_message
            ]
        );
    }

    /**
     * Send account deletion notification.
     *
     * @param string $to_email Recipient email
     * @param string $to_name Recipient name
     * @return bool Success status
     */
    public function sendAccountDeletion(string $to_email, string $to_name)
    {
        return $this->send(
            $to_email,
            $to_name,
            'Your Account Has Been Deleted',
            [
                'message' => $this->getAccountDeletionMessage()
            ]
        );
    }

    /**
     * Send notification for organizer application received (to applicant)
     *
     * @param string $to_email Organizer applicant email
     * @param string $to_name Organizer applicant name
     * @return bool Success status
     */
    public function sendOrganizerApplicationReceived(string $to_email, string $to_name)
    {
        $message = "Thank you for applying to be an organizer. Your application has been received and is pending approval. " .
                   "You will be notified once an administrator reviews your application.";
        
        return $this->send(
            $to_email, 
            $to_name, 
            'Organizer Application Received',
            [
                'message' => $message
            ]
        );
    }
    
    /**
     * Send notification to admin about new organizer application
     *
     * @param string $admin_email Admin email
     * @param string $admin_name Admin name
     * @param string $applicant_name Organizer applicant name
     * @param string $applicant_email Organizer applicant email
     * @param string $company_name Company name (if provided)
     * @return bool Success status
     */
    public function sendOrganizerApplicationNotification(string $admin_email, string $admin_name, string $applicant_name, string $applicant_email, string $company_name = '')
    {
        $message = "A new organizer application has been submitted.\n\n" .
                   "Name: {$applicant_name}\n" .
                   "Email: {$applicant_email}\n";
        
        if (!empty($company_name)) {
            $message .= "Company: {$company_name}\n\n";
        }
        
        $message .= "Please review this application in the admin dashboard.";
        
        return $this->send(
            $admin_email, 
            $admin_name, 
            'New Organizer Application',
            [
                'message' => $message
            ]
        );
    }
    
    /**
     * Send notification for organizer application approval
     *
     * @param string $to_email Organizer email
     * @param string $to_name Organizer name
     * @return bool Success status
     */
    public function sendOrganizerApproval(string $to_email, string $to_name)
    {
        $message = "Your organizer application has been approved. You can now access organizer features in the system.";
        
        return $this->send(
            $to_email, 
            $to_name, 
            'Organizer Application Approved',
            [
                'message' => $message
            ]
        );
    }
    
    /**
     * Send notification for organizer application rejection
     *
     * @param string $to_email Applicant email
     * @param string $to_name Applicant name
     * @return bool Success status
     */
    public function sendOrganizerRejection(string $to_email, string $to_name)
    {
        $message = "We regret to inform you that your organizer application has been declined. " .
                   "If you have any questions, please contact our support team.";
                   
        return $this->send(
            $to_email,
            $to_name,
            'Organizer Application Status Update',
            [
                'message' => $message
            ]
        );
    }
} 