import os
from pathlib import Path

def read_file_content(file_path: Path) -> str:
    """Read and return the content of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def get_all_project_files() -> str:
    """Get contents of all relevant project files"""
    # Define the project root (adjust as needed)
    project_root = Path('.')
    
    # Initialize output
    output = []
    
    # Define folders and files to scan
    folders_to_scan = ['models', 'services', 'utils']
    root_files = ['app.py', 'config.py']
    
    # Process root files
    for file_name in root_files:
        file_path = project_root / file_name
        if file_path.exists():
            output.append(f"\n{'='*80}\n")
            output.append(f"File: {file_name}\n")
            output.append(f"{'='*80}\n")
            output.append(read_file_content(file_path))
    
    # Process folders
    for folder in folders_to_scan:
        folder_path = project_root / folder
        if folder_path.exists():
            for file_path in folder_path.glob('**/*.py'):
                if file_path.name != '__pycache__':
                    output.append(f"\n{'='*80}\n")
                    output.append(f"File: {file_path}\n")
                    output.append(f"{'='*80}\n")
                    output.append(read_file_content(file_path))
    
    return '\n'.join(output)

if __name__ == "__main__":
    content = get_all_project_files()
    
    # Save to file
    with open('project_files.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Files have been extracted and saved to project_files.txt") 