import os

def get_file_content(working_directory:str, file_path:str):
    
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
                new_content = content[:MAX_CHARS] + f'\n[...FIle "{file_path}" truncate at 10000 characters]'
                f.seek(0)
                f.write(new_content)
                f.truncate()
                return new_content
            else: 
                return content

    except Exception as e:
        return f"Error: {str(e)}"
