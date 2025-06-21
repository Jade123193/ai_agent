import os

def get_files_info(working_directory, directory=None):
    
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

