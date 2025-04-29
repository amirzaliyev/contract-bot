from pathlib import Path

base = Path("docs")
file = base / "templates" / "user123" / "file.docx"

print(type(file))