import hashlib
import os

SUPPORTED_ALGOS = ["md5", "sha1", "sha256", "sha512"]

def get_hash_function(algorithm: str):
    algo = algorithm.lower()
    if algo not in SUPPORTED_ALGOS:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Choose from {SUPPORTED_ALGOS}")
    return getattr(hashlib, algo)()

def hash_file(file_path, algorithm='sha256'):
    hash_func = get_hash_function(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def verify_file_hash(file_path, expected_hash, algorithm='sha256'):
    actual_hash = hash_file(file_path, algorithm)
    return actual_hash.lower() == expected_hash.lower(), actual_hash

def hash_folder(folder_path, algorithm='sha256'):
    hash_func = get_hash_function(algorithm)

    for root, _, files in sorted(os.walk(folder_path)):
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(file_path, folder_path).replace("\\", "/")

            
            hash_func.update(rel_path.encode('utf-8'))

            
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)

    return hash_func.hexdigest()
