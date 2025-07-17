import streamlit as st
import tempfile
import os
import shutil
import zipfile
from utils.hasherCore import hash_file, hash_folder, verify_file_hash, SUPPORTED_ALGOS

st.set_page_config(page_title="Hasher Tool GUI", layout="centered")
st.title("🔐 Hasher Tool")

algo = st.selectbox("Choose hash algorithm", SUPPORTED_ALGOS, index=2)
expected = st.text_input("Expected hash (optional)")

def compute_folder_hash_with_progress(path, algorithm):
    files_list = []
    for root, _, files in os.walk(path):
        for name in files:
            files_list.append(os.path.join(root, name))
    total = len(files_list)
    progress = st.progress(0)
    try:
        hash_func = __import__('hashlib').__getattribute__(algorithm)()
    except Exception:
        hash_func = __import__('hashlib').sha256()
    for idx, file_path in enumerate(sorted(files_list)):
        rel_path = os.path.relpath(file_path, path).replace("\\", "/")
        hash_func.update(rel_path.encode('utf-8'))
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        progress.progress((idx + 1) / total)
    return hash_func.hexdigest()

path_input = st.text_input("Or enter local file/folder path:")
if st.button("Hash Path") and path_input:
    if os.path.exists(path_input):
        if os.path.isfile(path_input):
            digest = hash_file(path_input, algo)
            st.subheader(f"{algo.upper()} Hash of file:")
            st.code(digest)
            if expected:
                match, actual = verify_file_hash(path_input, expected, algo)
                st.success("✅ Match!") if match else st.error("❌ Mismatch!")
        elif os.path.isdir(path_input):
            st.info(f"Hashing folder '{path_input}'...")
            digest = compute_folder_hash_with_progress(path_input, algo)
            st.subheader(f"{algo.upper()} Hash of folder:")
            st.code(digest)
            st.subheader("Individual file hashes:")
            file_hashes = []
            for root, _, files in sorted(os.walk(path_input)):
                for name in sorted(files):
                    file_path = os.path.join(root, name)
                    rel = os.path.relpath(file_path, path_input).replace("\\", "/")
                    h = hash_file(file_path, algo)
                    file_hashes.append({"file": rel, "hash": h})
            st.table(file_hashes)
            if expected:
                if digest.lower() == expected.lower():
                    st.success("✅ Match!")
                else:
                    st.error("❌ Mismatch!")
    else:
        st.error("❌ Path does not exist. Please check and try again.")

uploaded = st.file_uploader(
    "Or drag & drop files here. For folder hashing, either upload a .zip or select multiple files.",
    accept_multiple_files=True,
)

if uploaded:
    if len(uploaded) == 1 and uploaded[0].name.lower().endswith(".zip"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(uploaded[0].read())
            zip_path = tmp.name
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        st.info("Unzipping and hashing contents...")
        digest = compute_folder_hash_with_progress(extract_dir, algo)
        st.subheader(f"{algo.upper()} Hash of ZIP folder:")
        st.code(digest)
        st.subheader("Individual file hashes:")
        file_hashes = []
        for root, _, files in sorted(os.walk(extract_dir)):
            for name in sorted(files):
                file_path = os.path.join(root, name)
                rel = os.path.relpath(file_path, extract_dir).replace("\\", "/")
                h = hash_file(file_path, algo)
                file_hashes.append({"file": rel, "hash": h})
        st.table(file_hashes)
        if expected:
            match, actual = verify_file_hash(zip_path, expected, algo)
            st.success("✅ Match!") if match else st.error("❌ Mismatch!")
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
    else:
        folder = tempfile.mkdtemp()
        for file in uploaded:
            dest = os.path.join(folder, file.name)
            with open(dest, "wb") as f:
                f.write(file.read())
        st.info("Hashing uploaded files as folder...")
        digest = compute_folder_hash_with_progress(folder, algo)
        st.subheader(f"{algo.upper()} Hash of uploaded folder:")
        st.code(digest)
        st.subheader("Individual file hashes:")
        file_hashes = []
        for root, _, files in sorted(os.walk(folder)):
            for name in sorted(files):
                file_path = os.path.join(root, name)
                rel = os.path.relpath(file_path, folder).replace("\\", "/")
                h = hash_file(file_path, algo)
                file_hashes.append({"file": rel, "hash": h})
        st.table(file_hashes)
        if expected:
            if digest.lower() == expected.lower():
                st.success("✅ Match!")
            else:
                st.error("❌ Mismatch!")
        shutil.rmtree(folder)

