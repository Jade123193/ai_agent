import os
from dotenv import load_dotenv
import sys

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

if len(sys.argv)< 2:
    print("error message and exit the program with exit code 1.")
    sys.exit(1)
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=sys.argv[1]
)
print(response.text)
print("Prompt tokens:", response.usage_metadata.prompt_token_count)
print("Response tokens:", response.usage_metadata.candidates_token_count)

