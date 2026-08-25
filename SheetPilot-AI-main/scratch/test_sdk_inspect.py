import sys
import os
sys.path.append(os.path.abspath('.'))

from google import genai
from google.genai import types

# Inspect attributes/modules of google.genai
import inspect

print("genai package attributes:", dir(genai))
print("types module attributes:", dir(types))

# Let's inspect where types.Schema or similar is defined
print("types.Schema:", hasattr(types, "Schema"))

# Let's try to convert a Pydantic model to Schema or print how the client compiles it
client = genai.Client(api_key="TEST")
# Let's check how the generate_content call maps to api methods
print("models methods:", dir(client.models))

# Let's see if we can find where pydantic is referenced in client.models.generate_content
import inspect
try:
    print(inspect.getsource(client.models.generate_content))
except Exception as e:
    print("Cannot get source of generate_content:", e)
