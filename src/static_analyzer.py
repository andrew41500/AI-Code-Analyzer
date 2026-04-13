"""
Static Code Analysis Module using Pylint

This module integrates pylint to perform static analysis on Python code
and formats the results for integration with the AI review system.
"""

import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Tuple
import json


class StaticAnalyzer:
    """
    Handles static code analysis using pylint.
    
    Analyzes Python code for style issues, potential bugs, and code quality metrics.
    """
    
    def __init__(self):
        """Initialize the static analyzer."""
        self.pylint_config = {
            'disable': ['missing-module-docstring', 'missing-class-docstring'],
            'max-line-length': 120,
        }
    
    def analyze_code(self, code: str, filename: str = "temp_code.py") -> Dict:
        """
        Analyze Python code using pylint.
        
        Args:
            code: The Python code string to analyze
            filename: Optional filename for context (default: "temp_code.py")
            
        Returns:
            Dictionary containing:
                - score: Pylint score (0-10)
                - issues: List of issues found
                - categories: Issues grouped by category
                - raw_output: Raw pylint output
        """
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Run pylint with JSON output using python -m pylint
            # This ensures we use the same Python interpreter and pylint installation
            result = subprocess.run(
                [sys.executable, '-m', 'pylint', '--output-format=json', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Also run pylint in text mode to get the score (pylint doesn't include score in JSON)
            score_result = subprocess.run(
                [sys.executable, '-m', 'pylint', '--score=y', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output for issues
            issues = []
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Fallback: parse text output if JSON fails
                    issues = self._parse_text_output(result.stdout)
            
            # Extract score from text output
            pylint_score = None
            import re
            if score_result.stdout:
                # Look for score pattern like "Your code has been rated at 7.00/10"
                score_match = re.search(r'rated at ([\d.]+)/10', score_result.stdout)
                if score_match:
                    pylint_score = float(score_match.group(1))
            
            # Use pylint's calculated score if available, otherwise calculate our own
            if pylint_score is not None:
                score = pylint_score
            else:
                score = self._calculate_score(issues)
            
            # Group issues by category
            categories = self._group_by_category(issues)
            
            # Note: pylint exits with non‑zero codes when it finds issues, which is
            # expected and should NOT be treated as a fatal error for our UI.
            return {
                'score': score,
                'issues': issues,
                'categories': categories,
                'raw_output': result.stdout + result.stderr,
                'error': False,
            }
            
        except subprocess.TimeoutExpired:
            return {
                'score': 0.0,
                'issues': [],
                'categories': {},
                'raw_output': 'Pylint analysis timed out',
                'error': True
            }
        except FileNotFoundError:
            return {
                'score': 0.0,
                'issues': [],
                'categories': {},
                'raw_output': 'Pylint not found. Please install pylint: pip install pylint',
                'error': True
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def _calculate_score(self, issues: List[Dict]) -> float:
        """
        Calculate pylint score from issues.
        
        Pylint uses a scoring system where:
        - 10.0 is perfect
        - Each issue reduces the score
        - Score = 10 - (total_issues * penalty)
        
        Args:
            issues: List of pylint issue dictionaries
            
        Returns:
            Score between 0.0 and 10.0
        """
        if not issues:
            return 10.0
        
        # Count issues by type
        error_count = sum(1 for issue in issues if issue.get('type') == 'error')
        warning_count = sum(1 for issue in issues if issue.get('type') == 'warning')
        refactor_count = sum(1 for issue in issues if issue.get('type') == 'refactor')
        convention_count = sum(1 for issue in issues if issue.get('type') == 'convention')
        
        # Calculate score using pylint's actual scoring formula
        # Pylint uses: score = 10.0 - (penalty / number_of_statements)
        # But since we don't have statement count, we use a simplified version:
        # Errors: -10 points each, Warnings: -2 points each, Refactor: -2 points each, Convention: -1 point each
        # Then normalize to 0-10 scale
        penalty = (error_count * 10.0) + (warning_count * 2.0) + (refactor_count * 2.0) + (convention_count * 1.0)
        
        # Pylint's actual formula is more complex, but this approximation works better
        # We divide by a factor to get reasonable scores
        # With this formula: 1 error = -10 points, so score would be 0
        # But we want errors to reduce score significantly but not to 0 immediately
        # So we use: score = max(0.0, 10.0 - (penalty / max(1, total_issues)))
        total_issues = len(issues)
        if total_issues == 0:
            return 10.0
        
        # More accurate scoring: errors are severe, others are less severe
        # Scale: 1 error = -2.0 points, 1 warning = -0.4 points, etc.
        score = max(0.0, 10.0 - (penalty / 5.0))
        
        return round(score, 2)
    
    def _group_by_category(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group issues by their category/type.
        
        List of pylint issue dictionaries
            
        Returns:
            Dictionary with categories as keys and lists of issues as values
        """
        categories = {
            'error': [],
            'warning': [],
            'refactor': [],
            'convention': [],
            'info': []
        }
        
        for issue in issues:
            issue_type = issue.get('type', 'info').lower()
            if issue_type in categories:
                categories[issue_type].append(issue)
            else:
                categories['info'].append(issue)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _parse_text_output(self, output: str) -> List[Dict]:
        """
        Fallback parser for pylint text output.
        
        Args:
            output: Raw pylint text output
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        lines = output.split('\n')
        
        for line in lines:
            if ':' in line and any(char.isdigit() for char in line):
                # Try to parse pylint text format
                parts = line.split(':')
                if len(parts) >= 3:
                    issues.append({
                        'type': 'warning',
                        'message': line,
                        'line': 0,
                        'column': 0
                    })
        
        return issues
    
    def format_report(self, analysis_result: Dict) -> str:
        """
        Format analysis results as a readable report.
        
        Args:
            analysis_result: Result dictionary from analyze_code()
            
        Returns:
            Formatted markdown report string
        """
        report = []
        report.append("## Static Analysis Report (Pylint)\n")
        report.append(f"**Score: {analysis_result['score']}/10.0**\n")
        
        if analysis_result.get('error'):
            report.append(f"\n⚠️ **Error:** {analysis_result['raw_output']}\n")
            return "\n".join(report)
        
        categories = analysis_result.get('categories', {})
        total_issues = len(analysis_result.get('issues', []))
        
        report.append(f"\n**Total Issues Found: {total_issues}**\n")
        
        if total_issues == 0:
            report.append("\n✅ No issues found! Code passes all static checks.\n")
        else:
            # Report by category
            for category, issues in categories.items():
                if issues:
                    report.append(f"\n### {category.upper()} ({len(issues)} issues)\n")
                    for issue in issues[:10]:  # Limit to first 10 per category
                        line = issue.get('line', '?')
                        message = issue.get('message', 'Unknown issue')
                        symbol = issue.get('symbol', '')
                        report.append(f"- **Line {line}** ({symbol}): {message}")
                    if len(issues) > 10:
                        report.append(f"- ... and {len(issues) - 10} more issues")
        
        return "\n".join(report)


