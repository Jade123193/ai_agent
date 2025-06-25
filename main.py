import os
from dotenv import load_dotenv
import sys

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file contents.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content is to be read.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute Python files with optional arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content is to execute the script.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to file whose content is to be written or overwritten files.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content of the file that is to be written or overwritten files.",
                ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file
    ]
)


client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpuful AI coding agent.

When a user asks a question or makes a request, make a function call paln. You can perfomr the folliwng operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

if len(sys.argv)< 2:
    print("error message and exit the program with exit code 1.")
    sys.exit(1)

contents = sys.argv[1]

if "--verbose" in sys.argv:
    verbose = True
else:
    verbose = False
if verbose:
    print("User prompt:", contents) 

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=contents,
    config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt),
)

if response.function_calls: 
    for function_call_part in response.function_calls:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
else:
    print(response.text)

if verbose:
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)

