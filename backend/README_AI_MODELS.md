# AI Models Integration Guide

This project supports multiple AI model providers for generating educational content, quizzes, flashcards, and chat responses. Currently, the following providers are supported:

1. **Mistral AI** (via OpenAI-compatible API)
2. **Google Vertex AI** (Gemini 1.0 Pro)

## File Structure

- `mistral_utils.py` - Original implementation using Mistral AI
- `gemini_vertex_utils.py` - Implementation using Google Vertex AI with Gemini 1.0 Pro
- `gemini_utils.py` - Utility functions for Gemini models
- `enhanced_openai_utils.py` - Enhanced utilities using Gemini models

## Important: Dependency Conflicts

There are known dependency conflicts between Google Vertex AI libraries and FastAPI/other packages. If you encounter errors like:

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
fastapi 0.104.1 requires anyio<4.0.0,>=3.7.1, but you have anyio 4.9.0 which is incompatible.
```

### Fix Scripts

We've provided multiple options to fix these dependency issues:

#### Windows Users:
1. Double-click `fix_dependencies.bat`
2. Choose between:
   - Option 1: Standard fix (tries to maintain version ranges)
   - Option 2: Alternative fix (uses specific older versions)

#### Linux/Mac Users:
1. Make the script executable: `chmod +x fix_dependencies.sh`
2. Run: `./fix_dependencies.sh`
3. Choose between the standard or alternative fix

#### Manual Fix:
If the automated scripts don't work, you can try these manual steps:

1. Uninstall conflicting packages:
   ```
   pip uninstall -y anyio httpx httpcore websockets h11 vertexai google-cloud-aiplatform
   ```

2. Install FastAPI dependencies with specific versions:
   ```
   pip install fastapi==0.95.2 uvicorn==0.22.0 anyio==3.7.1 httpx==0.24.1
   ```

3. Install Google Cloud libraries with specific versions:
   ```
   pip install google-cloud-aiplatform==1.36.4
   pip install "vertexai @ https://files.pythonhosted.org/packages/a8/a4/1f9a27dbe8d1a52b818b1e28c2a5cd1e6c8a1f0d1cbe1e8c8ab2a76d2e0c/vertexai-0.0.1-py2.py3-none-any.whl"
   ```

## Setting Up Mistral AI

### Prerequisites

1. A Mistral AI account
2. A Mistral API key

### Environment Setup

Set the following environment variable:

```bash
export MISTRAL_API_KEY="your-mistral-api-key"
```

For Windows:

```cmd
set MISTRAL_API_KEY=your-mistral-api-key
```

### Dependencies

```bash
pip install openai>=1.0.0
```

## Setting Up Google Vertex AI with Gemini

### Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCP project with billing enabled
3. Vertex AI API enabled in your project
4. A service account with Vertex AI User role

### Environment Setup

Set the following environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # Optional, defaults to us-central1
```

For Windows:

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json
set GOOGLE_CLOUD_PROJECT=your-project-id
set GOOGLE_CLOUD_LOCATION=us-central1
```

### Dependencies

If you're using the standard fix:
```bash
pip install google-cloud-aiplatform>=1.36.0,<1.100.0 vertexai>=0.0.1,<1.40.0
```

If you're using the alternative fix:
```bash
pip install google-cloud-aiplatform==1.36.4
pip install "vertexai @ https://files.pythonhosted.org/packages/a8/a4/1f9a27dbe8d1a52b818b1e28c2a5cd1e6c8a1f0d1cbe1e8c8ab2a76d2e0c/vertexai-0.0.1-py2.py3-none-any.whl"
```

## Usage Examples

### Using Mistral AI

```python
from mistral_utils import mistral_chat, mistral_generate_suggestions

# Generate educational suggestions
suggestions = await mistral_generate_suggestions("Transcript text here...")

# Chat with Mistral
response = await mistral_chat("What is photosynthesis?")
```

### Using Google Vertex AI (Gemini)

```python
from gemini_vertex_utils import gemini_chat, gemini_generate_suggestions

# Generate educational suggestions
suggestions = await gemini_generate_suggestions("Transcript text here...")

# Chat with Gemini
response = await gemini_chat("What is photosynthesis?")
```

## Testing

You can test the Gemini implementation using the provided test script:

```bash
python test_gemini.py
```

## Switching Between Providers

Both implementations maintain the same function signatures for backward compatibility. If you want to switch from Mistral to Gemini, you can:

1. Update your imports to use the Gemini functions instead
2. Set up the required environment variables for Google Vertex AI
3. Update any function calls to use the Gemini equivalents

## Performance Considerations

- **Mistral AI**: Generally faster response times, lower latency
- **Google Vertex AI (Gemini)**: More advanced capabilities, potentially higher quality responses

## Troubleshooting

### Mistral API Issues

- Check that your API key is valid and correctly set
- Ensure you have sufficient credits in your Mistral account
- Check for rate limiting issues

### Google Vertex AI Issues

- Verify that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to a valid service account key file
- Ensure your service account has the "Vertex AI User" role
- Check that the Vertex AI API is enabled in your project
- Verify that Gemini models are available in your selected region
- Try the alternative fix script if you're having dependency issues

## Additional Resources

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [Google Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini) 