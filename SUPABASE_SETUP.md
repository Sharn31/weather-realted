# Supabase Setup Guide

This guide will help you set up Supabase to store contact form submissions from the "Get in Touch" page.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Choose a project name (e.g., "Weather Disease Predictor")
   - **Database Password**: Create a strong password (save this securely)
   - **Region**: Choose the region closest to you
5. Click "Create new project" and wait for it to be set up

## Step 2: Get Your Supabase Credentials

1. Once your project is created, go to **Settings** → **API**
2. You'll find:
   - **Project URL**: Copy this (looks like `https://xxxxx.supabase.co`)
   - **anon/public key**: Copy this key (starts with `eyJ...`)

## Step 3: Create the Database Table

1. Go to **Table Editor** in your Supabase dashboard
2. Click **"New Table"**
3. Name the table: `contact_submissions`
4. Add the following columns:

| Column Name | Type | Default Value | Nullable |
|------------|------|---------------|----------|
| id | int8 | auto-increment | No (Primary Key) |
| name | text | - | No |
| email | text | - | No |
| message_type | text | - | No |
| message | text | - | No |
| submitted_at | timestamptz | now() | No |

5. Click **"Save"**

### SQL Alternative (if you prefer SQL):

```sql
CREATE TABLE contact_submissions (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message_type TEXT NOT NULL,
    message TEXT NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow inserts (for the contact form)
CREATE POLICY "Allow public inserts" ON contact_submissions
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy to allow authenticated users to read (optional)
CREATE POLICY "Allow authenticated reads" ON contact_submissions
    FOR SELECT
    TO authenticated
    USING (true);
```

## Step 4: Set Environment Variables

### Option A: Using PowerShell (Windows)

Run the PowerShell script:
```powershell
.\setup_supabase.ps1
```

Or manually set:
```powershell
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-anon-key-here"
```

### Option B: Using Command Prompt (Windows)

```cmd
set SUPABASE_URL=https://your-project-id.supabase.co
set SUPABASE_KEY=your-anon-key-here
```

### Option C: Using .env file (Recommended for production)

Create a `.env` file in your project root:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And update `app.py` to load the .env file:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option D: For Heroku/Production

Set environment variables in your hosting platform:
- Heroku: `heroku config:set SUPABASE_URL=... SUPABASE_KEY=...`
- Other platforms: Use their environment variable settings

## Step 5: Install Dependencies

Make sure you have the Supabase client installed:
```bash
pip install -r requirements.txt
```

## Step 6: Test the Integration

1. Start your Flask application
2. Go to the "Get in Touch" page
3. Fill out and submit the contact form
4. Check your Supabase dashboard → Table Editor → `contact_submissions` table
5. You should see the new submission!

## Troubleshooting

### Issue: "Supabase not configured" warning
- **Solution**: Make sure you've set both `SUPABASE_URL` and `SUPABASE_KEY` environment variables

### Issue: "Failed to save contact form data to Supabase"
- **Solution**: 
  - Check that your table name is exactly `contact_submissions`
  - Verify your Supabase URL and key are correct
  - Check that Row Level Security policies allow inserts
  - Check the application logs for detailed error messages

### Issue: Table doesn't exist
- **Solution**: Make sure you've created the `contact_submissions` table in your Supabase project

## Security Notes

- The `anon` key is safe to use in client-side code, but for server-side use, you might want to use the `service_role` key (keep this secret!)
- Row Level Security (RLS) is recommended for production
- Consider adding rate limiting to prevent spam submissions

## Viewing Submissions

You can view all contact form submissions in your Supabase dashboard:
1. Go to **Table Editor**
2. Select the `contact_submissions` table
3. All submissions will be listed with their details

