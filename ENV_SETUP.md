# Environment Variables Setup Guide

## Security Notice

**IMPORTANT**: API keys and other sensitive credentials have been exposed in the Git history. You should:

1. Regenerate all exposed API keys immediately
2. For Supabase: Visit your Supabase dashboard and regenerate your project API keys
3. For OpenAI: Revoke and regenerate your API key from the OpenAI dashboard

## Setup Instructions

### Backend Setup

1. Copy the template file to create your actual environment file:
   ```
   cp backend/.env.template backend/.env
   ```

2. Edit `backend/.env` and fill in your actual API keys:
   ```
   SUPABASE_URL=your_new_supabase_url
   SUPABASE_SERVICE_KEY=your_new_supabase_service_key
   OPENAI_API_KEY=your_new_openai_api_key
   ```

### Frontend Setup

1. Copy the template file to create your actual environment file:
   ```
   cp .env.template .env
   ```

2. Edit `.env` and fill in your actual API keys:
   ```
   VITE_SUPABASE_URL=your_new_supabase_url
   VITE_SUPABASE_ANON_KEY=your_new_supabase_anon_key
   ```

## Best Practices

- Never commit `.env` files to Git repositories
- Regularly rotate your API keys
- Use different API keys for development and production
- Consider using a secrets management service for production environments