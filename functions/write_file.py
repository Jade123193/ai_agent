import os

def write_file(working_directory, file_path, content):
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
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written'

    except Exception as e:
        return f'Error: {e}'


