from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class FilterCondition(BaseModel):
    column: str = Field(description="Name of the column to filter on")
    operator: str = Field(description="Comparison operator, e.g. '==', '!=', '>', '<', '>=', '<=', 'contains', 'startswith', 'endswith', 'isnull', 'notnull'")
    value: Any = Field(default=None, description="The value to compare the column against. Null for operators like isnull/notnull")

class SortCondition(BaseModel):
    column: str = Field(description="Name of the column to sort by")
    ascending: bool = Field(default=True, description="True for ascending order, False for descending")

class AggregateOperation(BaseModel):
    column: str = Field(description="Column to aggregate, or '*' for count")
    func: str = Field(description="Aggregation function, e.g., 'sum', 'mean', 'median', 'min', 'max', 'count', 'std'")
    alias: str = Field(description="New column name for the aggregated result")

class ColumnTransformation(BaseModel):
    column: str = Field(description="Target column name")
    new_column: Optional[str] = Field(default=None, description="New column name if renaming/creating. If null, overwrites existing column.")
    operation: str = Field(description="Type of transformation: 'math', 'string_upper', 'string_lower', 'fill_na', 'drop_na'")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the transformation, e.g., math expression or value to fillna")

class VisualizationConfig(BaseModel):
    chart_type: str = Field(description="Type of chart to display: 'bar', 'line', 'scatter', 'pie', 'histogram', 'box'")
    x_axis: str = Field(description="Column name to use for the X axis")
    y_axis: Optional[str] = Field(default=None, description="Column name to use for the Y axis (optional for pie, histogram)")
    color: Optional[str] = Field(default=None, description="Column name for grouping colors (optional)")
    title: Optional[str] = Field(default=None, description="Title of the chart")

class StructuredOperation(BaseModel):
    intent: str = Field(
        description="Main intent of the operation. E.g., 'profile', 'filter_sort', 'aggregate', 'transformation', 'duplicate_check', 'missing_check', 'chart'"
    )
    select_columns: Optional[List[str]] = Field(default=None, description="List of columns to select/keep. If null, keep all.")
    filters: Optional[List[FilterCondition]] = Field(default=None, description="Filter conditions to apply")
    sort: Optional[List[SortCondition]] = Field(default=None, description="Sort conditions to apply")
    limit: Optional[int] = Field(default=None, description="Limit the number of rows returned (used for top/bottom N)")
    group_by: Optional[List[str]] = Field(default=None, description="Column names to group by")
    aggregations: Optional[List[AggregateOperation]] = Field(default=None, description="Aggregation operations to perform (used with or without group_by)")
    transformations: Optional[List[ColumnTransformation]] = Field(default=None, description="Column transformations to perform")
    visualization: Optional[VisualizationConfig] = Field(default=None, description="Visualization configuration to render")
    explanation: str = Field(description="A user-friendly natural language explanation of what this operation will do and why.")

class AIResponse(BaseModel):
    status: str = Field(description="The response status: 'success', 'clarification_required', 'unsupported', 'validation_error', 'ai_error'")
    operation: Optional[StructuredOperation] = Field(default=None, description="The structured operation if status is 'success'.")
    clarification: Optional[str] = Field(default=None, description="The clarification question to ask the user if status is 'clarification_required'.")
    explanation: Optional[str] = Field(default=None, description="A natural language description of what will be performed.")
    language: str = Field(default="English", description="The detected language of the user's input, e.g. English, Telugu, Hindi.")
    error: Optional[str] = Field(default=None, description="Error or unsupported message if status is 'unsupported' or 'validation_error'.")
