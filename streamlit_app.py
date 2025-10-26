import streamlit as st
import os
import time
import zipfile
import json
import random
import base64
import uuid
from pathlib import Path
from jinja2 import Template
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import FancyBboxPatch, Circle
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Expanded CodeGenie class with AI-powered features
class AICodeGenie:
    def __init__(self):
        self.projects = []
        self.base_path = Path("ai_generated_apps")
        self.base_path.mkdir(exist_ok=True)
        
        # Enhanced color schemes with AI-generated palettes
        self.color_schemes = {
            "Neon Cyber": {"primary": "#00ff9d", "secondary": "#00b8ff", "accent": "#ff00c8"},
            "Solar Flare": {"primary": "#ff6b35", "secondary": "#f7931e", "accent": "#ffd166"},
            "Ocean Depth": {"primary": "#006994", "secondary": "#00a8e8", "accent": "#90e0ef"},
            "Forest Magic": {"primary": "#2d5a27", "secondary": "#4c956c", "accent": "#fefee3"},
            "Purple Haze": {"primary": "#7209b7", "secondary": "#560bad", "accent": "#b5179e"},
            "Sunset Glow": {"primary": "#ff5400", "secondary": "#ff6b6b", "accent": "#feca57"},
            "Ice Queen": {"primary": "#a8dadc", "secondary": "#457b9d", "accent": "#1d3557"}
        }
        
        # AI training data for better idea analysis
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
            "weather_app": {
                "keywords": ['weather', 'forecast', 'temperature', 'climate', 'meteorology', 'temperature'],
                "features": ['forecast', 'locations', 'maps', 'alerts', 'historical']
            },
            "expense_tracker": {
                "keywords": ['expense', 'budget', 'finance', 'money', 'spending', 'tracker', 'financial'],
                "features": ['categories', 'reports', 'budgets', 'export', 'charts']
            },
            "fitness_tracker": {
                "keywords": ['fitness', 'workout', 'exercise', 'health', 'gym', 'training', 'calories'],
                "features": ['workouts', 'progress', 'stats', 'goals', 'nutrition']
            },
            "recipe_book": {
                "keywords": ['recipe', 'cooking', 'food', 'meal', 'kitchen', 'cookbook', 'ingredients'],
                "features": ['categories', 'search', 'ratings', 'shopping list', 'nutrition']
            },
            "book_library": {
                "keywords": ['book', 'library', 'read', 'collection', 'catalog', 'reading', 'novel'],
                "features": ['reviews', 'ratings', 'progress', 'wishlist', 'recommendations']
            },
            "music_player": {
                "keywords": ['music', 'player', 'playlist', 'audio', 'songs', 'tunes', 'melody'],
                "features": ['playlists', 'equalizer', 'lyrics', 'radio', 'favorites']
            }
        }

    def build_ai_application(self, idea: str, app_type: str = "auto", features: list = None, 
                           color_scheme: str = "Neon Cyber", complexity: str = "advanced"):
        try:
            # AI-powered idea analysis
            ai_analysis = self.analyze_idea_with_ai(idea)
            detected_type = ai_analysis["recommended_type"]
            confidence = ai_analysis["confidence"]
            suggested_features = ai_analysis["suggested_features"]
            
            if app_type != "auto" and app_type != "Auto-detect":
                detected_type = app_type.lower().replace(" ", "_")
                confidence = 1.0  # User override gets full confidence
            
            # Merge user features with AI suggestions
            all_features = list(set((features or []) + suggested_features))
            
            project_name = self.generate_ai_project_name(idea, detected_type)
            project_path = self.base_path / project_name
            
            # Create enhanced project structure
            self._create_ai_project_structure(project_path)
            
            # Get color scheme
            colors = self.color_schemes.get(color_scheme, self.color_schemes["Neon Cyber"])
            
            # Generate app based on AI analysis
            generation_result = self.generate_ai_app(
                project_name, idea, detected_type, colors, all_features, complexity
            )
            
            if generation_result["status"] != "success":
                return generation_result
            
            # Create AI-enhanced project info
            project_info = {
                "id": str(uuid.uuid4()),
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
        """AI-powered idea analysis with confidence scoring"""
        idea_lower = idea.lower()
        
        # Calculate scores for each app type
        scores = {}
        for app_type, patterns in self.ai_patterns.items():
            score = 0
            matched_keywords = []
            
            # Keyword matching with weights
            for keyword in patterns["keywords"]:
                if keyword in idea_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            # Feature suggestion based on context
            suggested_features = []
            for feature in patterns["features"]:
                if any(word in idea_lower for word in feature.split()):
                    suggested_features.append(feature.title())
            
            scores[app_type] = {
                "score": score,
                "matched_keywords": matched_keywords,
                "suggested_features": suggested_features[:3]  # Top 3 features
            }
        
        # Find best match
        best_type = max(scores.items(), key=lambda x: x[1]["score"])
        max_score = best_type[1]["score"]
        
        # Calculate confidence (0.0 to 1.0)
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
        """Generate creative, AI-style project names"""
        prefixes = ["Quantum", "Neural", "Smart", "AI", "Cyber", "Hyper", "Ultra", "Mega"]
        suffixes = ["Pro", "Max", "Plus", "X", "360", "Labs", "Studio", "Hub"]
        
        words = [word for word in idea.split()[:3] if len(word) > 2]
        base_name = "_".join(words).lower() if words else "app"
        base_name = ''.join(c for c in base_name if c.isalnum() or c == '_')
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix}_{base_name}_{suffix}_{int(time.time())}"

    def _create_ai_project_structure(self, project_path: Path):
        """Create comprehensive project structure"""
        directories = [
            "frontend",
            "backend",
            "assets/css",
            "assets/js", 
            "assets/images",
            "assets/fonts",
            "data",
            "docs",
            "tests",
            "deployment",
            "config"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_ai_app(self, project_name: str, idea: str, app_type: str, colors: dict, 
                       features: list, complexity: str):
        """AI-powered app generation with multiple app types"""
        project_path = self.base_path / project_name
        
        try:
            if app_type == "todo_app":
                result = self.generate_ai_todo_app(project_name, idea, colors, features, complexity)
            elif app_type == "calculator_app":
                result = self.generate_ai_calculator_app(project_name, idea, colors, features, complexity)
            elif app_type == "expense_tracker":
                result = self.generate_ai_expense_tracker(project_name, idea, colors, features, complexity)
            elif app_type == "fitness_tracker":
                result = self.generate_ai_fitness_tracker(project_name, idea, colors, features, complexity)
            elif app_type == "recipe_book":
                result = self.generate_ai_recipe_book(project_name, idea, colors, features, complexity)
            elif app_type == "weather_app":
                result = self.generate_ai_weather_app(project_name, idea, colors, features, complexity)
            elif app_type == "music_player":
                result = self.generate_ai_music_player(project_name, idea, colors, features, complexity)
            else:
                # Default to enhanced todo app
                result = self.generate_ai_todo_app(project_name, idea, colors, features, complexity)
            
            # Always create these files
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
        """Generate AI-powered expense tracker"""
        project_path = self.base_path / project_name
        
        try:
            # Enhanced HTML with charts and analytics
            html_content = self._render_ai_template("expense_tracker", {
                "project_name": project_name,
                "idea": idea,
                "colors": colors,
                "features": features,
                "has_charts": "Charts" in features,
                "has_budgets": "Budget Tracking" in features,
                "has_categories": "Categories" in features
            })
            
            (project_path / "frontend" / "index.html").write_text(html_content)
            
            # Advanced CSS with financial app styling
            css_content = self._generate_expense_tracker_css(colors, features)
            (project_path / "assets" / "css" / "style.css").write_text(css_content)
            
            # Sophisticated JavaScript with data visualization
            js_content = self._generate_expense_tracker_js(features, complexity)
            (project_path / "assets" / "js" / "app.js").write_text(js_content)
            
            # Sample data for demo
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

    def generate_ai_fitness_tracker(self, project_name: str, idea: str, colors: dict, 
                                  features: list, complexity: str):
        """Generate AI-powered fitness tracker"""
        project_path = self.base_path / project_name
        
        try:
            html_content = self._render_ai_template("fitness_tracker", {
                "project_name": project_name,
                "idea": idea,
                "colors": colors,
                "features": features,
                "has_workouts": "Workout Plans" in features,
                "has_progress": "Progress Tracking" in features,
                "has_nutrition": "Nutrition Tracking" in features
            })
            
            (project_path / "frontend" / "index.html").write_text(html_content)
            
            css_content = self._generate_fitness_tracker_css(colors, features)
            (project_path / "assets" / "css" / "style.css").write_text(css_content)
            
            js_content = self._generate_fitness_tracker_js(features, complexity)
            (project_path / "assets" / "js" / "app.js").write_text(js_content)
            
            if "Sample Data" in features:
                self._create_sample_fitness_data(project_path)
            
            files_created = [
                str(project_path / "frontend" / "index.html"),
                str(project_path / "assets" / "css" / "style.css"),
                str(project_path / "assets" / "js" / "app.js")
            ]
            
            return {
                "status": "success", 
                "files_created": files_created,
                "app_type": "fitness_tracker"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_ai_recipe_book(self, project_name: str, idea: str, colors: dict, 
                              features: list, complexity: str):
        """Generate AI-powered recipe book"""
        project_path = self.base_path / project_name
        
        try:
            html_content = self._render_ai_template("recipe_book", {
                "project_name": project_name,
                "idea": idea,
                "colors": colors,
                "features": features,
                "has_search": "Search" in features,
                "has_categories": "Categories" in features,
                "has_ratings": "Ratings" in features
            })
            
            (project_path / "frontend" / "index.html").write_text(html_content)
            
            css_content = self._generate_recipe_book_css(colors, features)
            (project_path / "assets" / "css" / "style.css").write_text(css_content)
            
            js_content = self._generate_recipe_book_js(features, complexity)
            (project_path / "assets" / "js" / "app.js").write_text(js_content)
            
            if "Sample Data" in features:
                self._create_sample_recipe_data(project_path)
            
            files_created = [
                str(project_path / "frontend" / "index.html"),
                str(project_path / "assets" / "css" / "style.css"),
                str(project_path / "assets" / "js" / "app.js")
            ]
            
            return {
                "status": "success",
                "files_created": files_created,
                "app_type": "recipe_book"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_expense_tracker_css(self, colors: dict, features: list):
        """Generate advanced CSS for expense tracker"""
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
            }
            .chart-bar:hover {
                transform: scale(1.05);
            }"""
        
        return f'''
        :root {{
            --primary: {colors['primary']};
            --secondary: {colors['secondary']};
            --accent: {colors['accent']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
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
        
        .app-header p {{
            opacity: 0.9;
            font-size: 1.1em;
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
            transition: background-color 0.3s ease;
        }}
        
        .expense-item:hover {{
            background: #f8fafc;
        }}
        
        .expense-item:last-child {{
            border-bottom: none;
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
        
        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            
            .expense-item {{
                grid-template-columns: 1fr;
                text-align: center;
                gap: 10px;
            }}
            
            .form-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        '''

    def _generate_expense_tracker_js(self, features: list, complexity: str):
        """Generate advanced JavaScript for expense tracker"""
        chart_js = ""
        if "Charts" in features:
            chart_js = '''
            function renderCharts() {
                const expenses = JSON.parse(localStorage.getItem('expenses')) || [];
                
                // Category spending chart
                const categoryData = {};
                expenses.forEach(expense => {
                    if (expense.type === 'expense') {
                        categoryData[expense.category] = (categoryData[expense.category] || 0) + parseFloat(expense.amount);
                    }
                });
                
                const chartContainer = document.getElementById('spendingChart');
                if (chartContainer) {
                    chartContainer.innerHTML = '';
                    
                    Object.entries(categoryData).forEach(([category, amount], index) => {
                        const bar = document.createElement('div');
                        bar.className = 'chart-bar';
                        bar.style.height = `${Math.min(amount / 10, 100)}%`;
                        bar.style.width = '30px';
                        bar.style.margin = '2px';
                        bar.title = `${category}: $${amount}`;
                        chartContainer.appendChild(bar);
                    });
                }
                
                // Monthly trend
                const monthlyData = {};
                expenses.forEach(expense => {
                    const date = new Date(expense.date);
                    const monthKey = `${date.getFullYear()}-${date.getMonth() + 1}`;
                    monthlyData[monthKey] = (monthlyData[monthKey] || 0) + parseFloat(expense.amount);
                });
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
                
                document.getElementById('clearAll').addEventListener('click', () => {{
                    if (confirm('Are you sure you want to clear all expenses?')) {{
                        this.clearAllExpenses();
                    }}
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
                
                // Reset form
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
            
            clearAllExpenses() {{
                this.expenses = [];
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
        
        // Initialize the tracker when DOM is loaded
        let tracker;
        document.addEventListener('DOMContentLoaded', () => {{
            tracker = new ExpenseTracker();
            // Set default date to today
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
        }});
        '''

    def _create_sample_expense_data(self, project_path: Path):
        """Create sample expense data for demo"""
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
            },
            {
                "id": "3",
                "description": "Electricity Bill",
                "amount": 75.30,
                "type": "expense", 
                "category": "Utilities",
                "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            }
        ]
        
        (project_path / "data" / "sample_expenses.json").write_text(
            json.dumps(sample_expenses, indent=2)
        )

    def _render_ai_template(self, template_type: str, context: dict):
        """Render AI-enhanced templates"""
        templates = {
            "expense_tracker": '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }} - AI Expense Tracker</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="app-container">
        <div class="app-header">
            <h1>💰 {{ project_name }}</h1>
            <p>AI-Powered Expense Tracking • Generated from: "{{ idea }}"</p>
        </div>
        
        <div class="dashboard">
            <div class="stat-card">
                <div class="stat-number" id="totalBalance">$0.00</div>
                <div>Total Balance</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalIncome">$0.00</div>
                <div>Total Income</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalExpenses">$0.00</div>
                <div>Total Expenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="transactionCount">0</div>
                <div>Transactions</div>
            </div>
        </div>
        
        {% if has_charts %}
        <div class="chart-container">
            <h3>📊 Spending by Category</h3>
            <div class="chart" id="spendingChart"></div>
        </div>
        {% endif %}
        
        <div class="expense-form">
            <h3>➕ Add New Transaction</h3>
            <form id="expenseForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="description">Description</label>
                        <input type="text" id="description" required placeholder="What was this for?">
                    </div>
                    <div class="form-group">
                        <label for="amount">Amount ($)</label>
                        <input type="number" id="amount" step="0.01" required placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label for="type">Type</label>
                        <select id="type" required>
                            <option value="expense">Expense</option>
                            <option value="income">Income</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="category">Category</label>
                        <select id="category" required>
                            <option value="Food">Food</option>
                            <option value="Transportation">Transportation</option>
                            <option value="Entertainment">Entertainment</option>
                            <option value="Utilities">Utilities</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="date">Date</label>
                        <input type="date" id="date" required>
                    </div>
                </div>
                <button type="submit" class="btn">Add Transaction</button>
                <button type="button" id="clearAll" class="btn" style="background: #ef4444; margin-left: 10px;">
                    Clear All
                </button>
            </form>
        </div>
        
        <div class="expense-list">
            <h3 style="padding: 20px; margin: 0; border-bottom: 1px solid #e2e8f0;">📋 Recent Transactions</h3>
            <div id="expenseList"></div>
        </div>
    </div>
    
    <script src="assets/js/app.js"></script>
</body>
</html>'''
        }
        
        template = Template(templates.get(template_type, templates["expense_tracker"]))
        return template.render(**context)

    def _create_ai_readme(self, project_path: Path, project_name: str, idea: str, 
                         app_type: str, features: list, colors: dict):
        """Create AI-enhanced README"""
        readme_content = f'''# 🚀 {project_name}

## 🤖 AI-Generated Application

> **Inspired by:** "{idea}"

---

## 🎯 Project Overview

This is an **AI-powered {app_type.replace('_', ' ').title()}** generated by **CodeGenie Pro v3.0** with advanced machine learning analysis.

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

{chr(10).join([f"- ✅ {feature}" for feature in features])}

## 🚀 Quick Start

1. **Open** `frontend/index.html` in your browser
2. **Explore** the AI-generated interface
3. **Customize** the code as needed
4. **Deploy** to your preferred platform

## 📁 Project Structure
