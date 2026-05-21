"""JPEG to JXL conversion utility script.

This script processes JPEG files and converts each to JXL format using the Wand
library, a Python binding for ImageMagick.

The script supports two input methods:

1. Pass filenames as arguments: python jpg.py file1.jpg file2.jpg ...
2. Pipe a list of filenames via stdin: cat file_list.txt | python jpg.py

Each file is processed sequentially within the current process, printing
information about the conversion process to stdout.
"""

import hashlib
import os
import sys
from pathlib import Path

from wand.image import Image


def get_md5(filename: str) -> str:
    """Calculate MD5 hash of file contents.

    Args:
        filename: Path to the file to hash.

    Returns:
        String containing the hexadecimal MD5 hash of the file contents.
    """
    with Path(filename.strip()).open("rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def process_file(jpg: str) -> tuple[bool, str | None]:
    """Process a single JPEG file and convert it to JXL.

    Args:
        jpg: Path to the JPEG file to convert.

    Returns:
        Tuple containing (success status, md5 hash)
    """
    jpg = jpg.strip()  # Remove trailing newlines
    if jpg.lower().endswith(".jpg"):
        jxl: str = jpg[:-4] + ".jxl"  # Replace last 4 characters (.jpg) with .jxl
    else:
        jxl: str = jpg

    try:
        try:
            md5_hash: str = get_md5(jpg)
            # Only attempt conversion if we got a valid MD5 hash
            if md5_hash:
                with Image(filename=jpg) as img:
                    img.compression_quality = 80
                    img.save(filename=jxl)
        except FileNotFoundError:
            md5_hash = "dryrun"
            print(f"File not found: {jpg}", file=sys.stderr, flush=True)
        except Exception as e:
            md5_hash = "error"  # Clear hash if conversion fails
            print(f"Conversion error for {jpg}: {str(e)}", file=sys.stderr, flush=True)
        print(
            f"in={jpg} | out={jxl} | log=converted [{jpg}/{md5_hash}] to [{jxl}]",
            flush=True,
        )
        return True, md5_hash
    except Exception as e:
        print(f"Error processing {jpg}: {str(e)}", file=sys.stderr, flush=True)
        return False, None


# counter of lines processed in this partition
i: int = 0

# print current process ID (PID)
print(f"pid={os.getpid()}:: start <--", flush=True)

# Check if files were provided as command-line arguments or from stdin
if len(sys.argv) > 1:
    for jpg in sys.argv[1:]:
        success, _ = process_file(jpg)
        if success:
            i += 1
else:
    for line in sys.stdin:
        success, _ = process_file(line)
        if success:
            i += 1

# print the final count of lines processed in this partition
print(f"pid={os.getpid()}:: processed {i} lines in partition", flush=True)
# print current process ID (PID) again as last line
print(f"pid={os.getpid()}:: final <--", flush=True)
