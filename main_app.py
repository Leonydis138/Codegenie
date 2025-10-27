import streamlit as st
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime

# Import from other modules
from core_infrastructure import (
    EnhancedDatabaseManager, 
    EnhancedSecurityManager, 
    EnhancedResearchEngine
)
from analytics_engine import AdvancedAnalyticsEngine
from autonomous_agent import EnhancedAutonomousAgent

# ===================== PAGE CONFIGURATION =====================
st.set_page_config(
    page_title="AI Assistant Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE INITIALIZATION =====================
def init_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user_id = "user_" + str(time.time())
        st.session_state.db_manager = EnhancedDatabaseManager()
        st.session_state.security = EnhancedSecurityManager()
        st.session_state.research_engine = EnhancedResearchEngine(st.session_state.db_manager)
        st.session_state.analytics = AdvancedAnalyticsEngine()
        st.session_state.agent = EnhancedAutonomousAgent(
            st.session_state.db_manager,
            st.session_state.security,
            st.session_state.research_engine,
            st.session_state.analytics,
            st.session_state.user_id
        )
        st.session_state.conversation_history = []
        st.session_state.uploaded_data = None
        st.session_state.current_persona = "Assistant"

# ===================== MAIN APPLICATION =====================
def main():
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🤖 AI Assistant Platform")
        st.markdown("---")
        
        # Persona selection
        st.session_state.current_persona = st.selectbox(
            "🎭 Select AI Persona",
            ["Assistant", "Researcher", "Teacher", "Analyst", "Engineer", "Scientist"],
            index=0
        )
        
        # Theme
        theme = st.selectbox("🎨 Theme", ["Dark", "Light"], index=0)
        
        st.markdown("---")
        st.markdown("### 📊 Session Info")
        st.info(f"**User ID**: {st.session_state.user_id[:12]}...")
        st.info(f"**Session**: {st.session_state.agent.session_id[:12]}...")
        st.info(f"**Interactions**: {len(st.session_state.conversation_history)}")
        
        st.markdown("---")
        if st.button("🔄 Clear Session", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.uploaded_data = None
            st.rerun()
    
    # Main header
    st.markdown('<div class="main-header">🤖 AI Assistant Platform</div>', unsafe_allow_html=True)
    st.markdown(f"**Active Persona**: {st.session_state.current_persona} | **Theme**: {theme}")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Home", 
        "💬 AI Assistant", 
        "📊 Data Analytics", 
        "🔬 Research", 
        "💻 Code Playground"
    ])
    
    # ===================== TAB 1: HOME =====================
    with tab1:
        st.markdown("## Welcome to AI Assistant Platform")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Sessions", len(st.session_state.conversation_history))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Active Users", "1")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Data Uploads", "1" if st.session_state.uploaded_data is not None else "0")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Features
        st.markdown("### 🌟 Platform Features")
        
        features_col1, features_col2 = st.columns(2)
        
        with features_col1:
            st.markdown("""
            #### 💬 AI Assistant
            - Natural language interaction
            - Multi-persona support
            - Research integration
            - Code generation
            
            #### 📊 Data Analytics
            - Upload CSV/Excel files
            - Automated analysis
            - Interactive visualizations
            - ML model building
            """)
        
        with features_col2:
            st.markdown("""
            #### 🔬 Research Engine
            - Multi-source search
            - DuckDuckGo integration
            - Wikipedia access
            - arXiv papers
            
            #### 💻 Code Playground
            - Safe code execution
            - Python support
            - Output visualization
            - Security sandbox
            """)
        
        st.markdown("---")
        
        # Quick start
        st.markdown("### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Select a Persona** from the sidebar
        2. **Navigate to AI Assistant** to start chatting
        3. **Upload data** in Data Analytics for analysis
        4. **Run research** in the Research tab
        5. **Execute code** in Code Playground
        """)
    
    # ===================== TAB 2: AI ASSISTANT =====================
    with tab2:
        st.markdown("## 💬 AI Assistant")
        st.markdown(f"**Active Persona**: {st.session_state.current_persona}")
        
        # Conversation display
        conversation_container = st.container()
        
        with conversation_container:
            if st.session_state.conversation_history:
                for entry in st.session_state.conversation_history:
                    with st.chat_message("user"):
                        st.write(entry.get("user_input", ""))
                    
                    if "system_response" in entry:
                        with st.chat_message("assistant"):
                            st.markdown(entry["system_response"])
            else:
                st.info("👋 Start a conversation by typing your question or goal below!")
        
        # Input
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Ask me anything, request research, or describe a problem to solve..."
        )
        
        col1, col2 = st.columns([1, 5])
        
        with col1:
            send_button = st.button("🚀 Send", use_container_width=True)
        
        with col2:
            if st.button("🔍 Research Mode", use_container_width=True):
                if user_input:
                    user_input = "Research: " + user_input
                    send_button = True
        
        if send_button and user_input:
            with st.spinner("🤔 Processing your request..."):
                response, metadata = st.session_state.agent.execute_enhanced_goal(user_input)
                
                st.session_state.conversation_history.append({
                    "user_input": user_input,
                    "system_response": response,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
    
    # ===================== TAB 3: DATA ANALYTICS =====================
    with tab3:
        st.markdown("## 📊 Data Analytics")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your data (CSV or Excel)",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file for analysis"
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_data = df
                
                st.success(f"✅ File loaded: {uploaded_file.name} ({df.shape[0]} rows, {df.shape[1]} columns)")
                
                # Data preview
                st.markdown("### 📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Analysis tabs
                analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
                    "📈 Overview",
                    "📊 Visualization",
                    "🤖 AI Insights",
                    "🧠 ML Models"
                ])
                
                with analysis_tab1:
                    st.markdown("### 📈 Comprehensive Analysis")
                    analysis_text = st.session_state.analytics.generate_comprehensive_analysis(df)
                    st.markdown(analysis_text)
                
                with analysis_tab2:
                    st.markdown("### 📊 Interactive Visualizations")
                    
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        viz_type = st.selectbox(
                            "Visualization Type",
                            ["line", "bar", "scatter", "histogram", "pie", "heatmap", "box", "3d_scatter"]
                        )
                    
                    with viz_col2:
                        viz_theme = st.selectbox("Theme", ["plotly_dark", "plotly", "seaborn", "simple_white"])
                    
                    if st.button("Generate Visualization", use_container_width=True):
                        fig = st.session_state.analytics.create_advanced_visualization(
                            df, viz_type, f"{viz_type.title()} Chart", viz_theme
                        )
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Could not generate visualization with current data")
                
                with analysis_tab3:
                    st.markdown("### 🤖 AI-Generated Insights")
                    insights = st.session_state.analytics.generate_ai_insights(df)
                    st.markdown(insights)
                
                with analysis_tab4:
                    st.markdown("### 🧠 Machine Learning Models")
                    
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    if len(numeric_cols) >= 2:
                        target_col = st.selectbox("Select Target Variable", numeric_cols)
                        model_type = st.selectbox("Model Type", ["regression"])
                        
                        if st.button("Train Model", use_container_width=True):
                            with st.spinner("Training model..."):
                                result = st.session_state.analytics.create_ml_model(df, target_col, model_type)
                                
                                if "error" in result:
                                    st.error(f"❌ {result['error']}")
                                else:
                                    st.success("✅ Model trained successfully!")
                                    
                                    st.markdown("#### Model Metrics")
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("MSE", f"{result['metrics']['mse']:.4f}")
                                    with col2:
                                        st.metric("RMSE", f"{result['metrics']['rmse']:.4f}")
                                    with col3:
                                        st.metric("R² Score", f"{result['metrics']['r2_score']:.4f}")
                                    
                                    st.markdown("#### Feature Importance")
                                    importance_df = pd.DataFrame(
                                        result['feature_importance'].items(),
                                        columns=['Feature', 'Importance']
                                    ).sort_values('Importance', ascending=False)
                                    
                                    st.dataframe(importance_df, use_container_width=True)
                    else:
                        st.warning("Need at least 2 numeric columns for ML modeling")
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
        
        elif st.session_state.uploaded_data is not None:
            st.info("Using previously uploaded data")
            df = st.session_state.uploaded_data
            st.dataframe(df.head(), use_container_width=True)
    
    # ===================== TAB 4: RESEARCH =====================
    with tab4:
        st.markdown("## 🔬 Research Engine")
        st.markdown("Search across multiple sources: Web, Wikipedia, and arXiv")
        
        research_query = st.text_input(
            "Research Query:",
            placeholder="Enter your research topic..."
        )
        
        max_results = st.slider("Maximum results per source", 3, 10, 5)
        
        if st.button("🔍 Search", use_container_width=True):
            if research_query:
                with st.spinner("🔍 Searching multiple sources..."):
                    results = st.session_state.research_engine.search_multiple_sources(
                        research_query, max_results
                    )
                    
                    if any(results.values()):
                        for source, source_results in results.items():
                            if source_results:
                                st.markdown(f"### {source.title()} Results ({len(source_results)})")
                                
                                for i, result in enumerate(source_results, 1):
                                    with st.expander(f"{i}. {result.get('title', 'N/A')}"):
                                        st.markdown(f"**Source**: {result.get('source', 'Unknown')}")
                                        if 'url' in result and result['url']:
                                            st.markdown(f"**URL**: [{result['url']}]({result['url']})")
                                        if 'snippet' in result:
                                            st.markdown(f"**Summary**: {result['snippet']}")
                                
                                st.markdown("---")
                    else:
                        st.warning("No results found. Try a different query.")
            else:
                st.warning("Please enter a research query")
    
    # ===================== TAB 5: CODE PLAYGROUND =====================
    with tab5:
        st.markdown("## 💻 Code Playground")
        st.markdown("Write and execute Python code in a safe sandbox environment")
        
        st.info("**Available libraries**: pandas, numpy, json, math, random, datetime")
        
        # Code examples
        example_col1, example_col2 = st.columns(2)
        
        with example_col1:
            if st.button("📊 Data Analysis Example"):
                st.session_state.code_input = """import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 28],
    'salary': [50000, 60000, 75000, 55000]
})

