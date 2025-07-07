<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Mailgun, Postmark, AWS and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'resend' => [
        'key' => env('RESEND_KEY'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    'geoapify' => [
        'api_key' => env('GEOAPIFY_API_KEY'),
    ],

    /*
     * Mailgun API Configuration
     */
    'mailgun' => [
        'domain' => env('MAILGUN_DOMAIN'),
        'secret' => env('MAILGUN_SECRET'),
        'from_email' => env('MAILGUN_FROM_EMAIL', 'noreply@resume-system.com'),
        'from_name' => env('MAILGUN_FROM_NAME', 'Resume System'),
    ],

    /*
     * EmailJS API Configuration (Legacy)
     */
    // 'emailjs' => [
    //     'service_id' => env('EMAILJS_SERVICE_ID', 'service_tkaezxq'),
    //     'template_id' => env('EMAILJS_TEMPLATE_ID', 'template_726x0bt'),
    //     'public_key' => env('EMAILJS_PUBLIC_KEY', 'cB89naFzev32g-tTN'),
    //     'private_key' => env('EMAILJS_PRIVATE_KEY', '7OA_S9jvYm5xZxNjrI_Eu'),
    // ],

];
