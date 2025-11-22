"""
File handling utilities
"""
import os
import tempfile
import zipfile
from typing import List, Dict


def save_temp_file(content: str, extension: str = ".sol") -> str:
    """
    Save content to a temporary file

    Args:
        content: File content
        extension: File extension

    Returns:
        Path to temporary file
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
        f.write(content)
        return f.name


def extract_zip(zip_path: str, extract_to: str) -> List[str]:
    """
    Extract zip file and return list of extracted files

    Args:
        zip_path: Path to zip file
        extract_to: Extraction directory

    Returns:
        List of extracted file paths
    """
    extracted_files = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        extracted_files = [
            os.path.join(extract_to, name)
            for name in zip_ref.namelist()
            if not name.endswith('/')
        ]

    return extracted_files


def read_contract_files(directory: str, extensions: List[str] = [".sol", ".vy"]) -> Dict[str, str]:
    """
    Read all contract files from a directory

    Args:
        directory: Directory path
        extensions: List of file extensions to read

    Returns:
        Dictionary mapping file names to contents
    """
    files = {}

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    files[filename] = f.read()

    return files


def cleanup_temp_files(*file_paths: str) -> None:
    """
    Delete temporary files

    Args:
        file_paths: Paths to files to delete
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
