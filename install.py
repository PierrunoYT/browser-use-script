#!/usr/bin/env python3
"""
Installation script for Browser Use CLI

This script helps users set up the browser-use CLI tool with all dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("❗ Browser-use requires Python 3.11 or higher")
        return False


def install_dependencies():
    """Install Python dependencies"""
    commands = [
        ("pip install -r requirements.txt", "Installing Python dependencies"),
        ("playwright install chromium --with-deps --no-shell", "Installing Playwright browser")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def setup_environment():
    """Set up environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        try:
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from .env.example")
            print("❗ Please edit .env file with your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example file not found")
        return False


def main():
    """Main installation function"""
    print("🚀 Browser Use CLI Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Installation failed during dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Installation failed during environment setup")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Run 'python main.py' to start the interactive CLI")
    print("3. Or run 'python simple_example.py' for a basic example")
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    main()
