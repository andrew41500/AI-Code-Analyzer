"""
AI Code Reviewer - Streamlit Application

Main Streamlit UI for the AI Code Reviewer tool.
Allows users to paste code or upload Python files for comprehensive code review.
"""
#Test


import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_reviewer import AIReviewer
from src.static_analyzer import StaticAnalyzer

# Page configuration
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .score-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'review_completed' not in st.session_state:
        st.session_state.review_completed = False
    if 'static_analysis' not in st.session_state:
        st.session_state.static_analysis = None
    if 'ai_review' not in st.session_state:
        st.session_state.ai_review = None


def get_code_input() -> str:
    """
    Get code input from user (either pasted or uploaded).
    
    Returns:
        Code string or empty string if no input
    """
    code = ""
    
    # Sidebar for input method selection
    with st.sidebar:
        st.header("📝 Input Method")
        input_method = st.radio(
            "Choose how to provide code:",
            ["Paste Code", "Upload File"],
            key="input_method"
        )
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        # API Key input (optional, can also use .env)
        api_key = st.text_input(
            "API Key (optional if set in .env)",
            type="password",
            help="Provide your Groq or Google Gemini API key."
        )
        
        if api_key:
            st.session_state.api_key = api_key
        elif 'api_key' not in st.session_state:
            # Try to get from environment
            st.session_state.api_key = os.getenv('GROQ_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    # Main input area
    if input_method == "Paste Code":
        st.subheader("📋 Paste Your Python Code")
        code = st.text_area(
            "Enter Python code here:",
            height=400,
            placeholder="""# Example code
def calculate_sum(a, b):
    return a+b

result = calculate_sum(5, 10)
print(result)
""",
            key="pasted_code"
        )
    else:
        st.subheader("📁 Upload Python File")
        uploaded_file = st.file_uploader(
            "Choose a .py file",
            type=['py'],
            key="uploaded_file"
        )
        
        if uploaded_file is not None:
            code = uploaded_file.read().decode('utf-8')
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.code(code, language='python')
    
    return code


def display_results(static_analysis: dict, ai_review: dict):
    """
    Display review results in a formatted way.
    
    Args:
        static_analysis: Static analysis results dictionary
        ai_review: AI review results dictionary
    """
    st.markdown("---")
    st.header("📊 Review Results")
    
    # Create two columns for scores
    col1, col2 = st.columns(2)
    
    with col1:
        score = static_analysis.get('score', 0.0)
        score_color = "🟢" if score >= 8.0 else "🟡" if score >= 6.0 else "🔴"
        st.metric(
            "Pylint Score",
            f"{score}/10.0",
            delta=f"{score - 5.0:.1f}" if score > 5.0 else None
        )
        st.caption(f"{score_color} Code Quality Indicator")
    
    with col2:
        total_issues = len(static_analysis.get('issues', []))
        st.metric(
            "Issues Found",
            total_issues,
            delta=f"-{total_issues}" if total_issues > 0 else None
        )
        st.caption("Static Analysis Issues")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Combined Report", "🤖 AI Review", "🔍 Static Analysis"])
    
    with tab1:
        st.markdown("## Complete Code Review Report\n")
        
        # Static Analysis Section
        st.markdown("### 🔍 Static Analysis (Pylint)")
        analyzer = StaticAnalyzer()
        static_report = analyzer.format_report(static_analysis)
        st.markdown(static_report)
        
        st.markdown("---")
        
        # AI Review Section
        st.markdown("### 🤖 AI-Powered Review")
        reviewer = AIReviewer()
        ai_report = reviewer.format_review(ai_review)
        st.markdown(ai_report)
    
    with tab2:
        st.markdown("## AI Code Review\n")
        reviewer = AIReviewer()
        ai_report = reviewer.format_review(ai_review)
        st.markdown(ai_report)
    
    with tab3:
        st.markdown("## Static Analysis Details\n")
        analyzer = StaticAnalyzer()
        static_report = analyzer.format_report(static_analysis)
        st.markdown(static_report)
        
        # Show raw issues if available
        issues = static_analysis.get('issues', [])
        if issues:
            st.markdown("### Raw Issues Data")
            with st.expander("View Raw JSON Data"):
                st.json(issues)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<p class="main-header">🔍 AI Code Reviewer</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
        Automated code review using AI and static analysis tools.<br>
        Get instant feedback on style, bugs, security, and best practices.
    </div>
    """, unsafe_allow_html=True)
    
    # Get code input
    code = get_code_input()
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Code",
            type="primary",
            use_container_width=True
        )
    
    # Process analysis
    if analyze_button:
        if not code.strip():
            st.error("❌ Please provide Python code to analyze.")
            return
        
        if not st.session_state.get('api_key'):
            st.error("❌ Please provide an API key in the sidebar or set GROQ_API_KEY / GOOGLE_API_KEY in your .env file.")
            st.info("💡 You can use either a Groq key (console.groq.com) or a Google key (aistudio.google.com).")
            return
        
        # Show progress
        with st.spinner("🔄 Analyzing code... This may take a moment."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Static Analysis
            status_text.text("Running static analysis with pylint...")
            progress_bar.progress(30)
            
            try:
                analyzer = StaticAnalyzer()
                static_analysis = analyzer.analyze_code(code)
                st.session_state.static_analysis = static_analysis
            except Exception as e:
                st.error(f"❌ Static analysis failed: {str(e)}")
                return
            
            # Step 2: AI Review
            try:
                reviewer = AIReviewer(api_key=st.session_state.api_key)
                
                # Update status text with active provider
                status_text.text(f"Generating AI review with {reviewer.active_provider} ({reviewer.active_model})...")
                progress_bar.progress(60)
                
                ai_review = reviewer.review_code(code, static_analysis=static_analysis)
                st.session_state.ai_review = ai_review
                st.session_state.active_provider = reviewer.active_provider
                st.session_state.active_model = reviewer.active_model
            except Exception as e:
                st.error(f"❌ AI review failed: {str(e)}")
                st.info("💡 Make sure your API key is valid and you have internet connection.")
                # Still show static analysis if available
                if st.session_state.static_analysis:
                    analyzer = StaticAnalyzer()
                    static_report = analyzer.format_report(st.session_state.static_analysis)
                    st.markdown("## Static Analysis Results")
                    st.markdown(static_report)
                return
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            st.session_state.review_completed = True
            
            # Small delay for UX
            import time
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
    
    # Display results if available
    if st.session_state.review_completed:
        if st.session_state.static_analysis and st.session_state.ai_review:
            display_results(
                st.session_state.static_analysis,
                st.session_state.ai_review
            )
    
    # Footer
    st.markdown("---")
    active_info = f" | Active Model: {st.session_state.active_model}" if st.session_state.get('active_model') else ""
    st.markdown(f"""
    <div style='text-align: center; color: #999; font-size: 0.9rem; padding: 2rem;'>
        <p>🔍 AI Code Reviewer | Powered by LangChain, Groq & Gemini | Static Analysis by Pylint{active_info}</p>
        <p>For issues or contributions, visit the project repository.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


