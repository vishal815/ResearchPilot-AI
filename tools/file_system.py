"""
ResearchForge v2 — Virtual File System
Agents share data via a dict inside LangGraph state instead of disk files.
"""


def vfs_write(virtual_files: dict, filename: str, content: str) -> dict:
    updated = dict(virtual_files)
    updated[filename] = content
    return updated


def vfs_read(virtual_files: dict, filename: str) -> str:
    return virtual_files.get(filename, f"[File not found: {filename}]")


def vfs_list(virtual_files: dict) -> list:
    return list(virtual_files.keys())


def vfs_read_all(virtual_files: dict) -> str:
    """Concatenate all VFS files for the synthesiser."""
    parts = []
    for fname, content in virtual_files.items():
        parts.append(f"=== {fname} ===\n{content}")
    return "\n\n".join(parts)
