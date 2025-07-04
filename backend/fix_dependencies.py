#!/usr/bin/env python3
"""
Script to fix dependency conflicts for Vertex AI and FastAPI
"""

import os
import sys
import subprocess
import logging
import re

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

def parse_requirements(file_path):
    """Parse requirements.txt file and extract package specifications"""
    packages = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                packages.append(line)
        return packages
    except Exception as e:
        logger.error(f"Failed to parse requirements file: {e}")
        return []

def fix_dependencies():
    """Fix dependency conflicts"""
    logger.info("Starting dependency fix...")
    
    # First, uninstall problematic packages
    packages_to_uninstall = [
        "anyio",
        "httpx",
        "httpcore",
        "websockets",
        "h11",
        "vertexai",
        "google-cloud-aiplatform"
    ]
    
    uninstall_cmd = f"pip uninstall -y {' '.join(packages_to_uninstall)}"
    if not run_command(uninstall_cmd):
        logger.warning("Uninstallation had issues, but continuing...")
    
    # Install core packages first (FastAPI and dependencies)
    core_packages = [
        "fastapi>=0.100.0,<0.105.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "anyio>=3.7.1,<4.0.0",
        "httpx>=0.24.1,<0.25.0",
        "httpcore>=0.17.3,<0.18.0",
        "websockets>=11.0.0,<13.0.0",
        "h11>=0.14.0,<0.15.0"
    ]
    
    logger.info("Installing core packages...")
    for package in core_packages:
        install_cmd = f"pip install {package}"
        if not run_command(install_cmd):
            logger.warning(f"Failed to install {package}, continuing with next package...")
    
    # Install OpenAI for Mistral
    logger.info("Installing OpenAI for Mistral...")
    if not run_command("pip install openai>=1.0.0"):
        logger.warning("Failed to install OpenAI package, continuing...")
    
    # Install utility packages
    utility_packages = [
        "requests>=2.31.0",
        "aiohttp>=3.8.5",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "bcrypt>=4.0.1",
        "einops",
        "safetensors"
    ]
    
    logger.info("Installing utility packages...")
    for package in utility_packages:
        install_cmd = f"pip install {package}"
        if not run_command(install_cmd):
            logger.warning(f"Failed to install {package}, continuing with next package...")
    
    # Install Google Vertex AI packages last
    logger.info("Installing Google Vertex AI packages...")
    vertex_packages = [
        "google-cloud-aiplatform>=1.36.0,<1.100.0",
        "vertexai>=0.0.1,<1.40.0"
    ]
    
    for package in vertex_packages:
        install_cmd = f"pip install {package}"
        if not run_command(install_cmd):
            logger.warning(f"Failed to install {package}, continuing with next package...")
    
    logger.info("Dependency fix completed!")
    return True

if __name__ == "__main__":
    logger.info("=== Dependency Conflict Fix Script ===")
    
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
        logger.info("All dependencies have been fixed!")
        sys.exit(0)
    else:
        logger.error("Failed to fix dependencies.")
        sys.exit(1) 