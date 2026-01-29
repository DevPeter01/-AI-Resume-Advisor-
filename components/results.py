import streamlit as st
import re


def show_results(analysis_text):
    if not analysis_text:
        return

    st.markdown("---")
    st.markdown("### <span style='color: var(--accent-primary)'>02.</span> Analysis Results", unsafe_allow_html=True)
    
    # Parse the analysis text into sections
    sections = parse_analysis_into_sections(analysis_text)
    
    # Display each section with proper formatting
    display_parsed_sections(sections)
    
    st.markdown("""
    <div style="margin-top: 2rem; text-align: center;">
        <div class="success-badge">Analysis Completed Successfully</div>
    </div>
    """, unsafe_allow_html=True)


def parse_analysis_into_sections(analysis_text):
    """
    Parse the analysis text into structured sections
    """
    sections = {}
    
    # Define section patterns
    section_patterns = {
        'quick_summary': r'## 📊 QUICK SUMMARY \(TL;DR\)(.*?)(?=## |$)',
        'resume_score': r'## 💯 RESUME SCORE & BREAKDOWN(.*?)(?=## |$)',
        'role_fit': r'## 🎯 ROLE FIT ANALYSIS(.*?)(?=## |$)',
        'skill_gap': r'## 🧩 SKILL GAP MATRIX(.*?)(?=## |$)',
        'hiring_manager': r'## 🔍 HIRING MANAGER SIMULATION(.*?)(?=## |$)',
        'risks': r'## ⚠️ RESUME RISK DETECTION(.*?)(?=## |$)',
        'improvements': r'## 🛠️ IMPROVEMENT ACTIONS \(PRIORITIZED\)(.*?)(?=## |$)',
        'rewrites': r'## ✏️ EXAMPLE REWRITES(.*?)(?=## |$)',
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            sections[section_name] = content
    
    return sections

def display_parsed_sections(sections):
    """
    Display parsed sections with appropriate formatting
    """
    # Quick Summary
    if 'quick_summary' in sections:
        with st.expander("📊 Quick Summary (TL;DR)", expanded=True):
            # Format bullet points
            content = sections['quick_summary']
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('-'):
                    st.markdown(f"<div class='bullet-item'>{line}</div>", unsafe_allow_html=True)
    
    # Resume Score
    if 'resume_score' in sections:
        st.subheader("💯 Resume Score & Breakdown")
        score_content = sections['resume_score']
        
        # Extract the overall score
        overall_match = re.search(r'Overall Score: (\d+)/100', score_content)
        if overall_match:
            overall_score = int(overall_match.group(1))
            # Display score visually
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"<div class='score-display'>Score: {overall_score}/100</div>", unsafe_allow_html=True)
                # Create a progress bar
                st.progress(overall_score / 100)
        
        # Display breakdown
        st.markdown("<div class='score-breakdown'>", unsafe_allow_html=True)
        breakdown_lines = [line for line in score_content.split('\n') if 'Overall Score:' not in line and ':' in line]
        for line in breakdown_lines:
            line = line.strip()
            if line:
                st.markdown(f"<div class='breakdown-item'>{line}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Role Fit Analysis
    if 'role_fit' in sections:
        with st.expander("🎯 Role Fit Analysis", expanded=True):
            st.markdown(f"<div class='role-fit-content'>{sections['role_fit']}</div>", unsafe_allow_html=True)
    
    # Skill Gap Matrix
    if 'skill_gap' in sections:
        st.subheader("🧩 Skill Gap Matrix")
        # Render as a table
        st.markdown(sections['skill_gap'])
    
    # Hiring Manager Simulation
    if 'hiring_manager' in sections:
        st.subheader("🔍 Hiring Manager Simulation")
        # Format the simulation content
        content = sections['hiring_manager']
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                st.markdown(f"<div class='simulation-item'>{line}</div>", unsafe_allow_html=True)
            elif line:
                st.markdown(f"<div class='simulation-header'>{line}</div>", unsafe_allow_html=True)
    
    # Resume Risks
    if 'risks' in sections:
        st.subheader("⚠️ Resume Risk Detection")
        content = sections['risks']
        risk_items = [item.strip() for item in content.split('\n') if item.strip().startswith('- ')]
        for item in risk_items:
            st.markdown(f"<div class='risk-item'>{item}</div>", unsafe_allow_html=True)
    
    # Improvement Actions
    if 'improvements' in sections:
        st.subheader("🛠️ Improvement Actions (Prioritized)")
        content = sections['improvements']
        improvement_items = [item.strip() for item in content.split('\n') if item.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]
        for item in improvement_items:
            st.markdown(f"<div class='improvement-item'>{item}</div>", unsafe_allow_html=True)
    
    # Example Rewrites
    if 'rewrites' in sections:
        st.subheader("✏️ Example Rewrites")
        content = sections['rewrites']
        # Split into before/after sections
        rewrite_parts = content.split('**After:**')
        if len(rewrite_parts) > 1:
            before_part = rewrite_parts[0].replace('**Before:**', '').strip()
            after_part = rewrite_parts[1].split('**Why better:**')[0].strip() if '**Why better:**' in rewrite_parts[1] else rewrite_parts[1].strip()
            explanation = ''
            if '**Why better:**' in rewrite_parts[1]:
                explanation = rewrite_parts[1].split('**Why better:**')[1].strip()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div class='rewrite-section-title'>Before:</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rewrite-before'>{before_part}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div class='rewrite-section-title'>After:</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rewrite-after'>{after_part}</div>", unsafe_allow_html=True)
            
            if explanation:
                st.markdown("<div class='rewrite-explanation'><strong>Why better:</strong> {}</div>".format(explanation), unsafe_allow_html=True)
