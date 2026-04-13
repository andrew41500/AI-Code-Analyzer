#!/usr/bin/env python3
"""
Simple script to review changed Python files using AI Code Reviewer.

This script is called by GitHub Actions to review code changes.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ai_reviewer import AIReviewer
    from src.static_analyzer import StaticAnalyzer
except ImportError as e:
    print(f"## ❌ Error: Failed to import modules\n\n{e}\n")
    print("Make sure all dependencies are installed.")
    sys.exit(1)


def get_changed_files():
    """
    Get list of Python files that changed in this PR or push.
    
    Returns:
        List of file paths
    """
    # Check if we're in a PR or push
    event_name = os.getenv('GITHUB_EVENT_NAME', '')
    base_ref = os.getenv('GITHUB_BASE_REF', '')
    
    if event_name == 'pull_request' and base_ref:
        # For PRs: compare with base branch
        cmd = f"git diff --name-only --diff-filter=ACMR origin/{base_ref}...HEAD"
    else:
        # For pushes: compare with previous commit
        cmd = "git diff --name-only --diff-filter=ACMR HEAD~1 HEAD"
    
    # Run git command to get changed files
    import subprocess
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    if result.returncode != 0:
        # Fallback: just review all Python files in src/ and app.py
        files = list(Path('.').glob('**/*.py'))
        return [str(f) for f in files if f.name != '__init__.py']
    
    # Filter to only Python files
    files = [f.strip() for f in result.stdout.split('\n') if f.strip().endswith('.py')]
    return files


def main():
    """Main function to review changed files."""
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("⚠️ GROQ_API_KEY not set. Skipping AI review.")
        sys.exit(0)
    
    # Get changed files
    files = get_changed_files()
    
    if not files:
        print("No Python files to review.")
        sys.exit(0)
    
    print(f"Reviewing {len(files)} file(s):\n")
    
    # Initialize reviewers
    try:
        reviewer = AIReviewer(api_key=api_key)
        analyzer = StaticAnalyzer()
    except Exception as e:
        print(f"## ❌ Error: Failed to initialize reviewers\n\n{e}\n")
        sys.exit(1)
    
    # Review each file
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}\n")
            continue
        
        print(f"### 📄 {file_path}\n")
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Run static analysis
            static_result = analyzer.analyze_code(code, file_path)
            
            # Run AI review
            ai_result = reviewer.review_code(code, static_analysis=static_result)
            
            # Print results
            print(ai_result['review'])
            print("\n---\n")
            
        except Exception as e:
            print(f"❌ Error reviewing {file_path}: {e}\n")
            continue


if __name__ == '__main__':
    main()

