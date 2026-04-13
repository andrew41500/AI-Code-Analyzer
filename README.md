# 🔍 AI Code Reviewer

A comprehensive Python code review tool that combines **static analysis** (pylint) with **AI-powered review** (Groq/LLaMA or Google Gemini) to provide detailed feedback on code quality, style, bugs, security, and best practices.

## ✨ Features

- 🤖 **AI-Powered Review**: Uses **Groq (LLaMA 3.3)** as the primary provider with **Google Gemini (2.5 Flash)** as an automatic fallback.
- 🔍 **Static Analysis**: Integrates pylint for automated code quality checks
- 📊 **Comprehensive Reports**: Combines both static and AI analysis for complete feedback
- 🎨 **User-Friendly UI**: Clean Streamlit interface for easy code review
- 📁 **Multiple Input Methods**: Paste code directly or upload Python files
- 🚀 **GitHub Actions Ready**: Includes workflow template for automated PR reviews

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- **Groq API key** (Primary) ([Get one here](https://console.groq.com/keys))
- **Google Gemini API key** (Fallback) ([Get one here](https://aistudio.google.com/app/apikey))

### Setup Steps

1. **Clone or download this repository**

```bash
cd "AI Code Reviewer"
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up your API key**

   **Option 1: Environment variable (recommended)**
   
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_key_here
   GOOGLE_API_KEY=your_gemini_key_here
   ```
   
   **Option 2: Enter in the app**
   
   You can also enter your API key directly in the Streamlit app sidebar. The system will automatically detect the provider.

## 🚀 Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Using the Application

1. **Choose Input Method**:
   - **Paste Code**: Type or paste your Python code directly
   - **Upload File**: Upload a `.py` file from your computer

2. **Enter API Key** (if not set in `.env`):
   - Enter your Google Gemini API key in the sidebar

3. **Click "Analyze Code"**:
   - The tool will run static analysis (pylint)
   - Then generate an AI-powered review
   - Results will appear in organized tabs

4. **Review Results**:
   - **Combined Report**: View both static and AI analysis together
   - **AI Review**: Detailed AI-generated suggestions
   - **Static Analysis**: Pylint findings and score

### Example Usage

Try the sample code provided in `examples/sample_code.py`:

```bash
# Upload the file or paste its contents in the app
```

## 📁 Project Structure

```
ai-code-reviewer/
├── src/
│   ├── __init__.py
│   ├── ai_reviewer.py          # LangChain agent for AI review
│   └── static_analyzer.py      # Pylint integration
├── app.py                       # Streamlit UI application
├── examples/
│   └── sample_code.py          # Example code for testing
├── .github/
│   └── workflows/
│       └── code_review.yml     # GitHub Actions workflow template
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Configuration

### Pylint Configuration

The static analyzer uses default pylint settings. You can customize them in `src/static_analyzer.py`:

```python
self.pylint_config = {
    'disable': ['missing-module-docstring'],
    'max-line-length': 120,
}
```

The AI reviewer prioritizes Groq with a LLaMA model and falls back to Gemini if the primary provider is unavailable. You can customize the models in `.env`:

```env
GROQ_MODEL_NAME=llama-3.3-70b-versatile
GEMINI_MODEL_NAME=gemini-2.5-flash
```

The logic is handled in `src/ai_reviewer.py`:

```python
# Primary: Groq (LLaMA)
# Fallback: Google Gemini
```
 village
## 🤖 GitHub Actions Integration

A GitHub Actions workflow template is included in `.github/workflows/code_review.yml`. This allows you to:

- Automatically review code in pull requests
- Post review comments on PRs
- Run on every push or PR

### Setup for GitHub Actions

1. **Add your API key as a GitHub Secret**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add a new secret: `GOOGLE_API_KEY` with your API key value

2. **The workflow will**:
   - Trigger on pull requests
   - Analyze changed Python files
   - Post review comments (requires additional setup for PR comments)

**Note**: The provided workflow is a template. You may need to customize it based on your repository structure and requirements.

## 📊 What Gets Reviewed?

### Static Analysis (Pylint)
- Code style violations (PEP 8)
- Potential bugs and errors
- Code complexity
- Unused variables/imports
- Naming conventions

### AI Review (Gemini)
- **Style Improvements**: PEP 8 compliance, naming, formatting
- **Potential Bugs**: Logic errors, edge cases, runtime issues
- **Security Concerns**: Input validation, injection risks, etc.
- **Refactoring Suggestions**: Code structure improvements
- **Documentation**: Missing docstrings, unclear code

## 🎯 Example Output

### Pylint Score
- **Score: 6.5/10.0**
- Issues found by category (errors, warnings, conventions)

### AI Review
- Detailed markdown report with:
  - Style issues and fixes
  - Bug identification
  - Security recommendations
  - Refactoring suggestions
  - Documentation needs

## 🐛 Troubleshooting

### "Pylint not found"
```bash
pip install pylint
```

### "Google API key not found"
- Make sure you've set `GOOGLE_API_KEY` in `.env` or entered it in the app
- Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### API Rate Limits
- The free tier of Gemini has rate limits
- If you hit limits, wait a few minutes or upgrade your API plan

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 🙏 Acknowledgments

- **LangChain**: For the AI agent framework
- **Groq**: For providing high-speed LLaMA models
- **Google Gemini**: For the fallback AI model
- **Pylint**: For static code analysis
- **Streamlit**: For the UI framework

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Happy Coding! 🚀**

