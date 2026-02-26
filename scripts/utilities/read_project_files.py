import os
import sys
from pathlib import Path
from docx import Document

def read_docx(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def main():
    target_dir = r"d:\桌面\房产项目\建华官园智慧农贸"
    output_file = r"d:\桌面\leo_ai_system\temp_jianhua_data.txt"
    files = [
        "建华观园菜市场说辞.docx",
        "建华观园菜市场答客问.doc",
        "项目微信发送.docx"
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for filename in files:
            file_path = os.path.join(target_dir, filename)
            if os.path.exists(file_path):
                f.write(f"--- START OF {filename} ---\n")
                content = read_docx(file_path)
                f.write(content)
                f.write(f"\n--- END OF {filename} ---\n\n")
            else:
                f.write(f"File not found: {file_path}\n")
    print(f"Project data saved to {output_file}")

if __name__ == "__main__":
    main()
