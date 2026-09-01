import sys
import os
import inspect

# Import handle_null_fields from google.genai._transformers
from google.genai import _transformers

print("handle_null_fields source:")
try:
    print(inspect.getsource(_transformers.handle_null_fields))
except Exception as e:
    print(e)
