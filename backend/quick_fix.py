#!/usr/bin/env python3
"""
Quick fix script for the VertexAI import error
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

def quick_fix():
    """Apply a quick fix for the VertexAI import error"""
    logger.info("Starting quick fix for VertexAI import error...")
    
    # Uninstall conflicting packages
    packages_to_uninstall = [
        "vertexai",
        "google-cloud-aiplatform"
    ]
    
    uninstall_cmd = f"pip uninstall -y {' '.join(packages_to_uninstall)}"
    if not run_command(uninstall_cmd):
        logger.warning("Uninstallation had issues, but continuing...")
    
    # Install specific versions known to work
    if not run_command("pip install google-cloud-aiplatform==1.26.1"):
        logger.error("Failed to install google-cloud-aiplatform")
        return False
    
    if not run_command("pip install vertexai==0.0.1"):
        logger.warning("Failed to install vertexai from PyPI, trying direct URL...")
        direct_url = "https://files.pythonhosted.org/packages/a8/a4/1f9a27dbe8d1a52b818b1e28c2a5cd1e6c8a1f0d1cbe1e8c8ab2a76d2e0c/vertexai-0.0.1-py2.py3-none-any.whl"
        if not run_command(f"pip install {direct_url}"):
            logger.error("Failed to install vertexai")
            return False
    
    logger.info("Quick fix completed successfully!")
    
    # Verify the fix
    logger.info("Verifying the fix...")
    verify_script = """
import sys
try:
    from google.cloud import aiplatform
    print("Successfully imported aiplatform")
    from vertexai.generative_models import GenerativeModel
    print("Successfully imported GenerativeModel")
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
"""
    
    with open("verify_imports.py", "w") as f:
        f.write(verify_script)
    
    if run_command("python verify_imports.py"):
        logger.info("Verification successful! The imports are now working.")
    else:
        logger.error("Verification failed. Imports are still not working.")
        return False
    
    # Clean up
    try:
        os.remove("verify_imports.py")
    except:
        pass
    
    return True

if __name__ == "__main__":
    print("=== Quick Fix for VertexAI Import Error ===")
    print()
    print("This script will fix the 'ImportError: cannot import name VertexAI' error")
    print("by installing compatible versions of the Google Cloud libraries.")
    print()
    
    if quick_fix():
        print()
        print("✅ Fix applied successfully!")
        print("You can now run your application without the import error.")
    else:
        print()
        print("❌ Fix failed. Please try the alternative fix scripts:")
        print("   - Windows: fix_dependencies.bat")
        print("   - Linux/Mac: ./fix_dependencies.sh")
        sys.exit(1) 