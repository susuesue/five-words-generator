"""
核心业务逻辑模块
"""

from .generator import generate_three_segments
from .file_handler import extract_text, find_project_files

__all__ = ['generate_three_segments', 'extract_text', 'find_project_files']

