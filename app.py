import streamlit as st
import tempfile
import os
import shutil
#import zipfile

from utils.hasherCore import (
    hash_file,
    hash_folder,
    verify_file_hash,
    SUPPORTED_ALGOS,
)

st.set_page_config(page_title="Hasher Tool ", layout="centered")
st.title("🔐 Hasher Tool")


algo = st.selectbox("Choose hash algorithm", SUPPORTED_ALGOS, index=2)

expected = st.text_input("Expected hash (optional)")


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
            digest = hash_folder(path_input, algo)
            st.subheader(f"{algo.upper()} Hash of folder:")
            st.code(digest)
            if expected:
                if digest.lower() == expected.lower():
                    st.success("✅ Match!")
                else:
                    st.error("❌ Mismatch!")
    else:
        st.error("❌ Path does not exist. Please check and try again.")


uploaded = st.file_uploader(
    "Or drag & drop files here. For folder hashing, either upload a .zip or select multiple files.",
    type=None,
    accept_multiple_files=True,
)

if uploaded:
    
    if len(uploaded) == 1 and uploaded[0].name.lower().endswith(".zip"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(uploaded[0].read())
            path = tmp.name

        digest = hash_file(path, algo)
        st.subheader(f"{algo.upper()} Hash of ZIP file:")
        st.code(digest)
        if expected:
            match, actual = verify_file_hash(path, expected, algo)
            st.success("✅ Match!") if match else st.error("❌ Mismatch!")

        os.remove(path)

    else:
        
        folder = tempfile.mkdtemp()
        for file in uploaded:
            dest = os.path.join(folder, file.name)
            with open(dest, "wb") as f:
                f.write(file.read())

        digest = hash_folder(folder, algo)
        st.subheader(f"{algo.upper()} Hash of uploaded folder:")
        st.code(digest)

        if expected:
            if digest.lower() == expected.lower():
                st.success("✅ Match!")
            else:
                st.error("❌ Mismatch!")

        shutil.rmtree(folder)
