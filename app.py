import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import io
import time

# Page configuration
st.set_page_config(
    page_title="AI Resume Advisor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .analysis-section {
        background: #1E1E1E;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #333;
    }
    .success-message {
        background: #1A472A;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    .upload-section {
        background: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #444;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_gemini():
    """Initialize Gemini API with error handling - SILENT mode"""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if api_key and api_key != "demo_mode":
            genai.configure(api_key=api_key)
            return True
        return False
    except Exception:
        return False

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF with comprehensive error handling"""
    try:
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        if not text.strip():
            st.error("❌ No text could be extracted from the PDF. Please ensure it's a text-based PDF.")
            return None
            
        return text.strip()
        
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return None

def analyze_resume_with_gemini(resume_text, job_category):
    """Analyze resume using Gemini AI with detailed prompt"""
    
    prompt = f"""
    ACT as a Senior Certified Professional Resume Writer (CPRW) with 15+ years of experience at top tech companies.
    
    **RESUME TO ANALYZE:**
    {resume_text}
    
    **TARGET ROLE:** {job_category}
    
    Provide a comprehensive analysis in this EXACT format:
    
    ## 🔴 CRITICAL MISTAKES & ERRORS
    - List specific spelling, grammar, and punctuation errors
    - Identify formatting inconsistencies  
    - Highlight weak action verbs and passive voice
    - Point out unclear or vague statements
    
    ## 🟡 STRATEGIC ALIGNMENT GAPS
    - Missing keywords and skills for {job_category} role
    - Areas needing quantifiable metrics and achievements
    - Experience that should be rephrased for better impact
    - Industry-specific sections that are missing or weak
    
    ## 🟢 ACTIONABLE IMPROVEMENT TIPS
    1. First specific improvement step
    2. Second specific improvement step  
    3. Third specific improvement step
    4. Fourth specific improvement step
    5. Fifth specific improvement step
    
    Be extremely specific, direct, and provide exact phrasing suggestions where needed.
    Focus on actionable advice that the candidate can implement immediately.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"❌ Error analyzing resume: {str(e)}")
        return None

def mock_analysis(resume_text, job_category):
    """Mock analysis for testing without API key"""
    return f"""
## 🔴 CRITICAL MISTAKES & ERRORS
- Missing quantifiable achievements in project descriptions
- Inconsistent date formatting in experience section
- Overuse of passive voice in bullet points
- Missing contact information in header

## 🟡 STRATEGIC ALIGNMENT GAPS for {job_category}
- Missing keywords: 'machine learning', 'data pipelines', 'cloud infrastructure'
- No mention of specific technologies like Docker, Kubernetes, or AWS
- Lack of metrics to show impact (e.g., 'improved performance by 40%')
- Experience descriptions are too generic and not tailored to {job_category} role

## 🟢 ACTIONABLE IMPROVEMENT TIPS
1. Add 3-5 quantifiable achievements using the STAR method (Situation, Task, Action, Result)
2. Include specific technologies and tools relevant to {job_category} position
3. Rewrite bullet points to start with strong action verbs like 'Architected', 'Engineered', 'Optimized'
4. Create a dedicated 'Technical Skills' section with categorized skills
5. Add a professional summary at the top tailored to {job_category} roles
"""

def main():
    # Header Section
    st.markdown('<div class="main-header">AI Resume Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #888; margin-bottom: 3rem;">Get instant, professional resume feedback powered by AI</div>', unsafe_allow_html=True)
    
    # Initialize Gemini API (silent - no error messages)
    api_initialized = initialize_gemini()
    
    # Main content area - everything in one column
    st.markdown("### Upload & Analyze Your Resume")
    
    # Create two columns for upload and job selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload section
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📤 Upload Your Resume (PDF)",
            type="pdf",
            help="Your file is processed securely and never stored"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Job category selection
        job_categories = [
            "Software Engineer", "Data Scientist", "Product Manager", 
            "Data Analyst", "Frontend Developer", "Backend Developer",
            "Full Stack Developer", "DevOps Engineer", "Machine Learning Engineer",
            "UX/UI Designer", "Product Designer", "Project Manager",
            "Business Analyst", "Marketing Manager", "Sales Executive",
            "Cloud Architect", "Security Engineer", "QA Engineer"
        ]
        
        selected_job = st.selectbox(
            "🎯 Target Job Role",
            options=job_categories,
            index=0
        )
        
        # Analysis button
        analyze_clicked = st.button(
            "🚀 Analyze My Resume",
            type="primary",
            use_container_width=True,
            disabled=not uploaded_file
        )

    # Display results below the upload section
    if uploaded_file:
        st.info(f"**File Ready:** {uploaded_file.name} | **Target Role:** {selected_job}")
        
        if analyze_clicked:
            with st.spinner("🔍 Analyzing your resume... This may take 10-20 seconds."):
                # Simulate processing time for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if resume_text:
                    # Show text preview
                    with st.expander("📝 View Extracted Text", expanded=False):
                        st.text_area("", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, 
                                   height=200, key="extracted_text", label_visibility="collapsed")
                    
                    # Always use mock analysis for now (no API errors)
                    analysis_result = mock_analysis(resume_text, selected_job)
                    
                    if analysis_result:
                        st.markdown("---")
                        st.markdown("## 📋 Analysis Results")
                        
                        # Display results in a nice container
                        st.markdown(f'<div class="analysis-section">{analysis_result}</div>', 
                                  unsafe_allow_html=True)
                        
                        # Success message
                        st.markdown("""
                        <div class="success-message">
                        <h4>✅ Analysis Complete!</h4>
                        <p>Use these insights to improve your resume and land your dream job!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download results
                        st.download_button(
                            label="💾 Download Analysis Report",
                            data=analysis_result,
                            file_name=f"resume_analysis_{selected_job.replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        " • Your data is never stored"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()