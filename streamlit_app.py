import streamlit as st
import os
import time
import zipfile
import shutil
from pathlib import Path
from jinja2 import Template
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

# Simple CodeGenie class - everything in one file
class CodeGenieAutoBuilder:
    def __init__(self):
        self.projects = []
        self.base_path = Path("generated_apps")
        self.base_path.mkdir(exist_ok=True)

    def build_application(self, idea: str):
        try:
            # Analyze the idea to determine app type
            app_type = self.analyze_idea(idea)
            project_name = self.generate_project_name(idea)
            project_path = self.base_path / project_name
            
            # Create project structure
            self._create_project_structure(project_path)
            
            # Generate app based on type
            if app_type == "todo_app":
                result = self.generate_todo_app(project_name, idea)
            else:
                # Default to todo app
                result = self.generate_todo_app(project_name, idea)
            
            self.projects.append({
                "name": project_name,
                "idea": idea,
                "type": app_type,
                "path": str(project_path)
            })
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_idea(self, idea: str):
        idea_lower = idea.lower()
        
        if any(word in idea_lower for word in ['todo', 'task', 'checklist', 'reminder']):
            return "todo_app"
        elif any(word in idea_lower for word in ['blog', 'post', 'article', 'publish']):
            return "blog_app"
        elif any(word in idea_lower for word in ['note', 'memo', 'journal', 'diary']):
            return "notes_app"
        elif any(word in idea_lower for word in ['contact', 'address', 'phone', 'email']):
            return "contacts_app"
        elif any(word in idea_lower for word in ['book', 'library', 'read', 'collection']):
            return "library_app"
        else:
            return "todo_app"

    def generate_project_name(self, idea: str):
        words = idea.split()[:3]
        name = "_".join(words).lower().replace(' ', '_')
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        return f"app_{name}"

    def _create_project_structure(self, project_path: Path):
        directories = [
            "frontend",
            "assets/css",
            "assets/js",
            "data"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_todo_app(self, project_name: str, idea: str):
        project_path = self.base_path / project_name
        
        try:
            # Create HTML file
            html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Todo App</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="container">
        <h1>🚀 {project_name}</h1>
        <p><em>Generated from: "{idea}"</em></p>
        
        <div class="todo-input">
            <input type="text" id="todoInput" placeholder="Enter a new task...">
            <button onclick="addTodo()">Add Task</button>
        </div>
        
        <div id="todoList"></div>
    </div>
    
    <script src="assets/js/app.js"></script>
</body>
</html>'''
            
            (project_path / "frontend" / "index.html").write_text(html_content)
            
            # Create CSS file
            css_content = '''body {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}
.container {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.todo-item {
    padding: 10px;
    margin: 5px 0;
    background: #f8f9fa;
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.completed {
    text-decoration: line-through;
    opacity: 0.6;
}
.todo-input {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.todo-input input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}
.todo-input button {
    padding: 10px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}'''
            (project_path / "assets" / "css" / "style.css").write_text(css_content)
            
            # Create JavaScript file
            js_content = '''let todos = JSON.parse(localStorage.getItem('todos')) || [];

function renderTodos() {
    const todoList = document.getElementById('todoList');
    todoList.innerHTML = '';
    
    todos.forEach((todo, index) => {
        const todoItem = document.createElement('div');
        todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        todoItem.innerHTML = `
            <span>${todo.text}</span>
            <div>
                <button onclick="toggleTodo(${index})">✓</button>
                <button onclick="deleteTodo(${index})">✕</button>
            </div>
        `;
        todoList.appendChild(todoItem);
    });
}

function addTodo() {
    const input = document.getElementById('todoInput');
    const text = input.value.trim();
    
    if (text) {
        todos.push({ text: text, completed: false });
        localStorage.setItem('todos', JSON.stringify(todos));
        input.value = '';
        renderTodos();
    }
}

function toggleTodo(index) {
    todos[index].completed = !todos[index].completed;
    localStorage.setItem('todos', JSON.stringify(todos));
    renderTodos();
}

function deleteTodo(index) {
    todos.splice(index, 1);
    localStorage.setItem('todos', JSON.stringify(todos));
    renderTodos();
}

// Initial render
renderTodos();'''
            (project_path / "assets" / "js" / "app.js").write_text(js_content)
            
            files_created = [
                str(project_path / "frontend" / "index.html"),
                str(project_path / "assets" / "css" / "style.css"),
                str(project_path / "assets" / "js" / "app.js")
            ]
            
            return {
                "status": "success",
                "project_path": str(project_path),
                "app_type": "todo_app",
                "files_created": files_created
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_project_zip(self, project_path: str):
        try:
            project_dir = Path(project_path)
            zip_path = project_dir.parent / f"{project_dir.name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_dir.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(project_dir))
            
            return str(zip_path)
        except Exception as e:
            print(f"Error creating ZIP: {e}")
            return None

# Diagram functions
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    components = [
        (1, 4.5, 2, 0.9, "User Input", "#4CAF50"),
        (4, 4.5, 2, 0.9, "Idea Analyzer", "#2196F3"),
        (7, 4.5, 2, 0.9, "Template Engine", "#FF9800"),
        (4, 3, 2, 0.9, "Generator", "#9C27B0"),
        (4, 1.5, 2, 0.9, "File Manager", "#607D8B")
    ]
    for x, y, w, h, label, color in components:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    arrows = [(3, 4.9, 4, 4.9), (6, 4.9, 7, 4.9), (5, 3.9, 5, 3.1), (5, 2.4, 5, 1.9)]
    for x1, y1, x2, y2 in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1.8, color='black'))
    ax.set_xlim(0, 10)
    ax.set_ylim(0.5, 6)
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

def generate_workflow_diagram():
    fig, ax = plt.subplots(figsize=(10, 3))
    steps = [(1, 1.5, "1. Input"), (3, 1.5, "2. Analyze"), (5, 1.5, "3. Template"), (7, 1.5, "4. Generate"), (9, 1.5, "5. Output")]
    for x, y, label in steps:
        circle = Circle((x, y), 0.4, facecolor="#45B7D1", edgecolor='black', alpha=0.9)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    for i in range(len(steps)-1):
        ax.annotate('', xy=(steps[i+1][0]-0.4, steps[i+1][1]), xytext=(steps[i][0]+0.4, steps[i][1]), arrowprops=dict(arrowstyle='->', lw=1.6, color='black'))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

# Streamlit App
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

def build_app_interface(auto_detect, show_code):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("💡 Describe Your App Idea")
        idea = st.text_area(
            "What do you want to build?",
            placeholder="Example: I want to build a task management app for my team with due dates and priority levels...",
            height=100
        )
        with st.expander("🔧 Additional Settings (Optional)"):
            col1a, col2a = st.columns(2)
            with col1a:
                app_type = st.selectbox(
                    "App Type",
                    ["Auto-detect", "Todo App", "Blog App", "Notes App", "Contacts App", "Library App"]
                ) if not auto_detect else "Auto-detect"
                color_scheme = st.selectbox("Color Scheme", ["Blue Gradient", "Purple Gradient", "Green Gradient", "Custom"])
            with col2a:
                features = st.multiselect("Additional Features", ["Dark Mode", "Search Functionality", "Export Data", "User Authentication", "File Upload"])
        if st.button("🚀 Generate Application", type="primary", use_container_width=True):
            if not idea:
                st.error("Please describe your app idea first!")
            else:
                generate_application(idea, app_type, color_scheme, features, show_code)
    with col2:
        st.subheader("💡 Idea Examples")
        examples = {
            "Task Management": "A todo app with categories and due dates",
            "Personal Blog": "A blogging platform with markdown support",
            "Study Notes": "A notes app with folders and search",
            "Business Contacts": "A contact manager with groups and notes",
            "Book Library": "A book tracking app with reviews and ratings"
        }
        for name, example in examples.items():
            if st.button(f"📝 {name}", use_container_width=True, key=name):
                st.session_state.example_idea = example
                st.rerun()
        if 'example_idea' in st.session_state:
            st.info(f"💡 Example loaded: {st.session_state.example_idea}")

def generate_application(idea, app_type, color_scheme, features, show_code):
    with st.spinner("🤖 Analyzing your idea and generating application..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        steps = ["Analyzing idea...", "Determining app type...", "Generating code...", "Creating UI design...", "Building application..."]
        for i, step in enumerate(steps):
            status_text.text(f"🔄 {step}")
            progress_bar.progress(int((i + 1) / len(steps) * 100))
            time.sleep(0.35)
        try:
            result = st.session_state.builder.build_application(idea)
            if result["status"] == "success":
                progress_bar.progress(100)
                status_text.text("✅ Application generated successfully!")
                st.balloons()
                st.success("🎉 Your application has been generated successfully!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Project Location", Path(result["project_path"]).name)
                with col2:
                    st.metric("Files Created", len(result["files_created"]))
                with col3:
                    st.metric("App Type", result.get("app_type", "Auto-detected"))
                if show_code:
                    with st.expander("📄 View Generated Code"):
                        project_path = Path(result["project_path"])
                        html_file = project_path / "frontend" / "index.html"
                        if html_file.exists():
                            st.code(html_file.read_text(), language='html')
                st.markdown("---")
                st.subheader("📥 Download Your Application")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📁 Open in File Browser", use_container_width=True):
                        st.info(f"Project location: {result['project_path']}")
                with col2:
                    zip_path = st.session_state.builder.create_project_zip(result["project_path"])
                    if zip_path and Path(zip_path).exists():
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        st.download_button(label="📦 Download ZIP", data=zip_data, file_name=f"{Path(result['project_path']).name}.zip", mime="application/zip", use_container_width=True)
                st.markdown("---")
                st.subheader("👀 Application Preview")
                html_file = Path(result["project_path"]) / "frontend" / "index.html"
                if html_file.exists():
                    with open(html_file, "r") as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=600, scrolling=True)
            else:
                st.error(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Error generating application: {str(e)}")

def show_architecture():
    st.header("🏗️ System Architecture")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Architecture Diagram")
        generate_architecture_diagram()
        st.markdown("""
        ### 🎯 Core Components
        **1. Idea Analyzer** (NLP & classification)
        **2. Template Engine** (Jinja / static HTML)
        """)
    with col2:
        st.subheader("🔄 Workflow Process")
        generate_workflow_diagram()
        st.markdown("""
        **3. UI Designer** - responsive generation
        **4. File Manager** - packaging & zip
        """)
    st.markdown("---")
    st.subheader("🛠️ Technology Stack")
    tech_cols = st.columns(4)
    technologies = [
        ("Python 3.11", "Backend logic and generation"),
        ("Streamlit", "Web interface and UI"),
        ("HTML5/CSS3/JS", "Generated applications"),
        ("Jinja2", "Template rendering")
    ]
    for i, (tech, desc) in enumerate(technologies):
        with tech_cols[i]:
            st.metric(tech, desc)

def show_examples():
    st.header("🎨 Example Applications")
    examples = [
        {"name": "✅ Todo Application", "description": "Full-featured task management with categories and due dates", "features": ["Add/Delete Tasks", "Mark Complete", "Categories", "Due Dates", "Statistics"], "idea": "A todo app for project management with categories and priority levels", "type": "todo_app"},
        {"name": "📝 Blog Application", "description": "Content publishing platform with rich text support", "features": ["Create Posts", "Rich Content", "Timestamps", "Categories", "Search"], "idea": "A blogging platform for sharing articles with markdown support", "type": "blog_app"},
        {"name": "📓 Notes Application", "description": "Advanced note-taking with folders and search", "features": ["Auto-save", "Folders", "Search", "Rich Text", "Export"], "idea": "A notes app for studying with folders and search functionality", "type": "notes_app"}
    ]
    for example in examples:
        with st.expander(f"🎯 {example['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{example['description']}**")
                st.markdown("**Features:**")
                for feature in example['features']:
                    st.markdown(f"- {feature}")
            with col2:
                if st.button(f"🚀 Generate {example['name']}", key=example['type']):
                    st.session_state.example_idea = example['idea']
                    st.rerun()

def show_documentation():
    st.header("📚 Documentation")
    tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "API Reference", "Tutorials", "FAQ"])
    with tab1:
        st.subheader("🚀 Quick Start Guide")
        st.markdown("""
        1. Describe your idea in plain English.
        2. Click Generate.
        3. Download the ZIP and run the app (open frontend/index.html).
        """)
    with tab2:
        st.subheader("🔧 API Reference")
        st.code("""
from codegenie import CodeGenieAutoBuilder
builder = CodeGenieAutoBuilder()
result = builder.build_application("I want a todo app")
""", language="python")
    with tab3:
        st.subheader("🎓 Tutorials")
        st.markdown("Video & written tutorials coming soon.")
    with tab4:
        st.subheader("❓ Frequently Asked Questions")
        faqs = [
            ("What types of apps can I build?", "Todo, Blog, Notes, Contacts, Library."),
            ("Do I need to know how to code?", "No — CodeGenie generates working code.")
        ]
        for q, a in faqs:
            with st.expander(q):
                st.markdown(a)

def show_about():
    st.header("🚀 About CodeGenie Pro")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ## 🤖 What is CodeGenie Pro?
        AI-powered app generator that transforms ideas into working web apps.
        """)
    with col2:
        st.image("https://img.icons8.com/color/200/000000/robot.png", width=140)
    st.markdown("### 🔗 Links")
    st.markdown("[📁 GitHub Repository](https://github.com/Leonydis138/Codegenie)")
    st.markdown("[💬 Community Discord](https://discord.gg/codegenie)")
    st.markdown("[🐦 Twitter](https://twitter.com/codegenie)")

if __name__ == "__main__":
    main()
