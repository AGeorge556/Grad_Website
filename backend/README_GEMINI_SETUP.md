# Setting Up Google Vertex AI with Gemini 1.0 Pro

This guide will help you set up Google Vertex AI with Gemini 1.0 Pro for your application.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCP project with billing enabled
3. Vertex AI API enabled in your project

## Steps to Set Up

### 1. Create a Google Cloud Project (if you don't have one)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name and select a billing account
5. Click "Create"

### 2. Enable the Vertex AI API

1. Go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Vertex AI API"
3. Click on "Vertex AI API"
4. Click "Enable"

### 3. Create a Service Account and Download Credentials

1. Go to the [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Enter a name for the service account
4. Click "Create and Continue"
5. Add the "Vertex AI User" role
6. Click "Continue" and then "Done"
7. Click on the service account you just created
8. Go to the "Keys" tab
9. Click "Add Key" > "Create new key"
10. Choose JSON as the key type
11. Click "Create" to download the key file

### 4. Set Up Environment Variables

1. Rename the downloaded JSON key file to something like `vertex-ai-credentials.json`
2. Move the file to a secure location on your server
3. Set the following environment variables:

```bash
# Path to your service account key file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/vertex-ai-credentials.json"

# Your Google Cloud project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Optional: Set the location (defaults to us-central1)
export GOOGLE_CLOUD_LOCATION="us-central1"
```

For Windows:

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\vertex-ai-credentials.json
set GOOGLE_CLOUD_PROJECT=your-project-id
set GOOGLE_CLOUD_LOCATION=us-central1
```

### 5. Install Required Dependencies

Install the required Python packages:

```bash
pip install google-cloud-aiplatform vertexai
```

Or use the provided requirements.txt:

```bash
pip install -r requirements.txt
```

## Testing Your Setup

You can test your setup with the following Python code:

```python
import os
from google.cloud.aiplatform import VertexAI
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
VertexAI(project=project_id, location=location)

# Create a model instance
model = GenerativeModel("gemini-1.0-pro")

# Generate content
response = model.generate_content("Tell me a short joke")
print(response.text)
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Verify that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly
2. Check that the service account has the "Vertex AI User" role
3. Ensure the key file is accessible and has the correct permissions

### API Quota Issues

If you hit quota limits:

1. Check your [Vertex AI quotas](https://console.cloud.google.com/iam-admin/quotas)
2. Request an increase if needed

### Region Availability

Ensure that Gemini models are available in your selected region. If not, change the `GOOGLE_CLOUD_LOCATION` to a supported region like `us-central1`.

## Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Google Cloud Authentication Guide](https://cloud.google.com/docs/authentication/getting-started) 