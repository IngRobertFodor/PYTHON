import os
from pathlib import Path


subdirectories = {
    "_documents_": ['.pdf','.rtf','.txt'],
    "_audios_": ['.m4a','.m4b','.mp3'],
    "_videos_": ['.mov','.avi','.mp4'],
    "_images_": ['.jpg','.jpeg','.png']
}

def pick_directory(value):
    for category, suffixes in subdirectories.items():
        if value in suffixes:
            return category
    return "_misc_"

# Test out the pick_directory() function.
print(pick_directory('.pdf'))
# Output: _documents_

def organize_directory():
    for item in os.scandir():
        if item.is_dir():
            continue
        file_path = Path(item)
        file_type = file_path.suffix.lower()
        my_directory = pick_directory(file_type)
        directory_path = Path(my_directory)
        if directory_path.is_dir() != True:
            directory_path.mkdir()
        file_path.rename(directory_path.joinpath(file_path))

# Test out the organize_directory() function.
organize_directory()
# Output: No output, but the files in the directory are organized.