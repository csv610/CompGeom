import os
import re

def resolve_relative_import(package_parts, relative_import_match):
    indent = relative_import_match.group(1)
    dots = relative_import_match.group(2)
    imported_from = relative_import_match.group(3)
    import_statement = relative_import_match.group(4)
    
    level = len(dots)
    # level 1 (.) -> package_parts
    # level 2 (..) -> package_parts[:-1]
    
    if level == 1:
        target_base_parts = package_parts
    else:
        target_base_parts = package_parts[:-(level-1)]
        
    if not target_base_parts:
        return relative_import_match.group(0)
    
    base_path = ".".join(target_base_parts)
    if imported_from:
        absolute_imported_from = f"{base_path}.{imported_from}"
    else:
        absolute_imported_from = base_path
        
    return f"{indent}from {absolute_imported_from} import {import_statement}"

def process_file(file_path):
    rel_path = os.path.relpath(file_path, "src")
    parts = os.path.splitext(rel_path)[0].split(os.sep)
    # package_parts is the parts of the package containing this module
    package_parts = parts[:-1]
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Regex to match relative imports, including indented ones:
    pattern = re.compile(r"^(\s*)from\s+(\.+)([a-zA-Z0-9_.]*)\s+import\s+(.+)$", re.MULTILINE)
    
    def replacement_func(match):
        return resolve_relative_import(package_parts, match)
    
    new_content = pattern.sub(replacement_func, content)
    
    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        return True
    return False

def main():
    base_dir = "src/compgeom"
    changed_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    changed_files.append(file_path)
    
    print(f"Total files changed: {len(changed_files)}")
    for f in changed_files:
        print(f"Changed: {f}")

if __name__ == "__main__":
    main()
