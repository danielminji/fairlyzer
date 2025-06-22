# Mailgun Migration Guide

This document provides instructions for migrating the application's email service from EmailJS to Mailgun.

## Why We're Migrating

EmailJS is designed to be used with client-side JavaScript applications, not server-side PHP applications. Using it with PHP can lead to CORS issues and unreliable email delivery. Mailgun provides a robust API specifically designed for server-side applications.

## Migration Steps

### 1. Environment Setup

Add the following variables to your `.env` file:

```
MAILGUN_DOMAIN=your-domain.mailgun.org
MAILGUN_SECRET=your-secret
MAILGUN_FROM_EMAIL=noreply@your-domain.com
MAILGUN_FROM_NAME="Resume System"
```

Replace `your-domain.mailgun.org` with your actual Mailgun domain.

### 2. Verify Your Domain

1. Log in to your Mailgun account
2. Navigate to the "Domains" section
3. Click "Add New Domain" if you haven't set one up
4. Follow the DNS verification process

### 3. Verify Recipients (Sandbox Mode)

If you're using a Mailgun sandbox domain for testing:

1. Log in to your Mailgun account
2. Navigate to the "Domains" section
3. Select your sandbox domain
4. Add authorized recipients (required for sandbox domains)

### 4. Testing

After deployment, test all email-sending functionality:

- Password resets
- Account status updates
- Organizer applications
- Account deletion notifications

## Technical Implementation Details

The migration involved:

1. Creating a new `MailgunService` class 
2. Updating controller dependencies to use the new service
3. Configuring Mailgun credentials in `services.php`
4. Updating the AppServiceProvider to register the service

All email functionality remains the same from a user perspective, only the underlying delivery mechanism has changed. 
