import argparse
import os
from utils.hasherCore import hash_file, verify_file_hash, hash_folder, SUPPORTED_ALGOS

parser = argparse.ArgumentParser(description="🔐 Hasher Tool - File/Folder Hash Generator and Verifier")
parser.add_argument("path", help="Path to file or folder")
parser.add_argument("-a", "--algo", default="sha256", help=f"Hash algorithm ({', '.join(SUPPORTED_ALGOS)})")
parser.add_argument("-c", "--compare", help="Hash string to compare against")

args = parser.parse_args()

if not os.path.exists(args.path):
    print("❌ File or folder does not exist.")
    exit()

if os.path.isfile(args.path):
    if args.compare:
        match, actual = verify_file_hash(args.path, args.compare, args.algo)
        print(f"\n🔍 Comparing with: {args.compare}")
        print(f"📄 Actual {args.algo.upper()} hash: {actual}")
        print("✅ Match!" if match else "❌ Mismatch!")
    else:
        print(f"📄 {args.algo.upper()} hash of file '{args.path}':")
        print(hash_file(args.path, args.algo))

elif os.path.isdir(args.path):
    print(f"📁 {args.algo.upper()} hash of folder '{args.path}':")
    print(hash_folder(args.path, args.algo))
