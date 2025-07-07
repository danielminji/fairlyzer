<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Analyzer API</title>
    <style>
        body {
            font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            border-bottom: 1px solid #eaeaea;
            padding-bottom: 10px;
            color: #2563eb;
        }
        h2 {
            margin-top: 30px;
            color: #4b5563;
        }
        .endpoint {
            background-color: #f9fafb;
            border-left: 4px solid #2563eb;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }
        .method {
            font-weight: bold;
            color: #059669;
        }
        .path {
            font-family: monospace;
            background-color: #e5e7eb;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .note {
            background-color: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.9rem;
            color: #6b7280;
            border-top: 1px solid #eaeaea;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Resume Analyzer & Booth Recommendations API</h1>
    <p>This is the API backend for the Resume Analyzer & Booth Recommendations system. The frontend is built with Streamlit.</p>
    
    <div class="note">
        <strong>Note:</strong> This page is meant for developers. End users should access the frontend at <a href="http://localhost:8501">http://localhost:8501</a>
    </div>
    
    <h2>Authentication Endpoints</h2>
    <div class="endpoint">
        <span class="method">POST</span> <span class="path">/api/register</span> - Register a new user
    </div>
    <div class="endpoint">
        <span class="method">POST</span> <span class="path">/api/login</span> - Login and get authentication token
    </div>
    <div class="endpoint">
        <span class="method">POST</span> <span class="path">/api/logout</span> - Logout (requires authentication)
    </div>
    
    <h2>Resume Endpoints</h2>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/resumes</span> - Get all user's resumes (requires authentication)
    </div>
    <div class="endpoint">
        <span class="method">POST</span> <span class="path">/api/resumes</span> - Upload a new resume (requires authentication)
    </div>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/resumes/{id}</span> - Get resume details (requires authentication)
    </div>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/resumes/{id}/analysis</span> - Get resume analysis (requires authentication)
    </div>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/resumes/{id}/recommendations</span> - Get booth recommendations (requires authentication)
    </div>
    
    <h2>Booth Endpoints</h2>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/booths</span> - Get all booths (requires authentication)
    </div>
    <div class="endpoint">
        <span class="method">GET</span> <span class="path">/api/booths/{id}</span> - Get booth details (requires authentication)
    </div>
    
    <div class="footer">
        &copy; {{ date('Y') }} Resume Analyzer & Booth Recommendations System<br>
        <small>Laravel API + Streamlit Frontend</small>
    </div>
</body>
</html> 