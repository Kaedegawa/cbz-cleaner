import os
import re
import shutil
import zipfile
import pikepdf

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def sanitize_text(text: str) -> str:
    if text is None:
        return ""
    return re.sub(r'[<>:"/\\|?*]', '_', text)

def ensure_dirs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_pdf(input_path: str, output_path: str):
    try:
        with pikepdf.open(input_path) as pdf:
            meta = pdf.docinfo
            new_meta = {}
            for key, value in meta.items():
                new_meta[key] = sanitize_text(str(value))
            pdf.docinfo.update(new_meta)
            pdf.save(output_path)
        print(f"[PDF] Cleaned → {output_path}")
    except Exception as e:
        print(f"[PDF] Failed {input_path}: {e}")

def clean_cbz(input_path: str, output_path: str):
    temp_dir = input_path + "_tmp"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(input_path, 'r') as zin:
            for member in zin.namelist():
                safe_name = sanitize_text(os.path.basename(member))
                extracted_path = os.path.join(temp_dir, safe_name)
                with zin.open(member) as source, open(extracted_path, "wb") as target:
                    shutil.copyfileobj(source, target)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for fname in sorted(os.listdir(temp_dir)):
                zout.write(os.path.join(temp_dir, fname), fname)

        print(f"[CBZ] Cleaned → {output_path}")

    except Exception as e:
        print(f"[CBZ] Failed {input_path}: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    ensure_dirs()
    files = os.listdir(INPUT_DIR)
    if not files:
        print("No files found in input/. Place CBZs there.")
        return

    for fname in files:
        in_path = os.path.join(INPUT_DIR, fname)
        if not os.path.isfile(in_path):
            continue

        ext = os.path.splitext(fname)[1].lower()
        out_path = os.path.join(OUTPUT_DIR, fname)

        if ext == ".pdf":
            clean_pdf(in_path, out_path)
        elif ext == ".cbz":
            clean_cbz(in_path, out_path)
        else:
            print(f"Skipped (not cbz): {fname}")

if __name__ == "__main__":
    main()
