from pathlib import Path

current_dir = Path.cwd()

for item in current_dir.iterdir():
    print(item)