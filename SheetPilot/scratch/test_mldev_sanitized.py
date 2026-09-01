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
    
    # 1. Generate and sanitize Pydantic schema
    raw_schema = AIResponse.model_json_schema()
    sanitized_schema = remove_additional_properties(copy.deepcopy(raw_schema))
    
    # 2. Get to_mldev
    import inspect
    module = inspect.getmodule(client.models._generate_content)
    to_mldev = getattr(module, "_GenerateContentParameters_to_mldev")
    
    parameter_model = types._GenerateContentParameters(
        model="gemini-2.5-flash",
        contents="test",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=sanitized_schema
        ),
    )
    
    res = to_mldev(client.models._api_client, parameter_model, None, parameter_model)
    print("Success! Request dictionary created successfully.")
    
    # Print the config section
    print("Generation config response schema:")
    gen_config = res.get("config", {})
    response_schema = gen_config.get("responseSchema", {})
    print(json.dumps(response_schema, indent=2)[:2000]) # first 2000 chars
except Exception as e:
    import traceback
    traceback.print_exc()
