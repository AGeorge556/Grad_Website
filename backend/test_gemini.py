#!/usr/bin/env python3
"""
Test script for Gemini 1.0 Pro integration
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    missing_vars = []
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        missing_vars.append("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        missing_vars.append("GOOGLE_CLOUD_PROJECT")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables before running the test.")
        return False
    
    return True

def test_gemini_simple():
    """Test basic Gemini functionality"""
    try:
        from google.cloud.aiplatform import VertexAI
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        logger.info(f"Initializing Vertex AI with project: {project_id}, location: {location}")
        VertexAI(project=project_id, location=location)
        
        # Create a model instance
        logger.info("Creating Gemini model instance")
        model = GenerativeModel("gemini-1.0-pro")
        
        # Generate content
        prompt = "Tell me a short joke about programming"
        logger.info(f"Sending prompt: {prompt}")
        
        response = model.generate_content(prompt)
        
        logger.info("Response received successfully!")
        print("\n--- Gemini Response ---")
        print(response.text)
        print("----------------------\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Gemini: {str(e)}")
        return False

def test_gemini_chat():
    """Test Gemini chat functionality"""
    try:
        from google.cloud.aiplatform import VertexAI
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        logger.info(f"Initializing Vertex AI with project: {project_id}, location: {location}")
        VertexAI(project=project_id, location=location)
        
        # Create a model instance
        logger.info("Creating Gemini chat session")
        model = GenerativeModel("gemini-1.0-pro")
        chat = model.start_chat(system_instruction="You are a helpful AI assistant specialized in programming.")
        
        # Send a message
        prompt = "What are the key differences between Python and JavaScript?"
        logger.info(f"Sending chat message: {prompt}")
        
        response = chat.send_message(prompt)
        
        logger.info("Chat response received successfully!")
        print("\n--- Gemini Chat Response ---")
        print(response.text)
        print("----------------------------\n")
        
        # Send a follow-up message
        follow_up = "Can you give me a simple example of each language printing 'Hello World'?"
        logger.info(f"Sending follow-up: {follow_up}")
        
        response = chat.send_message(follow_up)
        
        logger.info("Follow-up response received successfully!")
        print("\n--- Gemini Follow-up Response ---")
        print(response.text)
        print("--------------------------------\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Gemini chat: {str(e)}")
        return False

def test_gemini_utils():
    """Test our Gemini utilities"""
    try:
        from gemini_utils import generate_response
        
        logger.info("Testing generate_response utility function")
        
        # Test with system prompt
        system_prompt = "You are a helpful AI assistant specialized in programming."
        user_prompt = "Explain what a decorator is in Python in one sentence."
        
        logger.info(f"Sending prompt with system instruction")
        response = generate_response(user_prompt, system_prompt)
        
        logger.info("Response received successfully!")
        print("\n--- Gemini Utils Response (with system prompt) ---")
        print(response)
        print("------------------------------------------------\n")
        
        # Test without system prompt
        logger.info(f"Sending prompt without system instruction")
        response = generate_response("What is the capital of France?")
        
        logger.info("Response received successfully!")
        print("\n--- Gemini Utils Response (without system prompt) ---")
        print(response)
        print("---------------------------------------------------\n")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Gemini utils: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Gemini 1.0 Pro Integration Test ===\n")
    
    if not check_environment():
        sys.exit(1)
    
    success = True
    
    print("\n1. Testing basic Gemini functionality...")
    if not test_gemini_simple():
        success = False
    
    print("\n2. Testing Gemini chat functionality...")
    if not test_gemini_chat():
        success = False
    
    print("\n3. Testing Gemini utilities...")
    try:
        if not test_gemini_utils():
            success = False
    except ImportError:
        logger.warning("Could not import gemini_utils. Skipping utility test.")
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
        sys.exit(1) 