print("Data Overview:")
print(data)
print("\\nAverage Salary:", data['salary'].mean())
print("Oldest Person:", data.loc[data['age'].idxmax(), 'name'])"""
        
        with example_col2:
            if st.button("🧮 Math Calculations"):
                st.session_state.code_input = """import math
import random

# Math operations
print("Square root of 16:", math.sqrt(16))
print("Pi:", math.pi)
print("Sin(90°):", math.sin(math.radians(90)))

# Random numbers
print("\\nRandom number:", random.randint(1, 100))
print("Random choice:", random.choice(['A', 'B', 'C']))"""
        
        # Code editor
        code_input = st.text_area(
            "Python Code:",
            height=300,
            value=st.session_state.get('code_input', '# Write your Python code here\nprint("Hello, World!")'),
            placeholder="Write your Python code here..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            execute_button = st.button("▶️ Run Code", use_container_width=True)
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.code_input = ""
                st.rerun()
        
        if execute_button and code_input:
            st.markdown("### 📤 Output")
            
            with st.spinner("⚙️ Executing code..."):
                result = st.session_state.security.safe_execute(code_input, st.session_state.user_id)
                
                if "🔒" in result:
                    st.error(result)
                elif "⚠️" in result:
                    st.warning(result)
                else:
                    st.code(result, language="text")
                    st.success("✅ Execution completed")
        
        # Safety information
        st.markdown("---")
        st.markdown("### 🔒 Safety Features")
        
        safety_col1, safety_col2 = st.columns(2)
        
        with safety_col1:
            st.markdown("""
            **Restrictions:**
            - File system access blocked
            - Network operations blocked
            - System commands blocked
            - Subprocess operations blocked
            """)
        
        with safety_col2:
            st.markdown("""
            **Limits:**
            - Execution timeout: 30 seconds
            - Rate limit: 5 executions per 5 minutes
            - Maximum code length: 10,000 characters
            - Output limited to 2,000 characters
            """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 2rem;'>
        <p>🤖 AI Assistant Platform | Powered by Advanced AI Technologies</p>
        <p>Built with Streamlit • Enhanced Security • Multi-Source Research</p>
    </div>
    """, unsafe_allow_html=True)

# ===================== RUN APPLICATION =====================
if __name__ == "__main__":
    main() 
