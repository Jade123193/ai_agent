from google.genai import types
from google import genai
import os
from dotenv import load_dotenv
import sys
import subprocess

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")


def get_files_info(directory, working_directory):
    abs_working_directory = os.path.abspath(working_directory)
    abs_path_directory = os.path.abspath(directory)
    target_dir = os.path.abspath(os.path.join(working_directory, directory))

    if not target_dir.startswith(abs_working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory.'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory.'

    try:

        item_names = os.listdir(target_dir)

        content_item_info = []

        for item_name in item_names:
            full_item_path = os.path.join(target_dir, item_name)
            is_dir = os.path.isdir(full_item_path)
            file_size = os.path.getsize(full_item_path)

            formatted_item_string = f' - {item_name}: file_size={file_size} bytes, is_dir={is_dir}'
            content_item_info.append(formatted_item_string)
        return '\n'.join(content_item_info)

    except Exception as e:
        return f'Error: {e}'


def get_file_content(file_path, working_directory):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        MAX_CHARS = 10000

        with open(abs_file_path, "r") as f:
            content = f.read()
            if len(content) > MAX_CHARS:
                new_content = content[:MAX_CHARS] + \
                    f'\n[...File "{file_path}" truncated at 10000 characters]'
                return new_content
            else:
                return content

    except Exception as e:
        return f"Error: {str(e)}"


def run_python_file(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not full_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    try:

        if not os.path.exists(full_path):
            return f'Error: File "{file_path}" not found.'

        if not full_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        result = subprocess.run(["python3", file_path], cwd=working_directory,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        formatted_stdout = f'STDOUT:{result.stdout.decode("utf-8")}'
        formatted_stderr = f'STDERR:{result.stderr.decode("utf-8")}'
        combined_output = '\n'.join([formatted_stdout, formatted_stderr])

        if result.returncode != 0:
            returncode_message = f'Process exited with code {result.returncode}'
            combined_output += '\n' + returncode_message

        if combined_output == "":
            return "No output produced."

        return combined_output

    except Exception as e:
        return f'Error: executing Python file: {e}'


def write_file(file_path, content, working_directory):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(file_path)
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    directory = os.path.dirname(full_path)

    if os.path.commonpath([abs_working_directory, full_path]) != abs_working_directory:
        return f'Error: Cannot write to \"{file_path}\" as it is outside the permitted working directory'
    try:
        if not os.path.exists(full_path):
            os.makedirs(directory, exist_ok=True)

        with open(full_path, "w") as f:
            chars_written = f.write(content)
            return f'Successfully wrote to \"{file_path}\" ({chars_written} characters written)'

    except Exception as e:
        return f'Error: {e}'


functions_dict = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file
}


def call_function(function_call_part, verbose=False):
    functions = functions_dict
    function_name = function_call_part.name
    if function_name not in functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    func_args = dict(function_call_part.args)
    func_args["working_directory"] = "./calculator"

    try:
        function_result = functions[function_name](**func_args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result}
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": str(e)},
                )
            ],
        )


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
You are a helpful AI coding agent with access to file system tools.

When a user asks about code or requests analysis, you should:
1. Start by calling get_files_info to explore the directory structure
2. Use get_file_content to read relevant files
3. Analyze the code and provide detailed explanations

Available tools:
- get_files_info: Lists files and directories (call with no parameters to list current directory)
- get_file_content: Read file contents  
- run_python_file: Execute Python files
- write_file: Write or overwrite files

Always start by exploring the codebase with your tools rather than asking the user for file paths.
"""


def generate_content(messages, client, tools):
    for i in range(20):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=tools, system_instruction=system_prompt)
            )

            for candidate in response.candidates:
                messages.append(candidate.content)

            if response.function_calls:
                for function_call_part in response.function_calls:
                    print(f" - Calling function: {function_call_part.name}")
                    function_call_result = call_function(
                        function_call_part, verbose)
                    actual_result = function_call_result.parts[0].function_response.response

                    tool_message = types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=function_call_part.name,
                                response=actual_result,
                            )
                        ],
                    )
                    messages.append(tool_message)

            elif response.text:
                print("Final response:")
                print(response.text)
                return response.text
            else:
                break

        except Exception as e:
            print(f"Error: {str(e)}")
            break

    print("Agent reached 20 iterations without success.")


if len(sys.argv) < 2:
    print("error message and exit the program with exit code 1.")
    sys.exit(1)


contents = sys.argv[1]


if "--verbose" in sys.argv:
    verbose = True
else:
    verbose = False

if verbose:
    print("User prompt:", contents)


messages = [types.Content(
    role="user", parts=[types.Part.from_text(text=contents)])]

generate_content(messages, client, [available_functions])
