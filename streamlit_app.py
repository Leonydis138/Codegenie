# streamlit_app.py
import streamlit as st
import os
import time
from pathlib import Path
from codegenie import CodeGenieAutoBuilder
from codegenie.utils.diagram_generator import generate_architecture_diagram, generate_workflow_diagram

st.set_page_config(
    page_title="CodeGenie Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.0rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .feature-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .app-preview {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def main():
    if 'builder' not in st.session_state:
        st.session_state.builder = CodeGenieAutoBuilder()

    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/robot.png", width=80)
        st.title("CodeGenie Pro")
        st.markdown("---")
        st.subheader("🚀 Quick Start")
        st.markdown("1. Describe your app idea\n2. Generate\n3. Download and run")
        st.markdown("---")
        st.subheader("📊 Stats")
        st.metric("Projects Built", len(st.session_state.builder.projects))
        st.markdown("---")
        st.subheader("🔧 Settings")
        auto_detect = st.checkbox("Auto-detect app type", value=True)
        show_code = st.checkbox("Show generated code", value=False)

    st.markdown('<h1 class="main-header">🚀 CodeGenie Pro</h1>', unsafe_allow_html=True)
    st.markdown("### Transform Your Ideas into Working Applications - Instantly!")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Build App", "📊 Architecture", "🎨 Examples", "📚 Documentation", "🚀 About"])
    with tab1:
        build_app_interface(auto_detect, show_code)
    with tab2:
        show_architecture()
    with tab3:
        show_examples()
    with tab4:
        show_documentation()
    with tab5:
        show_about()

# --- remaining functions for build_app_interface, generate_application, show_architecture, etc ---
# (Use the full code you already have in your local copy)
