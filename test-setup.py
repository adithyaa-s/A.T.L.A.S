#!/usr/bin/env python3
"""
Quick test to verify Docker setup before deploying
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - NOT FOUND at {path}")
        return False

def check_content(path, keywords, description):
    """Check if file contains expected content"""
    try:
        with open(path, 'r') as f:
            content = f.read().lower()
            if all(keyword.lower() in content for keyword in keywords):
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - Missing keywords")
                return False
    except Exception as e:
        print(f"✗ {description} - Error: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("ATLAS Docker Setup Verification")
    print("=" * 60)
    print()
    
    root = Path(__file__).parent
    checks_passed = 0
    checks_total = 0
    
    # Check Docker files
    print("Docker Files:")
    print("-" * 60)
    
    docker_files = [
        ("Dockerfile", "Dockerfile"),
        ("docker-compose.yml", "Docker Compose config"),
        (".dockerignore", "Docker ignore file"),
        ("entrypoint.sh", "Entry point script"),
    ]
    
    for file, desc in docker_files:
        checks_total += 1
        if check_file_exists(root / file, desc):
            checks_passed += 1
    
    print()
    
    # Check configuration files
    print("Configuration Files:")
    print("-" * 60)
    
    config_files = [
        ("requirements.txt", "Python requirements"),
        ("render.yaml", "Render deployment config"),
        (".env.production", "Production env template"),
    ]
    
    for file, desc in config_files:
        checks_total += 1
        if check_file_exists(root / file, desc):
            checks_passed += 1
    
    print()
    
    # Check documentation
    print("Documentation:")
    print("-" * 60)
    
    docs = [
        ("DEPLOYMENT.md", "Deployment guide"),
        ("QUICKSTART.md", "Quick start guide"),
        ("DEPLOYMENT_CHECKLIST.md", "Deployment checklist"),
        ("CONTAINERIZATION_COMPLETE.md", "Completion summary"),
        ("DOCKER_AND_RENDER_INDEX.md", "Index and navigation"),
    ]
    
    for file, desc in docs:
        checks_total += 1
        if check_file_exists(root / file, desc):
            checks_passed += 1
    
    print()
    
    # Check CI/CD
    print("CI/CD Configuration:")
    print("-" * 60)
    
    checks_total += 1
    if check_file_exists(root / ".github" / "workflows" / "docker-build.yml", "GitHub Actions workflow"):
        checks_passed += 1
    
    print()
    
    # Check file contents
    print("Content Verification:")
    print("-" * 60)
    
    content_checks = [
        (root / "Dockerfile", ["python", "node", "node.js", "npm", "alpine", "slim"], "Dockerfile contains Python and Node"),
        (root / "requirements.txt", ["google", "auth", "dotenv"], "requirements.txt has Google libraries"),
        (root / "render.yaml", ["type", "web", "docker", "env"], "render.yaml has proper structure"),
        (root / "entrypoint.sh", ["node", "python", "echo"], "entrypoint.sh has startup commands"),
    ]
    
    for path, keywords, desc in content_checks:
        checks_total += 1
        if check_content(path, keywords, desc):
            checks_passed += 1
    
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Checks Passed: {checks_passed}/{checks_total}")
    print()
    
    if checks_passed == checks_total:
        print("✓ All checks passed! ✓")
        print()
        print("Next steps:")
        print("1. Read QUICKSTART.md for deployment instructions")
        print("2. Test locally: docker-compose up --build")
        print("3. Commit to GitHub: git add . && git push")
        print("4. Deploy to Render following QUICKSTART.md")
        print()
        return 0
    else:
        print(f"✗ {checks_total - checks_passed} check(s) failed")
        print()
        print("Please review the errors above and fix any missing files.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
