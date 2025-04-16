# Graduation Project Website

## Environment Setup

This project requires several environment variables to function properly. For security reasons, these are not included in the repository.

**IMPORTANT**: Please refer to the [Environment Variables Setup Guide](ENV_SETUP.md) for detailed instructions on setting up your environment variables and security best practices.

## Getting Started

1. Set up environment variables as described in the [setup guide](ENV_SETUP.md)
2. Install dependencies for the frontend:
   ```
   npm install
   ```
3. Install dependencies for the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```
4. Start the frontend development server:
   ```
   npm run dev
   ```
5. Start the backend server:
   ```
   cd backend
   python main.py
   ```