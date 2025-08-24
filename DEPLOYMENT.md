# 🚀 Deployment Guide

This guide covers deploying your Resume Adapter application securely to Streamlit Cloud and other platforms.

## 🔐 Security Setup (IMPORTANT)

Your API keys are now **secured** and ready for deployment! The application uses environment variables instead of hardcoded values.

### ✅ What's Been Secured:
- ✅ API key removed from `config.json`
- ✅ Environment variables setup in `.env` 
- ✅ `.gitignore` created to exclude sensitive files
- ✅ `python-dotenv` added to requirements

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Secure deployment setup"
   git push origin main
   ```

2. **Set up Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Deploy your app

3. **Configure Secrets in Streamlit Cloud:**
   - In your app dashboard, go to "Settings" → "Secrets"
   - Add your secrets in TOML format:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-actual-api-key-here"
   OPENROUTER_DEFAULT_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
   
   # Rate Limiting (protects your API credits from spam)
   RATE_LIMIT_ENABLED = "true"
   RATE_LIMIT_MAX_REQUESTS = 30
   RATE_LIMIT_TIME_WINDOW = 60
   # RATE_LIMIT_ADMIN_IPS = "1.2.3.4,5.6.7.8"  # Optional: Admin IPs (no limits)
   
   # Optional settings (with defaults shown)
   DEFAULT_PORT = 8501
   AUTO_OPEN_BROWSER = "true"
   OCR_CONFIDENCE_THRESHOLD = 0.5
   MAX_FILE_SIZE_MB = 10
   ```

### Option 2: Heroku

1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
   heroku config:set OPENROUTER_DEFAULT_MODEL=mistralai/mistral-small-3.2-24b-instruct:free
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option 3: Railway

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard:**
   - `OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here`
   - `OPENROUTER_DEFAULT_MODEL=mistralai/mistral-small-3.2-24b-instruct:free`

## 🔧 Configuration Loading Priority

The app automatically detects the environment and loads configuration accordingly:

### 🌐 **Production (Streamlit Cloud):**
1. **`st.secrets`** (Streamlit Cloud secrets - highest priority)

### 💻 **Local Development:**
1. **Environment variables** (highest priority)
2. **`.env` file** (loaded automatically)
3. **`config.json`** (fallback, but API key removed)

### Running Locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Your .env file contains your API key (already created)
# Just run the app
streamlit run app.py
```

## 🛡️ Security Best Practices

### ✅ Done:
- API keys moved to environment variables
- Sensitive files added to `.gitignore`
- `python-dotenv` for local development
- Secure configuration loading
- **Smart environment detection** - automatically uses `st.secrets` on Streamlit Cloud
- **Local/production separation** - different config sources for different environments
- **Smart rate limiting** - IP-based request limits to prevent API abuse
- **Admin controls** - Special admin IPs with unlimited access

## 🛡️ Rate Limiting Protection

Your app now includes **built-in rate limiting** to protect your API credits from spam and abuse:

### 🔒 **Default Protection:**
- **30 requests per hour** per IP address
- **Automatic IP detection** (works with proxies/CDNs)
- **User-friendly error messages** when limits are exceeded
- **Real-time limit display** in the sidebar

### ⚙️ **Customizable via Environment Variables:**
```bash
# Disable rate limiting completely
RATE_LIMIT_ENABLED=false

# Increase limits for high-traffic deployments  
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_TIME_WINDOW=120

# Add admin IPs (no rate limits)
RATE_LIMIT_ADMIN_IPS=203.0.113.1,198.51.100.2
```

### 👑 **Admin Features:**
- **Unlimited requests** for admin IPs
- **Live monitoring** of all IP usage  
- **Reset limits** for specific users
- **Real-time statistics** in sidebar

### 📊 **How It Works:**
1. Each user's IP is tracked automatically
2. Requests are counted per time window
3. When limit is reached, user sees friendly error
4. Limits reset automatically after time window
5. Admin IPs bypass all restrictions

### 📋 Before Deployment Checklist:
- [ ] Verify `.env` is in `.gitignore` 
- [ ] Confirm `config.json` has placeholder API key
- [ ] Test locally with environment variables
- [ ] Set up environment variables in your deployment platform

## 🔄 Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | *Required* | `sk-or-v1-...` |
| `OPENROUTER_DEFAULT_MODEL` | Default AI model | `mistralai/mistral-small-3.2-24b-instruct:free` | `openai/gpt-4o` |
| **Rate Limiting** ||||
| `RATE_LIMIT_ENABLED` | Enable/disable rate limiting | `true` | `false` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per time window | `30` | `50` |
| `RATE_LIMIT_TIME_WINDOW` | Time window in minutes | `60` | `120` |
| `RATE_LIMIT_ADMIN_IPS` | Admin IPs (comma-separated) | *None* | `1.2.3.4,5.6.7.8` |
| **UI Settings** ||||
| `DEFAULT_PORT` | App port | `8501` | `8080` |
| `AUTO_OPEN_BROWSER` | Open browser automatically | `true` | `false` |
| **Processing** ||||
| `OCR_CONFIDENCE_THRESHOLD` | OCR confidence level | `0.5` | `0.8` |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` | `25` |

## 🚨 Emergency: If API Key Gets Exposed

If your API key gets accidentally committed:

1. **Revoke the key immediately** on OpenRouter
2. **Generate a new key** 
3. **Update your environment variables**
4. **Remove the key from git history** (if needed):
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch config.json' \
   --prune-empty --tag-name-filter cat -- --all
   ```

## 📞 Support

If you encounter issues:
- Check that environment variables are set correctly
- Verify the API key is valid and has sufficient credits
- Test locally first before deploying