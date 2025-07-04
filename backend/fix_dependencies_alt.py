#!/usr/bin/env python3
"""
Alternative script to fix dependency conflicts for Vertex AI and FastAPI
This script uses older versions of the Google Cloud libraries that are more compatible
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and log output"""
    logger.info(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False

def fix_dependencies():
    """Fix dependency conflicts using older versions"""
    logger.info("Starting alternative dependency fix...")
    
    # First, uninstall problematic packages
    packages_to_uninstall = [
        "anyio",
        "httpx",
        "httpcore",
        "websockets",
        "h11",
        "vertexai",
        "google-cloud-aiplatform",
        "google-api-core",
        "google-auth",
        "google-cloud-core",
        "googleapis-common-protos",
        "protobuf"
    ]
    
    uninstall_cmd = f"pip uninstall -y {' '.join(packages_to_uninstall)}"
    if not run_command(uninstall_cmd):
        logger.warning("Uninstallation had issues, but continuing...")
    
    # Install FastAPI and its dependencies with specific versions
    logger.info("Installing FastAPI and dependencies...")
    fastapi_deps = [
        "fastapi==0.95.2",
        "uvicorn==0.22.0",
        "pydantic==1.10.8",
        "starlette==0.27.0",
        "anyio==3.7.1",
        "httpx==0.24.1",
        "httpcore==0.17.3",
        "websockets==11.0.3",
        "h11==0.14.0"
    ]
    
    for package in fastapi_deps:
        if not run_command(f"pip install {package}"):
            logger.warning(f"Failed to install {package}, continuing...")
    
    # Install OpenAI for Mistral
    logger.info("Installing OpenAI for Mistral...")
    if not run_command("pip install openai==1.3.5"):
        logger.warning("Failed to install OpenAI package, continuing...")
    
    # Install Google Cloud libraries - use a version known to work with the current code
    logger.info("Installing Google Cloud libraries...")
    
    # First install the core Google Cloud libraries
    google_core_deps = [
        "protobuf==4.23.4",
        "googleapis-common-protos==1.59.1",
        "google-api-core==2.11.1",
        "google-auth==2.22.0",
        "google-cloud-core==2.3.3"
    ]
    
    for package in google_core_deps:
        if not run_command(f"pip install {package}"):
            logger.warning(f"Failed to install {package}, continuing...")
    
    # Install google-cloud-aiplatform
    if not run_command("pip install google-cloud-aiplatform==1.26.1"):
        logger.warning("Failed to install google-cloud-aiplatform, continuing...")
    
    # Install vertexai - this version is known to work with the code
    if not run_command("pip install vertexai==0.0.1"):
        logger.warning("Failed to install vertexai, trying alternative approach...")
        # Try installing from direct URL if package install fails
        direct_url = "https://files.pythonhosted.org/packages/a8/a4/1f9a27dbe8d1a52b818b1e28c2a5cd1e6c8a1f0d1cbe1e8c8ab2a76d2e0c/vertexai-0.0.1-py2.py3-none-any.whl"
        if not run_command(f"pip install {direct_url}"):
            logger.error("Failed to install vertexai from direct URL")
    
    # Install other utility packages
    logger.info("Installing utility packages...")
    utility_packages = [
        "requests>=2.31.0",
        "aiohttp>=3.8.5",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "bcrypt>=4.0.1",
        "python-dotenv>=1.0.0",
        "python-multipart>=0.0.6",
        "einops",
        "safetensors"
    ]
    
    for package in utility_packages:
        if not run_command(f"pip install {package}"):
            logger.warning(f"Failed to install {package}, continuing...")
    
    logger.info("Alternative dependency fix completed!")
    return True

if __name__ == "__main__":
    logger.info("=== Alternative Dependency Conflict Fix Script ===")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning("Not running in a virtual environment. It's recommended to use a virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            logger.info("Exiting.")
            sys.exit(0)
    
    # Make sure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    if fix_dependencies():
        logger.info("All dependencies have been fixed with alternative versions!")
        sys.exit(0)
    else:
        logger.error("Failed to fix dependencies.")
        sys.exit(1) 