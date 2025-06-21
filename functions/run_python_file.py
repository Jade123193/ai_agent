import os
import subprocess

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
    
        result = subprocess.run(["python3", file_path], cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
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
        

