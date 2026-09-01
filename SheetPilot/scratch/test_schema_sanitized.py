import sys
import os
import json
import copy

sys.path.append(os.path.abspath('.'))

from google import genai
from google.genai import types
from src.ai.schemas import AIResponse

def remove_additional_properties(schema):
    """Recursively remove additionalProperties and additional_properties from schema."""
    if not isinstance(schema, dict):
        return schema
    
    # Remove the keys
    schema.pop("additionalProperties", None)
    schema.pop("additional_properties", None)
    
    # Process nested dicts/lists
    for key, value in list(schema.items()):
        if isinstance(value, dict):
            schema[key] = remove_additional_properties(value)
        elif isinstance(value, list):
            schema[key] = [remove_additional_properties(item) if isinstance(item, dict) else item for item in value]
            
    return schema

try:
    client = genai.Client(api_key="TEST")
    
    # 1. Generate Pydantic schema
    raw_schema = AIResponse.model_json_schema()
    
    # 2. Deep copy and sanitize
    sanitized_schema = remove_additional_properties(copy.deepcopy(raw_schema))
    
    # 3. Try to convert using t_schema from the SDK
    import inspect
    from google.genai import _transformers
    
    # Use t_schema directly
    res_schema = _transformers.t_schema(client.models._api_client, sanitized_schema)
    print("Successfully converted sanitized schema using t_schema!")
    print("Result schema type:", type(res_schema))
except Exception as e:
    import traceback
    traceback.print_exc()
