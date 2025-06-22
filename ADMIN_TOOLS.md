# Admin Tools Documentation

## Overview

The Resume Analyzer system provides a streamlined admin interface for managing users, approving organizers, and monitoring system status. This document explains the available admin tools and how to use them.

## Admin Portal Home

The Admin Portal Home (accessible at `/admin_home`) serves as the central dashboard for all admin functions. From here, you can:

- Monitor system status (API, user management, email)
- Access all admin functions through a card-based interface
- View critical alerts and pending actions

## User Management System

The unified User Management system (accessible at `/admin_user_management`) provides a single interface for all user-related administrative tasks.

### Features:

1. **All Users Tab**
   - View and manage all users in the system
   - Search and filter by name, email, or role
   - Edit user information, reset passwords, and manage account status

2. **Pending Organizers Tab**
   - Review and approve/reject organizer registration requests
   - View organizer details before making approval decisions
   - Quick approval buttons for efficient processing

3. **Approved Organizers Tab**
   - Monitor all approved organizers
   - Manage organizer status and permissions
   - Edit organizer details as needed

4. **Job Seekers Tab**
   - Manage regular users (job seekers)
   - Filter and search for specific users
   - Update permissions and status

### User Actions:

For each user, you can:
- Change user role (user, organizer, admin)
- Toggle account status (active/inactive)
- Reset user password
- Delete user account (with confirmation)

## System Status

The Admin Portal includes real-time system status indicators:

- API Connection: Verifies the connection to the backend API
- User Management: Checks if the user system is functioning properly
- Email System: Verifies email configuration for notifications

## Access Control

Only users with admin privileges can access these tools. The system implements multiple layers of security:

1. Session-based authentication checks
2. Role-based authorization
3. API middleware protection for backend endpoints

## Best Practices

1. **Regular Monitoring**: Check the admin portal regularly for pending organizer approvals.
2. **Use Search Functions**: When managing a large number of users, utilize the search and filter capabilities.
3. **Password Security**: When resetting passwords, ensure they meet the minimum security requirements (8+ characters).
4. **Careful Deletion**: User deletion cannot be undone - use with caution.

## Getting Started

1. Log in with your admin account
2. Navigate to the Admin Portal Home (`/admin_home`)
3. Use the card interface to access the different admin functions
4. For organizer approvals, click "Manage Organizer Approvals" to go directly to the pending approvals tab 