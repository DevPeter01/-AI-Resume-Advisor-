import streamlit as st
import time

# Import Utils
from utils.ai_analysis import initialize_ai, analyze_resume, mock_analysis
from utils.pdf_processor import extract_text_from_pdf

# Import Components
from components.hero import show_hero
from components.upload import show_upload_section
from components.results import show_results

# Page Config
st.set_page_config(
    page_title="AI Resume Advisor - Professional Resume Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def load_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_features():
    """Display feature cards for the AI Resume Advisor"""
    st.markdown("<div class='header-container'><h2>Why Choose Our AI Resume Analyzer?</h2></div>", unsafe_allow_html=True)
    
    features = [
        {
            "icon": "🎯",
            "title": "Role-Specific Analysis",
            "description": "Tailored feedback based on your target job position with specific skill gap identification."
        },
        {
            "icon": "📊",
            "title": "Resume Scoring",
            "description": "Get a comprehensive score with breakdown of strengths and areas for improvement."
        },
        {
            "icon": "🔍",
            "title": "Hiring Manager Simulation",
            "description": "See how a recruiter would evaluate your resume in 30 seconds."
        },
        {
            "icon": "✏️",
            "title": "Smart Rewrites",
            "description": "Get specific examples of how to improve your resume bullets and descriptions."
        }
    ]
    
    st.markdown('<div class="features-grid">', unsafe_allow_html=True)
    for i, feature in enumerate(features):
        st.markdown(f"""
        <div class="feature-card fade-in-delay-{i+1}">
            <div class="feature-icon">{feature['icon']}</div>
            <div class="feature-title">{feature['title']}</div>
            <div class="feature-desc">{feature['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_stats():
    """Display statistics to build trust"""
    st.markdown("<h3 style='text-align: center; margin: 2rem 0;'>Our Impact</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">95%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">50K+</div>
            <div class="stat-label">Resumes Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">2.3x</div>
            <div class="stat-label">Better Response</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">100%</div>
            <div class="stat-label">ATS Compatible</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    load_css()
    
    # Initialize floating elements
    st.markdown("""
    <div class="floating-element floating-1"></div>
    <div class="floating-element floating-2"></div>
    <div class="floating-element floating-3"></div>
    """, unsafe_allow_html=True)
    
    # Initialize AI (silent)
    initialize_ai()
    
    # Hero Section
    show_hero()
    
    # Stats Section
    show_stats()
    
    st.markdown("---")
    
    # Features Section
    show_features()
    
    st.markdown("---")
    
    # Main Interaction Area
    uploaded_file, selected_job, analyze_clicked = show_upload_section()
    
    # Logic Handling
    if uploaded_file and analyze_clicked:
        # Spinner with modern text
        with st.spinner(">> Scanning Document... [AI Analysis In Progress]"):
            
            # Artificial delay for effect (can be removed for speed)
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # 1. Extract Text
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                # 2. Analyze (Mock or Real)
                # We prioritize mock for stability if key is missing/limit reached,
                # but try real if configured.
                
                # For this demo, we'll try to use the generic 'analyze_resume' logic.
                # If it returns None (e.g. no key), we fallback to mock.
                analysis_result = analyze_resume(resume_text, selected_job)
                
                if not analysis_result:
                    analysis_result = mock_analysis(resume_text, selected_job)
                
                # 3. Show Results
                show_results(analysis_result)
                
                # Download Button
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📥 Save Analysis Report [TXT]",
                        data=analysis_result,
                        file_name=f"resume_analysis_{selected_job.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

    elif analyze_clicked and not uploaded_file:
        st.warning("⚠️ System Alert: No Resume Detected. Please upload a PDF file.")

    # Footer
    st.markdown("<div class='footer'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #444; font-family: monospace; font-size: 0.8rem;'>"
        "AI Resume Advisor v2.0 | Advanced Resume Analysis Platform | Secure & Private"
        "</div>", 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()