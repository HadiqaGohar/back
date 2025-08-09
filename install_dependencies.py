#!/usr/bin/env python3
"""
Install additional dependencies for enhanced chatbot
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required packages"""
    print("🚀 Installing enhanced chatbot dependencies...")
    
    packages = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0", 
        "googlesearch-python>=1.2.3",
        "validators>=0.22.0",
        "aiohttp>=3.9.0",
        "langdetect>=1.0.9"
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{total_packages} packages")
    
    if success_count == total_packages:
        print("🎉 All dependencies installed successfully!")
        print("\n🔧 Next steps:")
        print("1. Make sure your .env file has GEMINI_API_KEY set")
        print("2. Start the backend server: python main.py")
        print("3. Start the frontend: npm run dev (in hg-resume-craft folder)")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())