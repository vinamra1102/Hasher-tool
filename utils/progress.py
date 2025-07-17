import os
import hashlib
import streamlit as st

def compute_folder_hash_with_progress(path, algorithm="sha256"):
    files_list = []
    for root, _, files in os.walk(path):
        for name in files:
            files_list.append(os.path.join(root, name))

    total_files = len(files_list)
    total_size = sum(os.path.getsize(f) for f in files_list)
    processed_size = 0

    progress_bar = st.progress(0)
    status_text = st.empty()
    size_text = st.empty()

    # Get hash function
    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        hash_func = hashlib.sha256()

    for idx, file_path in enumerate(sorted(files_list)):
        rel_path = os.path.relpath(file_path, path).replace("\\", "/")
        status_text.text(f"🔄 Hashing {rel_path} ({idx + 1}/{total_files})")

        # Feed filename into hash (so renames affect the folder hash)
        hash_func.update(rel_path.encode("utf-8"))

        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
                processed_size += len(chunk)
                percent_done = processed_size / total_size
                progress_bar.progress(min(percent_done, 1.0))
                size_text.text(f"📊 Processed {processed_size/1_048_576:.2f} MB / {total_size/1_048_576:.2f} MB")

    status_text.text("✅ Completed hashing all files.")
    return hash_func.hexdigest()
