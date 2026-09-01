import sys
import os
import json

sys.path.append(os.path.abspath('.'))

try:
    from google import genai
    from google.genai import types
    from google.genai._common import serialize
    # We can inspect the SDK's internal schema translation if available
    # Let's create a Client and look at how it serializes the config
    client = genai.Client(api_key="TEST_KEY")
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AIResponse
    )
    # Let's see what the config serialization outputs
    serialized_config = client.models._prepare_request(
        model="gemini-2.5-flash",
        contents="test",
        config=config
    )
    print("Serialized request structure successfully built.")
    print("Generation config response schema:")
    # We can inspect the schema inside the serialized config
    # Depending on how the SDK structures it:
    import pickle
    # Let's print the representation of the schema object
    schema_obj = config.response_schema
    print("response_schema type:", type(schema_obj))
except Exception as e:
    import traceback
    traceback.print_exc()
