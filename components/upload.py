import streamlit as st

def show_upload_section():
    st.markdown("### <span style='color: var(--accent-primary)'>01.</span> Upload & Analyze Your Resume", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-zone">
            <h4>📁 Upload Resume</h4>
            <p style="color: #666; font-size: 0.9rem;">Drag & drop your PDF resume here</p>
            <p style="color: #888; font-size: 0.8rem;">or click to browse files</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type="pdf",
            label_visibility="collapsed"
        )
        
        # Mascot / Toy Animation
        st.markdown("""
        <div class="mascot-container">
            <div class="mascot-body">📄</div>
        </div>
        <div style="text-align: center; color: var(--text-secondary); margin-top: 10px; font-family: var(--code-font); font-size: 0.8rem;">
            AI is ready to analyze...
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🎯 Select Target Role")
        job_categories = [
            "Software Engineer", "Data Scientist", "Product Manager", 
            "Full Stack Developer", "DevOps Engineer", "Machine Learning Engineer",
            "Frontend Developer", "Backend Developer", "UX Designer",
            "Cybersecurity Specialist", "Data Analyst", "Project Manager",
            "Business Analyst", "Marketing Manager", "Sales Manager",
            "HR Manager", "Financial Analyst", "Operations Manager"
        ]
        
        selected_job = st.selectbox(
            "Choose your target role:",
            options=job_categories,
            index=0
        )
        
        st.markdown("#### ⚙️ Analysis Options")
        analysis_depth = st.radio(
            "Select analysis depth:",
            options=["Standard", "Detailed", "Comprehensive"],
            horizontal=True
        )
        
        analyze_clicked = st.button(
            "🚀 Analyze Resume Now",
            use_container_width=True,
            type="primary"
        )
        
        # Show tips
        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            - Use a clean, well-formatted PDF resume
            - Ensure text is selectable (not scanned images)
            - Select the most relevant job category
            - For best results, use a recent version of your resume
            """)

    return uploaded_file, selected_job, analyze_clicked