import streamlit as st
import tempfile
import os
from utils.hasherCore import hash_file, verify_file_hash, SUPPORTED_ALGOS

st.set_page_config(page_title="Hasher Tool GUI", layout="centered")
st.title("🔐 Hasher Tool")

algo = st.selectbox("Choose hash algorithm", SUPPORTED_ALGOS, index=2)

uploaded = st.file_uploader(
    "Upload a file (or ZIP of a folder)", 
    type=["*"], 
    help="To hash a folder: zip it first and upload the .zip"
)

expected = st.text_input("Expected hash (optional)")

if uploaded:
    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        path = tmp.name

    digest = hash_file(path, algo)

    st.subheader(f"{algo.upper()} Hash:")
    st.code(digest)

    if expected:
        match, actual = verify_file_hash(path, expected, algo)
        if match:
            st.success("✅ Hash match!")
        else:
            st.error("❌ Hash mismatch!")
