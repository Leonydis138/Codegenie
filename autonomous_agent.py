import uuid
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Import from other modules
# from core_infrastructure import EnhancedDatabaseManager, EnhancedSecurityManager, EnhancedResearchEngine
# from analytics_engine import AdvancedAnalyticsEngine

# ===================== AUTONOMOUS AGENT =====================
class EnhancedAutonomousAgent:
    def __init__(self, db_manager, security, research_engine, analytics, user_id: str = "default"):
        self.user_id = user_id
        self.db_manager = db_manager
        self.security = security
        self.research_engine = research_engine
        self.analytics = analytics
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        self.context_memory = {}
        
        self._init_user_session()
    
    def _init_user_session(self):
        """Initialize user session"""
        try:
            self.db_manager.log_analytics(self.user_id, "session_start", self.session_id)
        except Exception as e:
            logger.error(f"Session init error: {e}")
    
    def execute_enhanced_goal(self, goal: str, context: Dict = None) -> Tuple[str, Dict]:
        """Execute goal with comprehensive capabilities"""
        goal = self.security.sanitize_input(goal, 3000)
        if not goal:
            return "❌ Please provide a valid goal", {}
        
        if not self.security.check_rate_limit(self.user_id, "goal_execution", 20, 300):
            return "🔒 Rate limit exceeded. Please wait.", {}
        
        try:
            self.db_manager.log_analytics(self.user_id, "goal_execution", goal[:100])
            
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": goal,
                "type": "goal",
                "session_id": self.session_id
            })
            
            goal_analysis = self._analyze_goal(goal)
            
            response_parts = []
            metadata = {"session_id": self.session_id, "goal_type": goal_analysis["type"]}
            
            # Research phase
            if goal_analysis["needs_research"]:
                research_results = self.research_engine.search_multiple_sources(goal, 8)
                metadata["research_sources"] = len([r for r in research_results.values() if r])
                
                if research_results and any(research_results.values()):
                    response_parts.append("## 🔍 Research Results\n")
                    
                    for source, results in research_results.items():
                        if results:
                            response_parts.append(f"### {source.title()} ({len(results)} results)")
                            for i, result in enumerate(results[:3], 1):
                                response_parts.append(f"{i}. **{result.get('title', 'N/A')}**")
                                if 'snippet' in result:
                                    response_parts.append(f"   {result['snippet']}")
                                if 'url' in result and result['url']:
                                    response_parts.append(f"   🔗 [Read more]({result['url']})")
                                response_parts.append("")
            
            # Code generation
            if goal_analysis["needs_code"]:
                code_solution = self._generate_code_solution(goal, goal_analysis)
                if code_solution:
                    response_parts.append("## 💻 Code Solution\n")
                    response_parts.append(f"```python\n{code_solution}\n```\n")
                    
                    execution_result = self.security.safe_execute(code_solution, self.user_id)
                    response_parts.append("## 📊 Execution Result\n")
                    response_parts.append(f"```\n{execution_result}\n```\n")
            
            # Educational content
            if goal_analysis["is_educational"]:
                educational_content = self._generate_educational_content(goal)
                response_parts.extend(educational_content)
            
            # Problem solving
            if goal_analysis["is_problem_solving"]:
                problem_solution = self._generate_problem_solution(goal)
                response_parts.extend(problem_solution)
            
            # Suggestions
            suggestions = self._generate_suggestions(goal, goal_analysis)
            if suggestions:
                response_parts.append("## 💡 Next Steps\n")
                for i, suggestion in enumerate(suggestions, 1):
                    response_parts.append(f"{i}. {suggestion}")
                response_parts.append("")
            
            if not response_parts:
                response_parts = [self._generate_fallback_response(goal)]
            
            final_response = "\n".join(response_parts)
            
            self.conversation_history[-1]["system_response"] = final_response
            self.conversation_history[-1]["metadata"] = metadata
            
            self._update_context_memory(goal, final_response, goal_analysis)
            
            metadata.update({
                "response_length": len(final_response),
                "suggestions_count": len(suggestions),
                "conversation_turn": len(self.conversation_history),
                "processing_time": time.time()
            })
            
            return final_response, metadata
            
        except Exception as e:
            error_msg = f"⚠️ System error: {str(e)}"
            logger.error(f"Goal execution error: {e}")
            return error_msg, {"error": str(e), "session_id": self.session_id}
    
    def _analyze_goal(self, goal: str) -> Dict:
        """Analyze goal type"""
        goal_lower = goal.lower()
        
        analysis = {
            "type": "general",
            "needs_research": False,
            "needs_code": False,
            "is_educational": False,
            "is_problem_solving": False,
            "complexity": "medium",
            "keywords": goal_lower.split()
        }
        
        research_keywords = ['research', 'find', 'search', 'what is', 'tell me about', 'information', 'latest']
        if any(keyword in goal_lower for keyword in research_keywords):
            analysis["needs_research"] = True
            analysis["type"] = "research"
        
        code_keywords = ['code', 'program', 'script', 'function', 'algorithm', 'implement', 'develop']
        if any(keyword in goal_lower for keyword in code_keywords):
            analysis["needs_code"] = True
            analysis["type"] = "coding"
        
        edu_keywords = ['learn', 'explain', 'how does', 'tutorial', 'guide', 'teach', 'understand']
        if any(keyword in goal_lower for keyword in edu_keywords):
            analysis["is_educational"] = True
            analysis["type"] = "educational"
        
        problem_keywords = ['solve', 'help', 'fix', 'debug', 'error', 'problem', 'issue']
        if any(keyword in goal_lower for keyword in problem_keywords):
            analysis["is_problem_solving"] = True
            analysis["type"] = "problem_solving"
        
        if len(goal.split()) > 20:
            analysis["complexity"] = "high"
        elif len(goal.split()) < 5:
            analysis["complexity"] = "low"
        
        return analysis
    
    def _generate_code_solution(self, goal: str, analysis: Dict) -> str:
        """Generate code solution"""
        goal_lower = goal.lower()
        
        if any(keyword in goal_lower for keyword in ['data', 'analyze', 'visualize', 'chart']):
            return """import pandas as pd
import numpy as np

# Sample data
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'value': np.random.randn(100).cumsum(),
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

print("Data Shape:", data.shape)
print("\\nFirst 5 rows:")
print(data.head())
print("\\nSummary Statistics:")
print(data.describe())"""
        
        elif any(keyword in goal_lower for keyword in ['calculator', 'math', 'calculate']):
            return """import math

def calculate(expression):
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

# Examples
print(calculate("2 + 2"))
print(calculate("10 * 5"))
print(calculate("math.sqrt(16)"))"""
        
        else:
            return """# General purpose code template
def main():
    print("Hello! This is a code solution.")
    # Add your logic here
    pass

if __name__ == "__main__":
    main()"""
    
    def _generate_educational_content(self, goal: str) -> List[str]:
        """Generate educational content"""
        content = ["## 📚 Educational Content\n"]
        
        content.append("### Overview")
        content.append(f"Let me help you learn about: {goal}\n")
        
        content.append("### Key Concepts")
        content.append("1. **Foundation**: Understanding the basics is crucial")
        content.append("2. **Practice**: Apply what you learn through exercises")
        content.append("3. **Deep Dive**: Explore advanced topics once comfortable\n")
        
        content.append("### Learning Path")
        content.append("- Start with fundamentals")
        content.append("- Build small projects")
        content.append("- Learn from examples")
        content.append("- Practice regularly\n")
        
        return content
    
    def _generate_problem_solution(self, goal: str) -> List[str]:
        """Generate problem solution"""
        solution = ["## 🔧 Problem Solving Approach\n"]
        
        solution.append("### 1. Understand the Problem")
        solution.append("- Define what needs to be solved")
        solution.append("- Identify constraints and requirements\n")
        
        solution.append("### 2. Break It Down")
        solution.append("- Divide into smaller sub-problems")
        solution.append("- Tackle each piece individually\n")
        
        solution.append("### 3. Implement Solution")
        solution.append("- Start with a simple approach")
        solution.append("- Test and iterate")
        solution.append("- Optimize as needed\n")
        
        return solution
    
    def _generate_suggestions(self, goal: str, analysis: Dict) -> List[str]:
        """Generate suggestions"""
        suggestions = []
        
        if analysis["needs_research"]:
            suggestions.append("Explore the research results above for detailed information")
        
        if analysis["needs_code"]:
            suggestions.append("Try modifying the code to fit your specific needs")
            suggestions.append("Test the code with your own data")
        
        if analysis["is_educational"]:
            suggestions.append("Practice with examples to reinforce learning")
            suggestions.append("Explore related topics to deepen understanding")
        
        suggestions.append("Ask follow-up questions if you need clarification")
        
        return suggestions
    
    def _generate_fallback_response(self, goal: str) -> str:
        """Generate fallback response"""
        return f"""## Response to: {goal}

I've analyzed your request. Here's what I can help with:

- **Research**: I can search multiple sources for information
- **Code**: I can generate and execute code solutions
- **Education**: I can explain concepts step-by-step
- **Problem Solving**: I can help break down and solve problems

Please provide more details or ask a specific question, and I'll provide a more targeted response."""
    
    def _update_context_memory(self, goal: str, response: str, analysis: Dict):
        """Update context memory"""
        try:
            self.context_memory[self.session_id] = {
                "last_goal": goal,
                "last_response_length": len(response),
                "goal_type": analysis["type"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Context memory error: {e}") 
