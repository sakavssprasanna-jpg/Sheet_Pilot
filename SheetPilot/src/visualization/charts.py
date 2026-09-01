import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from src.ai.schemas import VisualizationConfig

def render_chart(df: pd.DataFrame, config: VisualizationConfig) -> Optional[go.Figure]:
    """
    Generate an interactive Plotly figure from a DataFrame using a VisualizationConfig.
    
    Args:
        df: The pandas DataFrame.
        config: The VisualizationConfig detailing chart properties.
        
    Returns:
        A Plotly Figure object or None if generation fails.
    """
    if df is None or df.empty or config is None:
        return None
        
    chart_type = config.chart_type.lower()
    x = config.x_axis
    y = config.y_axis
    color = config.color
    title = config.title or f"{chart_type.capitalize()} Chart"
    
    # Verify columns exist in DataFrame
    available_cols = set(df.columns.map(str))
    if x not in available_cols:
        return None
    if y and y not in available_cols:
        y = None
    if color and color not in available_cols:
        color = None
        
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        elif chart_type == "pie":
            # For pie charts, values is y (or count if y is None), names is x
            fig = px.pie(df, names=x, values=y, title=title, template="plotly_dark")
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y, color=color, title=title, template="plotly_dark")
        else:
            return None
            
        # Customize premium dashboard aesthetics
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, system-ui, sans-serif"),
            margin=dict(l=40, r=40, t=50, b=40),
            title=dict(
                font=dict(size=18, color="#FFFFFF", weight="bold"),
                pad=dict(b=10)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#A0AEC0")
            )
        )
        
        # Style x and y axes gridlines for non-pie charts
        if chart_type in ["bar", "line", "scatter", "histogram", "box"]:
            fig.update_xaxes(
                showgrid=True, 
                gridcolor="rgba(255,255,255,0.08)", 
                linecolor="rgba(255,255,255,0.2)",
                tickfont=dict(color="#A0AEC0"),
                title_font=dict(color="#FFFFFF")
            )
            fig.update_yaxes(
                showgrid=True, 
                gridcolor="rgba(255,255,255,0.08)", 
                linecolor="rgba(255,255,255,0.2)",
                tickfont=dict(color="#A0AEC0"),
                title_font=dict(color="#FFFFFF")
            )
            
        return fig
    except Exception:
        return None
