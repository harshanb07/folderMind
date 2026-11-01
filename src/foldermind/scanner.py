from pathlib import Path

def scan_directory(directory: str) -> list[Path]:
    root = Path(directory) #string into path object

    files = [] #list to hold all the paths we find....

    for path in root.rglob("*.txt"): #searches root directory and all subdirectories for filenames ending in .txt
        files.append(path)

    return files 


if __name__ == "__main__":
    found_files = scan_directory("demo_data")

    for file in found_files:
        print(file)