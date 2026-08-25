import sys
import os
sys.path.append(os.path.abspath('.'))

from google import genai
import inspect

client = genai.Client(api_key="TEST")
print("client.models._generate_content source:")
try:
    print(inspect.getsource(client.models._generate_content))
except Exception as e:
    print(e)
