import shutil
import os


def reset_folder(folder_path: str):
    """
    Reset a folder by removing all files and subdirectories.
    """
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)
