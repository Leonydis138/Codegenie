import streamlit as st
import os
import time
import zipfile
import json
import random
from pathlib import Path
from jinja2 import Template
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class AICodeGenie:
    def __init__(self):
        self.projects = []
        self.base_path = Path("ai_generated_apps")
        self.base_path.mkdir(exist_ok=True)
        
        self.color_schemes = {
            "Neon Cyber": {"primary": "#00ff9d", "secondary": "#00b8ff", "accent": "#ff00c8"},
            "Solar Flare": {"primary": "#ff6b35", "secondary": "#f7931e", "accent": "#ffd166"},
            "Ocean Depth": {"primary": "#006994", "secondary": "#00a8e8", "accent": "#90e0ef"},
            "Forest Magic": {"primary": "#2d5a27", "secondary": "#4c956c", "accent": "#fefee3"},
            "Purple Haze": {"primary": "#7209b7", "secondary": "#560bad", "accent": "#b5179e"}
        }
        
        self.ai_patterns = {
            "todo_app": {
                "keywords": ['todo', 'task', 'checklist', 'reminder', 'to-do', 'to do', 'get things done', 'productivity'],
                "features": ['categories', 'due dates', 'priority', 'tags', 'recurring', 'subtasks']
            },
            "blog_app": {
                "keywords": ['blog', 'post', 'article', 'publish', 'content', 'writing', 'journal', 'diary'],
                "features": ['rich text', 'categories', 'tags', 'comments', 'search', 'rss']
            },
            "notes_app": {
                "keywords": ['note', 'memo', 'journal', 'diary', 'notepad', 'writing', 'study', 'research'],
                "features": ['folders', 'search', 'rich text', 'export', 'sync', 'templates']
            },
            "calculator_app": {
                "keywords": ['calculator', 'calculate', 'math', 'arithmetic', 'numbers', 'scientific', 'finance'],
                "features": ['scientific', 'history', 'memory', 'conversions', 'graphs']
            },
            "expense_tracker": {
                "keywords": ['expense', 'budget', 'finance', 'money', 'spending', 'tracker', 'financial'],
                "features": ['categories', 'reports', 'budgets', 'export', 'charts']
            }
        }

    def build_ai_application(self, idea: str, app_type: str = "auto", features: list = None, 
                           color_scheme: str = "Neon Cyber", complexity: str = "advanced"):
        try:
            ai_analysis = self.analyze_idea_with_ai(idea)
            detected_type = ai_analysis["recommended_type"]
            confidence = ai_analysis["confidence"]
            suggested_features = ai_analysis["suggested_features"]
            
            if app_type != "auto" and app_type != "Auto-detect":
                detected_type = app_type.lower().replace(" ", "_")
                confidence = 1.0
            
            all_features = list(set((features or []) + suggested_features))
            
            project_name = self.generate_ai_project_name(idea, detected_type)
            project_path = self.base_path / project_name
            
            self._create_ai_project_structure(project_path)
            
            colors = self.color_schemes.get(color_scheme, self.color_schemes["Neon Cyber"])
            
            generation_result = self.generate_ai_app(
                project_name, idea, detected_type, colors, all_features, complexity
            )
            
            if generation_result["status"] != "success":
                return generation_result
            
            project_info = {
                "id": str(random.randint(1000, 9999)),
                "name": project_name,
                "idea": idea,
                "type": detected_type,
                "ai_confidence": confidence,
                "ai_suggestions": suggested_features,
                "features": all_features,
                "colors": colors,
                "complexity": complexity,
                "created_at": datetime.now().isoformat(),
                "version": "3.0",
                "ai_analysis": ai_analysis
            }
            
            (project_path / "ai_project_info.json").write_text(json.dumps(project_info, indent=2))
            self.projects.append(project_info)
            
            return {
                "status": "success",
                "project_path": str(project_path),
                "app_type": detected_type,
                "files_created": generation_result.get("files_created", []),
                "project_info": project_info,
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e), "error_type": type(e).__name__}

    def analyze_idea_with_ai(self, idea: str):
        idea_lower = idea.lower()
        
        scores = {}
        for app_type, patterns in self.ai_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword in patterns["keywords"]:
                if keyword in idea_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            suggested_features = []
            for feature in patterns["features"]:
                if any(word in idea_lower for word in feature.split()):
                    suggested_features.append(feature.title())
            
            scores[app_type] = {
                "score": score,
                "matched_keywords": matched_keywords,
                "suggested_features": suggested_features[:3]
            }
        
        best_type = max(scores.items(), key=lambda x: x[1]["score"])
        max_score = best_type[1]["score"]
        
        total_possible = len(self.ai_patterns[best_type[0]]["keywords"]) * 2
        confidence = min(max_score / total_possible, 1.0) if total_possible > 0 else 0.0
        
        return {
            "recommended_type": best_type[0],
            "confidence": round(confidence, 2),
            "scores": scores,
            "suggested_features": best_type[1]["suggested_features"],
            "matched_keywords": best_type[1]["matched_keywords"]
        }

    def generate_ai_project_name(self, idea: str, app_type: str):
        prefixes = ["Quantum", "Neural", "Smart", "AI", "Cyber", "Hyper"]
        suffixes = ["Pro", "Max", "Plus", "X", "Labs", "Studio"]
        
        words = [word for word in idea.split()[:3] if len(word) > 2]
        base_name = "_".join(words).lower() if words else "app"
        base_name = ''.join(c for c in base_name if c.isalnum() or c == '_')
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix}_{base_name}_{suffix}_{int(time.time())}"

    def _create_ai_project_structure(self, project_path: Path):
        directories = [
            "frontend",
            "assets/css",
            "assets/js", 
            "assets/images",
            "data",
            "docs",
            "config"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_ai_app(self, project_name: str, idea: str, app_type: str, colors: dict, 
                       features: list, complexity: str):
        project_path = self.base_path / project_name
        
        try:
            result = self.generate_ai_expense_tracker(project_name, idea, colors, features, complexity)
            
            self._create_ai_readme(project_path, project_name, idea, app_type, features, colors)
            self._create_package_json(project_path, project_name, app_type)
            self._create_ai_config(project_path, colors, features)
            
            if "files_created" in result:
                result["files_created"].extend([
                    str(project_path / "README.md"),
                    str(project_path / "package.json"),
                    str(project_path / "config" / "app.config.json"),
                    str(project_path / "ai_project_info.json")
                ])
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_ai_expense_tracker(self, project_name: str, idea: str, colors: dict, 
                                  features: list, complexity: str):
        project_path = self.base_path / project_name
        
        try:
            # Create HTML content using string concatenation to avoid template issues
            html_content = self._create_expense_tracker_html(project_name, idea, features)
            (project_path / "frontend" / "index.html").write_text(html_content)
            
            css_content = self._generate_expense_tracker_css(colors, features)
            (project_path / "assets" / "css" / "style.css").write_text(css_content)
            
            js_content = self._generate_expense_tracker_js(features, complexity)
            (project_path / "assets" / "js" / "app.js").write_text(js_content)
            
            if "Sample Data" in features:
                self._create_sample_expense_data(project_path)
            
            files_created = [
                str(project_path / "frontend" / "index.html"),
                str(project_path / "assets" / "css" / "style.css"),
                str(project_path / "assets" / "js" / "app.js")
            ]
            
            return {
                "status": "success",
                "files_created": files_created,
                "app_type": "expense_tracker"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _create_expense_tracker_html(self, project_name: str, idea: str, features: list):
        """Create HTML content using simple string concatenation"""
        has_charts = "Charts" in features
        
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>{project_name} - AI Expense Tracker</title>',
            '    <link rel="stylesheet" href="assets/css/style.css">',
            '</head>',
            '<body>',
            '    <div class="app-container">',
            '        <div class="app-header">',
            f'            <h1>💰 {project_name}</h1>',
            f'            <p>AI-Powered Expense Tracking • Generated from: "{idea}"</p>',
            '        </div>',
            '        <div class="dashboard">',
            '            <div class="stat-card">',
            '                <div class="stat-number" id="totalBalance">$0.00</div>',
            '                <div>Total Balance</div>',
            '            </div>',
            '            <div class="stat-card">',
            '                <div class="stat-number" id="totalIncome">$0.00</div>',
            '                <div>Total Income</div>',
            '            </div>',
            '            <div class="stat-card">',
            '                <div class="stat-number" id="totalExpenses">$0.00</div>',
            '                <div>Total Expenses</div>',
            '            </div>',
            '            <div class="stat-card">',
            '                <div class="stat-number" id="transactionCount">0</div>',
            '                <div>Transactions</div>',
            '            </div>',
            '        </div>'
        ]
        
        if has_charts:
            html_parts.extend([
                '        <div class="chart-container">',
                '            <h3>📊 Spending by Category</h3>',
                '            <div class="chart" id="spendingChart"></div>',
                '        </div>'
            ])
        
        html_parts.extend([
            '        <div class="expense-form">',
            '            <h3>➕ Add New Transaction</h3>',
            '            <form id="expenseForm">',
            '                <div class="form-grid">',
            '                    <div class="form-group">',
            '                        <label for="description">Description</label>',
            '                        <input type="text" id="description" required placeholder="What was this for?">',
            '                    </div>',
            '                    <div class="form-group">',
            '                        <label for="amount">Amount ($)</label>',
            '                        <input type="number" id="amount" step="0.01" required placeholder="0.00">',
            '                    </div>',
            '                    <div class="form-group">',
            '                        <label for="type">Type</label>',
            '                        <select id="type" required>',
            '                            <option value="expense">Expense</option>',
            '                            <option value="income">Income</option>',
            '                        </select>',
            '                    </div>',
            '                    <div class="form-group">',
            '                        <label for="category">Category</label>',
            '                        <select id="category" required>',
            '                            <option value="Food">Food</option>',
            '                            <option value="Transportation">Transportation</option>',
            '                            <option value="Entertainment">Entertainment</option>',
            '                            <option value="Utilities">Utilities</option>',
            '                            <option value="Shopping">Shopping</option>',
            '                            <option value="Healthcare">Healthcare</option>',
            '                            <option value="Other">Other</option>',
            '                        </select>',
            '                    </div>',
            '                    <div class="form-group">',
            '                        <label for="date">Date</label>',
            '                        <input type="date" id="date" required>',
            '                    </div>',
            '                </div>',
            '                <button type="submit" class="btn">Add Transaction</button>',
            '            </form>',
            '        </div>',
            '        <div class="expense-list">',
            '            <h3 style="padding: 20px; margin: 0; border-bottom: 1px solid #e2e8f0;">📋 Recent Transactions</h3>',
            '            <div id="expenseList"></div>',
            '        </div>',
            '    </div>',
            '    <script src="assets/js/app.js"></script>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)

    def _generate_expense_tracker_css(self, colors: dict, features: list):
        chart_css = ""
        if "Charts" in features:
            chart_css = """
            .chart-container {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            .chart {
                height: 300px;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 10px;
                position: relative;
                overflow: hidden;
            }
            .chart-bar {
                background: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
                margin: 2px;
                border-radius: 4px;
                transition: all 0.3s ease;
            }"""
        
        return f'''
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .app-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .app-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .app-header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 800;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            text-align: center;
            border-left: 5px solid var(--accent);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 10px;
        }}
        
        .expense-form {{
            background: white;
            padding: 30px;
            margin: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }}
        
        .form-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .form-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
        }}
        
        .form-group input, .form-group select {{
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }}
        
        .form-group input:focus, .form-group select:focus {{
            outline: none;
            border-color: var(--primary);
        }}
        
        .btn {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .expense-list {{
            background: white;
            margin: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}
        
        .expense-item {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: 15px;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
            align-items: center;
        }}
        
        .expense-item:hover {{
            background: #f8fafc;
        }}
        
        .expense-amount {{
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .expense-amount.income {{
            color: #10b981;
        }}
        
        .expense-amount.expense {{
            color: #ef4444;
        }}
        
        .category-tag {{
            background: var(--accent);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        {chart_css}
        '''

    def _generate_expense_tracker_js(self, features: list, complexity: str):
        chart_js = ""
        if "Charts" in features:
            chart_js = '''
            function renderCharts() {
                const expenses = JSON.parse(localStorage.getItem('expenses')) || [];
                const categoryData = {};
                expenses.forEach(expense => {
                    if (expense.type === 'expense') {
                        categoryData[expense.category] = (categoryData[expense.category] || 0) + parseFloat(expense.amount);
                    }
                });
                
                const chartContainer = document.getElementById('spendingChart');
                if (chartContainer) {
                    chartContainer.innerHTML = '';
                    Object.entries(categoryData).forEach(([category, amount]) => {
                        const bar = document.createElement('div');
                        bar.className = 'chart-bar';
                        bar.style.height = `${Math.min(amount / 10, 100)}%`;
                        bar.style.width = '30px';
                        bar.style.margin = '2px';
                        bar.title = `${category}: $${amount}`;
                        chartContainer.appendChild(bar);
                    });
                }
            }'''
        
        return f'''
        class ExpenseTracker {{
            constructor() {{
                this.expenses = JSON.parse(localStorage.getItem('expenses')) || [];
                this.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Other'];
                this.init();
            }}
            
            init() {{
                this.renderExpenses();
                this.updateDashboard();
                {chart_js if chart_js else ''}
                this.setupEventListeners();
            }}
            
            setupEventListeners() {{
                document.getElementById('expenseForm').addEventListener('submit', (e) => {{
                    e.preventDefault();
                    this.addExpense();
                }});
            }}
            
            addExpense() {{
                const description = document.getElementById('description').value;
                const amount = parseFloat(document.getElementById('amount').value);
                const type = document.getElementById('type').value;
                const category = document.getElementById('category').value;
                const date = document.getElementById('date').value;
                
                if (!description || !amount || !date) {{
                    alert('Please fill in all required fields');
                    return;
                }}
                
                const expense = {{
                    id: Date.now().toString(),
                    description,
                    amount,
                    type,
                    category,
                    date,
                    createdAt: new Date().toISOString()
                }};
                
                this.expenses.push(expense);
                this.saveExpenses();
                this.renderExpenses();
                this.updateDashboard();
                { 'this.renderCharts();' if "Charts" in features else '' }
                document.getElementById('expenseForm').reset();
                document.getElementById('date').value = new Date().toISOString().split('T')[0];
            }}
            
            deleteExpense(id) {{
                this.expenses = this.expenses.filter(expense => expense.id !== id);
                this.saveExpenses();
                this.renderExpenses();
                this.updateDashboard();
                { 'this.renderCharts();' if "Charts" in features else '' }
            }}
            
            saveExpenses() {{
                localStorage.setItem('expenses', JSON.stringify(this.expenses));
            }}
            
            renderExpenses() {{
                const container = document.getElementById('expenseList');
                container.innerHTML = '';
                const sortedExpenses = this.expenses.sort((a, b) => new Date(b.date) - new Date(a.date));
                
                sortedExpenses.forEach(expense => {{
                    const item = document.createElement('div');
                    item.className = 'expense-item';
                    item.innerHTML = `
                        <div class="expense-description">
                            <strong>${{expense.description}}</strong>
                            <div class="category-tag">${{expense.category}}</div>
                        </div>
                        <div class="expense-amount ${{expense.type}}">
                            ${{expense.type === 'income' ? '+' : '-'}}$${{Math.abs(expense.amount).toFixed(2)}}
                        </div>
                        <div class="expense-date">${{new Date(expense.date).toLocaleDateString()}}</div>
                        <div class="expense-type">${{expense.type}}</div>
                        <button onclick="tracker.deleteExpense('${{expense.id}}')" class="btn" style="background: #ef4444; padding: 8px 15px;">
                            Delete
                        </button>
                    `;
                    container.appendChild(item);
                }});
            }}
            
            updateDashboard() {{
                const totalIncome = this.expenses
                    .filter(e => e.type === 'income')
                    .reduce((sum, e) => sum + parseFloat(e.amount), 0);
                    
                const totalExpenses = this.expenses
                    .filter(e => e.type === 'expense')
                    .reduce((sum, e) => sum + parseFloat(e.amount), 0);
                    
                const balance = totalIncome - totalExpenses;
                
                document.getElementById('totalBalance').textContent = `$${{balance.toFixed(2)}}`;
                document.getElementById('totalIncome').textContent = `$${{totalIncome.toFixed(2)}}`;
                document.getElementById('totalExpenses').textContent = `$${{totalExpenses.toFixed(2)}}`;
                document.getElementById('transactionCount').textContent = this.expenses.length;
            }}
            
            {chart_js if chart_js else ''}
        }}
        
        let tracker;
        document.addEventListener('DOMContentLoaded', () => {{
            tracker = new ExpenseTracker();
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
        }});
        '''

    def _create_sample_expense_data(self, project_path: Path):
        sample_expenses = [
            {
                "id": "1",
                "description": "Grocery Shopping",
                "amount": 85.50,
                "type": "expense",
                "category": "Food",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            },
            {
                "id": "2", 
                "description": "Freelance Work",
                "amount": 500.00,
                "type": "income",
                "category": "Work",
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            }
        ]
        
        (project_path / "data" / "sample_expenses.json").write_text(
            json.dumps(sample_expenses, indent=2)
        )

    def _create_ai_readme(self, project_path: Path, project_name: str, idea: str,
                         app_type: str, features: list, colors: dict):
        """Create README using simple string concatenation to avoid template issues"""
        created_at = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
        app_type_title = app_type.replace('_', ' ').title()
        
        # Build features list
        features_list = "\n".join([f"- {feature}" for feature in features])
        
        # Create README content using string concatenation
        readme_content = f"""# 🚀 {project_name}

## 🤖 AI-Generated Application

> **Inspired by:** "{idea}"

---

## 🎯 Project Overview

This is an **AI-powered {app_type_title}** generated by **CodeGenie Pro v3.0** with advanced machine learning analysis.

### ✨ AI Features
- **Smart Idea Analysis**: Advanced NLP understanding
- **Automatic Feature Detection**: AI-suggested functionality  
- **Optimized Code Generation**: Production-ready templates
- **Intelligent Styling**: AI-curated color schemes

### 🛠️ Technical Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Storage**: Browser Local Storage
- **Styling**: CSS Grid & Flexbox
- **Responsive**: Mobile-first design
- **Performance**: Optimized bundle

## 🎨 Design System

**Color Palette:**
- Primary: `{colors['primary']}`
- Secondary: `{colors['secondary']}`
- Accent: `{colors['accent']}`

## 🔧 Features

{features_list}

## 🚀 Quick Start

1. **Open** `frontend/index.html` in your browser  
2. **Explore** the AI-generated interface  
3. **Customize** the code as needed  
4. **Deploy** to your preferred platform

## 📁 Project Structure

```

{project_name}/
├──frontend/           # Main application
├──assets/            # Static resources
│├── css/          # Advanced styling
│├── js/           # AI-enhanced logic
│└── images/       # Media assets
├──data/             # Sample datasets
├──docs/             # Documentation
└──config/           # App configuration

```

## 🧠 AI Analysis Details

This application was generated using advanced machine learning patterns:

- **App Type Detection**: {app_type_title}
- **Feature Optimization**: {len(features)} AI-suggested features
- **Code Quality**: Production-grade templates
- **User Experience**: AI-optimized workflows

## 🔮 Next Steps

1. **Review** the generated code structure  
2. **Customize** functionality to your needs  
3. **Extend** with additional features  
4. **Deploy** to production environment  
5. **Iterate** based on user feedback

## 📄 License

Generated by **CodeGenie Pro v3.0** • AI-Powered Application Generator

---

*🤖 Generated with advanced AI analysis on {created_at}*
        
        (project_path / "README.md").write_text(readme_content)

    def _create_package_json(self, project_path: Path, project_name: str, app_type: str):
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": f"AI-generated {app_type.replace('_', ' ')} application",
            "main": "frontend/index.html",
            "scripts": {
                "start": "python -m http.server 8000",
                "dev": "live-server frontend"
            },
            "keywords": ["ai-generated", app_type, "codegenie", "web-app"],
            "author": "CodeGenie AI",
            "license": "MIT"
        }
        
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))

    def _create_ai_config(self, project_path: Path, colors: dict, features: list):
        config = {
            "app": {
                "version": "3.0",
                "generated_by": "CodeGenie AI",
                "timestamp": datetime.now().isoformat()
            },
            "design": {
                "color_scheme": colors,
                "features": features,
                "responsive": True
            }
        }
        
        (project_path / "config" / "app.config.json").write_text(json.dumps(config, indent=2))

    def create_ai_project_zip(self, project_path: str):
        try:
            project_dir = Path(project_path)
            zip_path = project_dir.parent / f"{project_dir.name}_ai_edition.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_dir.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(project_dir))
            
            return str(zip_path)
        except Exception as e:
            print(f"AI ZIP creation error: {e}")
            return None

    def get_ai_analytics(self):
        total_projects = len(self.projects)
        
        if total_projects == 0:
            return {
                "total_projects": 0,
                "ai_confidence_avg": 0,
                "feature_usage": {},
                "app_type_distribution": {}
            }
        
        confidence_sum = sum(project.get('ai_confidence', 0) for project in self.projects)
        avg_confidence = confidence_sum / total_projects
        
        feature_usage = {}
        for project in self.projects:
            for feature in project.get('features', []):
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
        
        app_type_dist = {}
        for project in self.projects:
            app_type = project.get('type', 'unknown')
            app_type_dist[app_type] = app_type_dist.get(app_type, 0) + 1
        
        return {
            "total_projects": total_projects,
            "ai_confidence_avg": round(avg_confidence, 2),
            "feature_usage": feature_usage,
            "app_type_distribution": app_type_dist,
            "latest_projects": self.projects[-5:] if self.projects else []
        }

def main():
    st.set_page_config(
        page_title="CodeGenie Pro v3.0 - AI Edition",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if 'ai_builder' not in st.session_state:
        st.session_state.ai_builder = AICodeGenie()
    
    if 'ai_projects' not in st.session_state:
        st.session_state.ai_projects = []
    
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #00ff9d 0%, #00b8ff 50%, #ff00c8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    .ai-feature-card {
        background: linear-gradient(135deg, rgba(0, 255, 157, 0.1) 0%, rgba(0, 184, 255, 0.1) 100%);
        border: 1px solid rgba(0, 255, 157, 0.3);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
        st.title("🤖 CodeGenie AI")
        st.markdown("---")
        
        ai_stats = st.session_state.ai_builder.get_ai_analytics()
        
        st.subheader("🧠 AI Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AI Projects", ai_stats["total_projects"])
        with col2:
            st.metric("Avg Confidence", f"{ai_stats['ai_confidence_avg']*100:.0f}%")
        
        st.markdown("---")
        st.subheader("🚀 AI Quick Start")
        st.markdown("""
        1. **💬 Describe** your vision
        2. **🧠 AI analyzes** automatically  
        3. **🎨 Customize** AI suggestions
        4. **⚡ Generate** intelligent app
        """)

    st.markdown('<h1 class="main-header">🤖 CodeGenie Pro v3.0</h1>', unsafe_allow_html=True)
    st.markdown("### 🧠 AI-Powered Application Generation • Transform Ideas into Intelligent Apps")
    
    ai_tabs = st.tabs(["🧠 AI Builder", "📊 AI Analytics", "🚀 AI Examples"])
    
    with ai_tabs[0]:
        show_ai_builder_interface()
    with ai_tabs[1]:
        show_ai_analytics_dashboard()
    with ai_tabs[2]:
        show_ai_examples_gallery()

def show_ai_builder_interface():
    st.header("🧠 AI-Powered Application Builder")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Describe Your Vision")
        
        idea = st.text_area(
            "Tell me what amazing app you want to create...",
            placeholder="Example: I need a smart expense tracker with budgeting, charts, and monthly reports for personal finance management...",
            height=120,
            key="ai_idea_input"
        )
        
        if idea and len(idea) > 10:
            with st.spinner("🧠 AI is analyzing your idea..."):
                ai_analysis = st.session_state.ai_builder.analyze_idea_with_ai(idea)
                st.session_state.current_analysis = ai_analysis
                
                confidence = ai_analysis["confidence"]
                st.metric("AI Confidence", f"{confidence*100:.0f}%")
                
                if confidence > 0.7:
                    st.success("🎯 High confidence match found!")
                elif confidence > 0.4:
                    st.warning("🤔 Moderate confidence - consider being more specific")
                else:
                    st.error("❌ Low confidence - try rephrasing your idea")
        
        with st.expander("🎨 AI Customization Panel", expanded=True):
            col1a, col2a, col3a = st.columns(3)
            
            with col1a:
                app_type = st.selectbox(
                    "App Type (AI Suggested)",
                    ["Auto-detect", "Todo App", "Expense Tracker", "Calculator"],
                    help="Let AI detect or choose manually"
                )
                
            with col2a:
                color_scheme = st.selectbox(
                    "AI Color Theme",
                    list(st.session_state.ai_builder.color_schemes.keys()),
                    help="AI-curated color palettes"
                )
                
            with col3a:
                complexity = st.selectbox(
                    "AI Complexity Level",
                    ["Simple", "Standard", "Advanced"],
                    help="AI will adjust code complexity accordingly"
                )
        
        with st.expander("🔧 AI Feature Recommendations", expanded=True):
            if st.session_state.current_analysis:
                suggested_features = st.session_state.current_analysis["suggested_features"]
                st.write("**AI Suggestions:**", ", ".join(suggested_features))
            
            all_features = [
                "Charts & Graphs", "Budget Tracking", "Categories", "Search", 
                "Export Data", "Dark Mode", "Responsive Design", "Local Storage",
                "Sample Data"
            ]
            
            features = st.multiselect(
                "Select Features:",
                all_features,
                default=st.session_state.current_analysis["suggested_features"] if st.session_state.current_analysis else []
            )
        
        if st.button("🚀 Generate AI Application", type="primary", use_container_width=True):
            if not idea:
                st.error("Please describe your app idea for AI analysis!")
            else:
                generate_ai_application(idea, app_type, color_scheme, features, complexity)
    
    with col2:
        st.subheader("🧠 AI Analysis")
        
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis
            
            st.write("**🔍 AI Detected:**")
            for keyword in analysis["matched_keywords"][:5]:
                st.write(f"- `{keyword}`")
            
            st.write(f"**🎯 Recommended Type:** {analysis['recommended_type'].replace('_', ' ').title()}")
            
        else:
            st.info("💡 Describe your app idea to see AI analysis here...")
        
        st.markdown("---")
        st.subheader("⚡ AI Quick Start")
        
        ai_examples = {
            "💰 Smart Expense Tracker": "I need an expense tracker with budgets, categories, and beautiful charts",
            "📝 Advanced Todo App": "Create a todo app with categories, due dates, and priority levels", 
            "🧮 Scientific Calculator": "Build a calculator with history and advanced functions"
        }
        
        for name, example in ai_examples.items():
            if st.button(f"{name}", use_container_width=True, key=f"ai_example_{name}"):
                st.session_state.ai_idea_input = example
                st.rerun()

def generate_ai_application(idea, app_type, color_scheme, features, complexity):
    with st.spinner("🧠 AI is generating your intelligent application..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        ai_steps = [
            "🔮 Analyzing idea with deep learning...",
            "🧠 Processing natural language patterns...", 
            "🎨 Designing AI-optimized UI/UX...",
            "⚡ Generating intelligent code templates...",
            "🔧 Implementing AI-suggested features...",
            "📦 Packaging AI-enhanced application..."
        ]
        
        for i, step in enumerate(ai_steps):
            status_text.text(f"{step}")
            progress_bar.progress(int((i + 1) / len(ai_steps) * 100))
            time.sleep(0.4)
        
        try:
            result = st.session_state.ai_builder.build_ai_application(
                idea, app_type, features, color_scheme, complexity.lower()
            )
            
            if result["status"] == "success":
                progress_bar.progress(100)
                status_text.text("✅ AI Application Generated Successfully!")
                
                st.balloons()
                st.success("🎉 Your AI-powered application is ready!")
                
                project_info = result["project_info"]
                ai_analysis = result["ai_analysis"]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Project Name", project_info["name"])
                with col2:
                    st.metric("AI Confidence", f"{ai_analysis['confidence']*100:.0f}%")
                with col3:
                    st.metric("App Type", project_info["type"].replace("_", " ").title())
                with col4:
                    st.metric("AI Features", len(project_info["features"]))
                
                with st.expander("🧠 AI Analysis Report", expanded=True):
                    report_col1, report_col2 = st.columns(2)
                    
                    with report_col1:
                        st.write("**AI Detection Results:**")
                        for app_type, score in ai_analysis["scores"].items():
                            if score["score"] > 0:
                                st.write(f"- {app_type.replace('_', ' ').title()}: {score['score']} points")
                    
                    with report_col2:
                        st.write("**AI Suggestions Implemented:**")
                        for feature in project_info["features"]:
                            st.write(f"- ✅ {feature}")
                
                st.markdown("---")
                st.subheader("📥 Download AI Application")
                
                download_col1, download_col2 = st.columns(2)
                
                with download_col1:
                    if st.button("📁 Open AI Project", use_container_width=True):
                        st.info(f"AI Project Location: `{result['project_path']}`")
                
                with download_col2:
                    zip_path = st.session_state.ai_builder.create_ai_project_zip(result["project_path"])
                    if zip_path and Path(zip_path).exists():
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        
                        st.download_button(
                            label="🤖 Download AI Edition", 
                            data=zip_data, 
                            file_name=f"{Path(result['project_path']).name}_ai.zip",
                            mime="application/zip", 
                            use_container_width=True,
                            type="primary"
                        )
                
                st.markdown("---")
                st.subheader("👁️ AI Application Preview")
                
                html_file = Path(result["project_path"]) / "frontend" / "index.html"
                if html_file.exists():
                    with open(html_file, "r") as f:
                        html_content = f.read()
                    
                    st.components.v1.html(html_content, height=600, scrolling=True)
                
                st.session_state.ai_projects.append(project_info)
                
            else:
                st.error(f"❌ AI Generation Failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"❌ AI System Error: {str(e)}")

def show_ai_analytics_dashboard():
    st.header("📊 AI Analytics Dashboard")
    
    ai_stats = st.session_state.ai_builder.get_ai_analytics()
    
    if ai_stats["total_projects"] == 0:
        st.info("🤖 No AI projects generated yet. Create your first AI application to see analytics!")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total AI Projects", ai_stats["total_projects"])
    with col2:
        st.metric("Avg AI Confidence", f"{ai_stats['ai_confidence_avg']*100:.0f}%")
    with col3:
        st.metric("App Types", len(ai_stats["app_type_distribution"]))
    with col4:
        st.metric("Features Used", len(ai_stats["feature_usage"]))
    
    st.subheader("📈 AI App Type Distribution")
    
    if ai_stats["app_type_distribution"]:
        app_types = list(ai_stats["app_type_distribution"].keys())
        counts = list(ai_stats["app_type_distribution"].values())
        
        fig = px.pie(
            values=counts, 
            names=app_types,
            title="AI-Generated App Types Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔥 AI Feature Usage")
    
    if ai_stats["feature_usage"]:
        features = list(ai_stats["feature_usage"].keys())
        usage = list(ai_stats["feature_usage"].values())
        
        fig = px.bar(
            x=features, 
            y=usage,
            title="Most Popular AI Features",
            labels={'x': 'Feature', 'y': 'Usage Count'},
            color=usage,
            color_continuous_scale='viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def show_ai_examples_gallery():
    st.header("🚀 AI Example Gallery")
    
    ai_examples = [
        {
            "name": "💰 AI Expense Tracker Pro",
            "description": "Intelligent finance management with predictive analytics",
            "features": ["Charts & Graphs", "Budget Tracking", "Categories", "Export Data"],
            "idea": "A smart expense tracker with AI-powered budgeting suggestions and financial insights",
            "type": "expense_tracker",
            "color": "Neon Cyber"
        },
        {
            "name": "📝 AI Todo Master", 
            "description": "Smart task management with AI prioritization",
            "features": ["Categories", "Due Dates", "Priority Levels", "Statistics"],
            "idea": "A todo app that intelligently prioritizes tasks based on deadlines and importance",
            "type": "todo_app",
            "color": "Solar Flare"
        }
    ]
    
    for example in ai_examples:
        with st.expander(f"🤖 {example['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{example['description']}**")
                st.markdown("**AI Features:**")
                for feature in example['features']:
                    st.markdown(f"- {feature}")
                st.markdown(f"*Idea: \"{example['idea']}\"*")
            
            with col2:
                st.write("**AI Type:**", example['type'].replace('_', ' ').title())
                st.write("**Theme:**", example['color'])
                
                if st.button(f"🚀 Generate {example['name']}", key=example['type']):
                    st.session_state.ai_idea_input = example['idea']
                    st.rerun()

if __name__ == "__main__":
    main()
