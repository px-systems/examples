import hashlib
import sys


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    paths = sys.argv[1:] or (line.strip() for line in sys.stdin if line.strip())
    status = 0
    for path in paths:
        try:
            print(f"{hash_file(path)}  {path}")
        except OSError as e:
            print(f"sha256: {path}: {e}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
