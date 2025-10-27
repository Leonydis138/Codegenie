import numpy as np
import pandas as pd
import logging
from typing import Dict, Optional

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

# ===================== ANALYTICS ENGINE =====================
class AdvancedAnalyticsEngine:
    def __init__(self):
        self.datasets = {}
        self.models = {}
        self.visualizations = {}
        
    def create_advanced_visualization(self, data: pd.DataFrame, viz_type: str, 
                                    title: str = "Data Visualization", 
                                    theme: str = "plotly_dark"):
        """Create advanced visualizations"""
        if not PLOTLY_AVAILABLE:
            return None
            
        try:
            fig = None
            colors = px.colors.qualitative.Set3 if PLOTLY_AVAILABLE else None
            
            if viz_type.lower() == "line":
                if len(data.columns) >= 2:
                    fig = px.line(data, x=data.columns[0], y=data.columns[1], 
                                 title=title, template=theme, color_discrete_sequence=colors)
                
            elif viz_type.lower() == "bar":
                if len(data.columns) >= 2:
                    fig = px.bar(data, x=data.columns[0], y=data.columns[1], 
                                title=title, template=theme, color_discrete_sequence=colors)
                
            elif viz_type.lower() == "scatter":
                if len(data.columns) >= 2:
                    fig = px.scatter(data, x=data.columns[0], y=data.columns[1], 
                                   title=title, template=theme, color_discrete_sequence=colors)
                    if len(data.columns) >= 3:
                        fig.update_traces(marker_size=data.iloc[:, 2] * 10)
                
            elif viz_type.lower() == "histogram":
                fig = px.histogram(data, x=data.columns[0], title=title, 
                                 template=theme, color_discrete_sequence=colors)
                
            elif viz_type.lower() == "pie":
                if len(data.columns) >= 2:
                    fig = px.pie(data, names=data.columns[0], values=data.columns[1], 
                               title=title, template=theme, color_discrete_sequence=colors)
                
            elif viz_type.lower() == "heatmap":
                numeric_data = data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    corr_matrix = numeric_data.corr()
                    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                                  title=f"{title} - Correlation Matrix", template=theme)
                
            elif viz_type.lower() == "box":
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    fig = px.box(data, y=numeric_cols[0], title=title, 
                               template=theme, color_discrete_sequence=colors)
                
            elif viz_type.lower() == "3d_scatter":
                if len(data.columns) >= 3:
                    numeric_cols = data.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 3:
                        fig = px.scatter_3d(data, x=numeric_cols[0], y=numeric_cols[1], 
                                          z=numeric_cols[2], title=title, template=theme)
            else:
                if len(data.columns) >= 2:
                    fig = px.line(data, x=data.columns[0], y=data.columns[1], 
                                 title=title, template=theme)
            
            if fig:
                fig.update_layout(
                    font_size=14,
                    title_font_size=18,
                    margin=dict(l=40, r=40, t=60, b=40),
                    hovermode='closest',
                    showlegend=True,
                    autosize=True,
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                fig.update_traces(
                    hovertemplate='<b>%{fullData.name}</b><br>X: %{x}<br>Y: %{y}<br><extra></extra>'
                )
                
            return fig
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            if PLOTLY_AVAILABLE:
                fig = go.Figure()
                fig.add_annotation(
                    text=f"Visualization Error: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="red")
                )
                fig.update_layout(
                    title="Visualization Error",
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, showticklabels=False)
                )
                return fig
            return None

    def generate_comprehensive_analysis(self, data: pd.DataFrame) -> str:
        """Generate comprehensive data analysis"""
        try:
            analysis = "# 📊 Comprehensive Data Analysis\n\n"
            
            analysis += f"## 📋 Dataset Overview\n"
            analysis += f"- **Shape**: {data.shape[0]:,} rows × {data.shape[1]} columns\n"
            analysis += f"- **Memory**: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n"
            
            analysis += "## 📈 Column Analysis\n"
            for col, dtype in data.dtypes.items():
                null_count = data[col].isnull().sum()
                null_pct = (null_count / len(data)) * 100
                analysis += f"- **{col}**: {dtype} ({null_count:,} nulls, {null_pct:.1f}%)\n"
            analysis += "\n"
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis += "## 🔢 Numerical Statistics\n"
                desc = data[numeric_cols].describe()
                
                for col in numeric_cols:
                    analysis += f"### {col}\n"
                    analysis += f"- Mean: {desc.loc['mean', col]:.2f}\n"
                    analysis += f"- Median: {desc.loc['50%', col]:.2f}\n"
                    analysis += f"- Std Dev: {desc.loc['std', col]:.2f}\n"
                    analysis += f"- Range: {desc.loc['min', col]:.2f} to {desc.loc['max', col]:.2f}\n\n"
            
            cat_cols = data.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                analysis += "## 📝 Categorical Analysis\n"
                for col in cat_cols[:5]:
                    unique_count = data[col].nunique()
                    most_common = data[col].value_counts().head(3)
                    analysis += f"### {col}\n"
                    analysis += f"- Unique values: {unique_count:,}\n"
                    analysis += f"- Most common:\n"
                    for val, count in most_common.items():
                        analysis += f"  - {val}: {count:,} ({count/len(data)*100:.1f}%)\n"
                    analysis += "\n"
            
            if len(numeric_cols) > 1:
                corr_matrix = data[numeric_cols].corr()
                analysis += "## 🔗 Correlation Insights\n"
                
                high_corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            high_corr_pairs.append((
                                corr_matrix.columns[i], 
                                corr_matrix.columns[j], 
                                corr_val
                            ))
                
                if high_corr_pairs:
                    analysis += "**Strong correlations found:**\n"
                    for col1, col2, corr_val in high_corr_pairs:
                        analysis += f"- {col1} ↔ {col2}: {corr_val:.3f}\n"
                else:
                    analysis += "No strong correlations (>0.7) detected.\n"
                analysis += "\n"
            
            analysis += "## ✅ Data Quality Assessment\n"
            total_nulls = data.isnull().sum().sum()
            total_cells = len(data) * len(data.columns)
            completeness = ((total_cells - total_nulls) / total_cells) * 100
            
            analysis += f"- **Completeness**: {completeness:.1f}%\n"
            analysis += f"- **Total missing values**: {total_nulls:,}\n"
            
            duplicates = data.duplicated().sum()
            analysis += f"- **Duplicate rows**: {duplicates:,} ({duplicates/len(data)*100:.1f}%)\n"
            
            return analysis
            
        except Exception as e:
            return f"❌ Error generating analysis: {str(e)}"

    def generate_ai_insights(self, data: pd.DataFrame) -> str:
        """Generate AI insights"""
        try:
            insights = []
            
            null_percentage = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
            if null_percentage > 10:
                insights.append(f"⚠️ **Data Quality Alert**: {null_percentage:.1f}% missing values")
            elif null_percentage > 0:
                insights.append(f"✅ **Good Quality**: {null_percentage:.1f}% missing values")
            else:
                insights.append("✅ **Excellent Quality**: No missing values!")
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                correlations = data[numeric_cols].corr()
                high_corr = []
                for i in range(len(correlations.columns)):
                    for j in range(i+1, len(correlations.columns)):
                        corr_val = correlations.iloc[i, j]
                        if abs(corr_val) > 0.8:
                            high_corr.append((correlations.columns[i], correlations.columns[j], corr_val))
                
                if high_corr:
                    insights.append("🔗 **Strong Correlations Detected**:")
                    for col1, col2, corr in high_corr[:3]:
                        direction = "positive" if corr > 0 else "negative"
                        insights.append(f"   - {col1} and {col2}: {direction} ({corr:.3f})")
            
            if len(numeric_cols) > 0:
                outlier_counts = {}
                for col in numeric_cols[:3]:
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = data[(data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))]
                    if len(outliers) > 0:
                        outlier_counts[col] = len(outliers)
                
                if outlier_counts:
                    insights.append("📊 **Outlier Detection**:")
                    for col, count in outlier_counts.items():
                        percentage = (count / len(data)) * 100
                        insights.append(f"   - {col}: {count} outliers ({percentage:.1f}%)")
            
            insights.append("\n### 💡 **Recommendations**:")
            
            if len(data) < 100:
                insights.append("- Consider collecting more data")
            elif len(data) > 10000:
                insights.append("- Large dataset - consider sampling")
            
            if len(numeric_cols) >= 3:
                insights.append("- Try dimensionality reduction (PCA)")
            
            categorical_cols = data.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                insights.append(f"- {len(categorical_cols)} categorical variables - consider encoding")
            
            insights.append("- Use visualization tools to explore patterns")
            insights.append("- Try ML models if you have a target variable")
            
            return "\n".join(insights)
            
        except Exception as e:
            return f"❌ Error generating insights: {str(e)}"

    def create_ml_model(self, data: pd.DataFrame, target_col: str, model_type: str = "regression") -> Dict:
        """Create and train ML models"""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}
            
        try:
            if target_col not in data.columns:
                return {"error": "Target column not found"}
            
            numeric_data = data.select_dtypes(include=[np.number])
            if target_col not in numeric_data.columns:
                return {"error": "Target must be numeric"}
            
            X = numeric_data.drop(columns=[target_col])
            y = numeric_data[target_col]
            
            if X.empty:
                return {"error": "No numeric features available"}
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            if model_type.lower() == "regression":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                y_pred = model.predict(X_test)
                
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                return {
                    "model_type": "Random Forest Regression",
                    "features": list(X.columns),
                    "target": target_col,
                    "metrics": {
                        "mse": mse,
                        "rmse": np.sqrt(mse),
                        "r2_score": r2
                    },
                    "feature_importance": dict(zip(X.columns, model.feature_importances_)),
                    "predictions": y_pred[:10].tolist(),
                    "actual": y_test[:10].tolist()
                }
            
        except Exception as e:
            return {"error": f"Model training error: {str(e)}"}
