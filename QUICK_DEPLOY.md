# Quick Vercel CLI Deployment Guide

## Option 1: Use the Deployment Script (Easiest)

### Windows (PowerShell):
```powershell
.\deploy_vercel.ps1
```

### Windows (Command Prompt):
```cmd
deploy_vercel.bat
```

The script will:
- Check if Vercel CLI is installed (install if needed)
- Check if you're logged in (prompt login if needed)
- Deploy your app to production

---

## Option 2: Manual CLI Deployment

### Step 1: Install Vercel CLI (if not installed)
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```
This will open your browser to authenticate.

### Step 3: Set Environment Variables (Important!)

Before deploying, set your environment variables:

```bash
# Set GEMINI_API_KEY
vercel env add GEMINI_API_KEY production

# Set SUPABASE_URL
vercel env add SUPABASE_URL production

# Set SUPABASE_KEY
vercel env add SUPABASE_KEY production
```

For each command, you'll be prompted to enter the value.

**Or set all at once:**
```bash
vercel env add GEMINI_API_KEY production
# Enter your API key when prompted

vercel env add SUPABASE_URL production
# Enter your Supabase URL when prompted

vercel env add SUPABASE_KEY production
# Enter your Supabase key when prompted
```

### Step 4: Deploy to Production

```bash
vercel --prod
```

**For preview deployment (testing):**
```bash
vercel
```

---

## Step-by-Step Commands (Copy & Paste)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Set environment variables (you'll be prompted for values)
vercel env add GEMINI_API_KEY production
vercel env add SUPABASE_URL production
vercel env add SUPABASE_KEY production

# 4. Deploy to production
vercel --prod
```

---

## What Happens During Deployment?

1. **First time**: Vercel will ask you to link your project
   - Choose your Vercel account
   - Choose to link to existing project or create new
   - Follow the prompts

2. **Subsequent deployments**: Just runs `vercel --prod` and it deploys

3. **After deployment**: You'll get a URL like:
   - `https://your-project-name.vercel.app`

---

## Troubleshooting

### "vercel: command not found"
- Install Node.js from https://nodejs.org/
- Then run: `npm install -g vercel`

### "Authentication failed"
- Run: `vercel login` again
- Make sure you have a Vercel account at https://vercel.com

### "Build failed"
- Check that all files are present (model.pkl, label_encoder.pkl)
- Verify requirements.txt has all dependencies
- Check the build logs in Vercel dashboard

### "Function timeout"
- Your model files might be too large
- Consider upgrading to Vercel Pro plan for larger limits
- Or optimize your model files

---

## Environment Variables Reminder

Make sure these are set in Vercel:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `SUPABASE_URL` - Your Supabase project URL  
- `SUPABASE_KEY` - Your Supabase anon/service key

You can also set them via Vercel dashboard:
1. Go to https://vercel.com
2. Select your project
3. Settings → Environment Variables
4. Add each variable

---

## Quick Commands Reference

```bash
# Deploy to production
vercel --prod

# Deploy preview (for testing)
vercel

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel remove
```

