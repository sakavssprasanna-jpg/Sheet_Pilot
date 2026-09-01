import sys
import os
import json

sys.path.append(os.path.abspath('.'))

from google import genai
from google.genai import types
from src.ai.schemas import AIResponse

client = genai.Client(api_key="TEST")

# Import the converter function from the internal module
# We can find it via client.models._generate_content
import inspect
module = inspect.getmodule(client.models._generate_content)
print("Module file:", module.__file__)

# Let's inspect the module functions
# We need to find _GenerateContentParameters_to_mldev
# It's likely imported into the module or exists in some sub-module
# Let's find it in the module attributes
to_mldev = getattr(module, "_GenerateContentParameters_to_mldev", None)
if to_mldev:
    print("Found _GenerateContentParameters_to_mldev")
    parameter_model = types._GenerateContentParameters(
        model="gemini-2.5-flash",
        contents="test",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIResponse
        ),
    )
    res = to_mldev(client.models._api_client, parameter_model, None, parameter_model)
    print("MLDev Request dict:")
    # Pretty print the generationConfig part which contains the schema
    gen_config = res.get("config", {})
    print(json.dumps(gen_config, indent=2))
else:
    print("_GenerateContentParameters_to_mldev NOT found in module")
