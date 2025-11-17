# Gemini API Setup Guide

## How to Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy your API key

## How to Set Up the API Key

### Option 1: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Option 2: Create a .env file

Create a file named `.env` in the project root with:
```
GEMINI_API_KEY=your_api_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And update app.py to load from .env:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Install Required Packages

```bash
pip install -r requirements.txt
```

## Features

Once the API key is configured, the application will automatically:
- Show recommended diagnostic tests for the predicted disease
- Indicate if medical emergency attention is required
- Display common symptoms and their descriptions

The AI information will appear below the main prediction result.

