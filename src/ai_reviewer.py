"""
AI Code Reviewer Module using LangChain and Gemini

This module uses LangChain to create an AI agent that reviews Python code
and provides intelligent suggestions for improvement.
"""

import os
from typing import Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIReviewer:
    """
    AI-powered code reviewer using LangChain and Gemini.
    
    Analyzes Python code and provides:
    - Style improvements
    - Potential bugs or vulnerabilities
    - Code refactoring suggestions
    - Documentation recommendations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI reviewer.
        Attempts to use Groq first, falls back to Gemini if Groq fails or key is missing.
        
        Args:
            api_key: User-provided API key (can be Groq or Gemini).
        """
        self.groq_key = api_key or os.getenv('GROQ_API_KEY')
        self.gemini_key = os.getenv('GOOGLE_API_KEY') or api_key
        self.active_provider = "Unknown"
        self.active_model = "Unknown"

        # Try Groq (LLaMA) first
        try:
            model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
            if self.groq_key:
                self.llm = ChatGroq(
                    model=model_name,
                    groq_api_key=self.groq_key,
                    temperature=0.3
                )
                self.active_provider = "Groq"
                self.active_model = model_name
        except Exception:
            # Silently catch to proceed with fallback
            pass

        # Fallback to Gemini-2.5-Flash if Groq initialization didn't happen
        if self.active_provider == "Unknown":
            try:
                gemini_model = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
                if self.gemini_key:
                    self.llm = ChatGoogleGenerativeAI(
                        model=gemini_model,
                        google_api_key=self.gemini_key,
                        temperature=0.3,
                    )
                    self.active_provider = "Gemini"
                    self.active_model = gemini_model
            except Exception:
                # Both failed
                pass

        # If we get here and still no provider, initialization failed
        if self.active_provider == "Unknown":
            if not self.groq_key and not self.gemini_key:
                raise ValueError(
                    "No API keys found. Please set GROQ_API_KEY or GOOGLE_API_KEY."
                )
            else:
                raise ValueError(
                    "Failed to initialize both Groq and Gemini models. "
                    "Please check your API keys and connection."
                )


            
        # Define the review prompt template.
        # IMPORTANT: We use string templates (\"system\" / \"human\") instead of
        # pre‑built Message objects so that {code} and other variables are
        # actually interpolated by LangChain.
        self.review_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert Python code reviewer with deep knowledge of:
- Python best practices and PEP 8 style guidelines
- Common bugs and security vulnerabilities
- Code refactoring techniques
- Documentation standards

Your task is to review exactly and only the Python code that is provided.
Do NOT invent or assume additional files, functions, or modules beyond what
is shown. If the code snippet is very small, still focus your review strictly
on that snippet.

Focus on:
1. Code style and PEP 8 compliance
2. Potential bugs or logical errors
3. Security vulnerabilities
4. Performance improvements
5. Missing documentation (docstrings, comments)
6. Code refactoring opportunities

Be specific, cite line numbers when relevant, and provide code examples for improvements.
Format your response in clear markdown with sections.""",
                ),
                (
                    "human",
                    """Please review the following Python code:

```python
{code}
```

{static_context}

Provide a comprehensive code review with:
1. **Style Issues**: PEP 8 violations, naming conventions, formatting
2. **Potential Bugs**: Logic errors, edge cases, potential runtime errors
3. **Security Concerns**: Input validation, SQL injection risks, etc.
4. **Refactoring Suggestions**: How to improve code structure and maintainability
5. **Documentation**: Missing docstrings, unclear code that needs comments

Your review must reference only the code shown above. 
If you are not sure about something, say that you are not sure instead of inventing code.

Format your response as markdown with clear sections and bullet points.""",
                ),
            ]
        )
    
    def review_code(self, code: str, static_analysis: Optional[Dict] = None) -> Dict[str, str]:
        """
        Review Python code using AI.
        
        Args:
            code: The Python code string to review
            static_analysis: Optional static analysis results to include in context
            
        Returns:
            Dictionary containing:
                - review: AI-generated review text
                - summary: Brief summary of findings
        """
        try:
            # Build optional static‑analysis context string
            static_context = ""
            if static_analysis:
                score = static_analysis.get("score", "N/A")
                issues = static_analysis.get("issues", []) or []
                categories = static_analysis.get("categories", {}) or {}

                # Prepare a compact, AI-friendly summary of the most important issues
                top_issues_lines = []
                for issue in issues[:10]:
                    line = issue.get("line", "?")
                    itype = issue.get("type", "info")
                    symbol = issue.get("symbol", "")
                    msg = issue.get("message", "")
                    top_issues_lines.append(
                        f"- [{itype}] Line {line} ({symbol}): {msg}"
                    )

                issues_block = "\n".join(top_issues_lines) if top_issues_lines else "No individual issues to list."

                static_context = (
                    "Pylint summary for this exact snippet:\n"
                    f"- Score: {score}/10.0\n"
                    f"- Total issues: {len(issues)}\n"
                    f"- Categories: {', '.join(categories.keys()) or 'none'}\n"
                    "\n"
                    "Key pylint issues (at most 10 shown):\n"
                    f"{issues_block}\n"
                )

            # Let LangChain render the final chat messages with the real code inserted
            messages = self.review_prompt.format_messages(
                code=code,
                static_context=static_context,
            )

            # Get AI review
            response = self.llm.invoke(messages)
            review_text = response.content if hasattr(response, 'content') else str(response)
            
            # Generate a brief summary
            summary = self._extract_summary(review_text)
            
            return {
                'review': review_text,
                'summary': summary
            }
            
        except Exception as e:
            error_msg = f"Error during AI review: {str(e)}"
            return {
                'review': f"## AI Review Error\n\n{error_msg}\n\nPlease check your API key and internet connection.",
                'summary': "Review failed due to an error."
            }
    
    def _extract_summary(self, review_text: str) -> str:
        """
        Extract a brief summary from the review text.
        
        Args:
            review_text: Full review text from AI
            
        Returns:
            Brief summary string
        """
        # Try to extract the first meaningful paragraph (no hard mid-word cut)
        lines = review_text.split('\n')
        summary_lines = []

        for line in lines:
            line = line.strip()
            # Skip markdown headings / empty lines
            if not line or line.startswith('#'):
                continue
            summary_lines.append(line)
            # Stop at the end of the first non-empty paragraph
            if line.endswith('.') or line.endswith('!') or line.endswith('?'):
                break

        summary = ' '.join(summary_lines).strip()

        # Soft length guard: if it's very long, cut at a sentence or word boundary,
        # but never in the middle of a word like "whic..."
        max_len = 400
        if len(summary) > max_len:
            cut = summary.rfind('.', 0, max_len)
            if cut == -1:
                cut = summary.rfind(' ', 0, max_len)
            if cut != -1:
                summary = summary[: cut + 1].strip()

        return summary if summary else "Review completed. See full report below."
    
    def format_review(self, review_result: Dict[str, str]) -> str:
        """
        Format AI review results as a readable report.
        
        Args:
            review_result: Result dictionary from review_code()
            
        Returns:
            Formatted markdown report string
        """
        report = []
        report.append("## AI Code Review\n")
        report.append(f"**Summary:** {review_result.get('summary', 'N/A')}\n")
        report.append("\n---\n")
        report.append(review_result.get('review', 'No review available.'))
        
        return "\n".join(report)

