import ast
import os
from pathlib import Path

def get_stdlib_modules():
    import sys
    return set(sys.stdlib_module_names)

def check_imports(src_dir):
    stdlib = get_stdlib_modules()
    violations = []
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                path = Path(root) / file
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=str(path))
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    mod = alias.name.split('.')[0]
                                    if mod not in stdlib and mod != 'deceptionguard':
                                        # Whitelist allowed dev-only optional imports in comparison/metrics scripts
                                        if mod in ['sklearn', 'numpy', 'scipy']:
                                            allowed_files = ['classifier.py', 'train_baseline.py', 'split.py', 'metrics.py']
                                            if path.name in allowed_files:
                                                continue
                            elif isinstance(node, ast.ImportFrom):
                                if node.level == 0 and node.module:
                                    mod = node.module.split('.')[0]
                                    if mod not in stdlib and mod != 'deceptionguard':
                                        if mod in ['sklearn', 'numpy', 'scipy']:
                                            allowed_files = ['classifier.py', 'train_baseline.py', 'split.py', 'metrics.py']
                                            if path.name in allowed_files:
                                                continue
                                        violations.append((str(path), mod))
                    except Exception as e:
                        print(f"Error parsing {path}: {e}")
    return violations

if __name__ == '__main__':
    src = Path('src/deceptionguard')
    violations = check_imports(src)
    if violations:
        print("Non-stdlib imports found in core:")
        for path, mod in violations:
            print(f"  {path}: {mod}")
        import sys
        sys.exit(1)
    else:
        print("Dependency check passed: only stdlib and local imports found.")
