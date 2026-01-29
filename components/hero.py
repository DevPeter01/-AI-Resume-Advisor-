import streamlit as st

def show_hero():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-code">
                const AIResumeAdvisor = () => analyzeYourCareer();
            </div>
            <div class="hero-sub">
                Transform your resume with AI-powered insights that hiring managers actually look for
            </div>
            <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span style="background: rgba(88, 166, 255, 0.1); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; border: 1px solid rgba(88, 166, 255, 0.2);">
                    🤖 AI-Powered
                </span>
                <span style="background: rgba(139, 92, 246, 0.1); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; border: 1px solid rgba(139, 92, 246, 0.2);">
                    📊 Detailed Analysis
                </span>
                <span style="background: rgba(63, 185, 80, 0.1); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; border: 1px solid rgba(63, 185, 80, 0.2);">
                    🎯 Role-Specific
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)