# Deploying to Vercel

This guide will help you deploy your Flask application to Vercel using the Vercel CLI.

## Prerequisites

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

## Deployment Steps

### 1. Set Environment Variables

Before deploying, you need to set your environment variables in Vercel:

**Option A: Using Vercel CLI**
```bash
vercel env add GEMINI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
```

**Option B: Using Vercel Dashboard**
1. Go to your project on [vercel.com](https://vercel.com)
2. Navigate to Settings → Environment Variables
3. Add the following variables:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon/service key

### 2. Deploy to Vercel

**First Deployment:**
```bash
vercel
```
Follow the prompts to link your project.

**Production Deployment:**
```bash
vercel --prod
```

**Preview Deployment:**
```bash
vercel
```

### 3. Important Notes

#### File Size Limits
- Vercel has a **50MB limit** for serverless functions
- Your `model.pkl` and `label_encoder.pkl` files must be under this limit
- If your model files are too large, consider:
  - Using Vercel's larger function size (requires Pro plan)
  - Hosting models on external storage (S3, etc.) and loading them at runtime
  - Using model compression techniques

#### Static Files
- Static files in the `static/` folder will be automatically served
- Templates in the `templates/` folder will be included in the deployment

#### Runtime Considerations
- Cold starts: First request after inactivity may be slower
- Timeout: Functions have a 10-second timeout on Hobby plan, 60 seconds on Pro
- Memory: Default is 1024MB, can be increased on Pro plan

### 4. Troubleshooting

**If deployment fails:**
1. Check that all dependencies are in `requirements.txt`
2. Verify Python version compatibility (currently set to 3.11 in vercel.json)
3. Check Vercel build logs for specific errors

**If app doesn't work after deployment:**
1. Verify environment variables are set correctly
2. Check that model files (`model.pkl`, `label_encoder.pkl`) are included
3. Review function logs in Vercel dashboard

### 5. Updating Your Deployment

After making changes:
```bash
vercel --prod
```

Or use Git integration:
- Connect your GitHub/GitLab repository to Vercel
- Automatic deployments on every push to main branch

## Alternative: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Configure build settings (usually auto-detected)
5. Add environment variables
6. Deploy!

## Support

For more information, visit:
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)

