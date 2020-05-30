import io
import os
import subprocess
import tempfile
from typing import Set

import boto3

_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
_BUCKET_NAME = os.getenv("BUCKET_NAME")

_s3 = boto3.resource(
    "s3", aws_access_key_id=_ACCESS_KEY, aws_secret_access_key=_SECRET_KEY
)

BUCKET = _s3.Bucket(_BUCKET_NAME)


def get_links() -> Set[str]:
    links = set()

    for item in BUCKET.objects.all():

        if item and item.key.endswith("txt"):

            with io.BytesIO() as out:

                BUCKET.download_fileobj(item.key, out)
                raw_byte_str = out.getvalue()

                if raw_byte_str:
                    lines = "".join(chr(x) for x in raw_byte_str)
                    for line in lines.split("\n"):
                        links.add(line.replace("\r", ""))

    return links


def upload_file(file_name: str, file_path: str):
    with open(file_path, "rb") as data:
        BUCKET.upload_fileobj(data, file_name)


def download_mp3s(links: Set[str], output_dir_path: str):
    cmd = [
        "youtube-dl",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        f"{output_dir_path}/%(title)s.%(ext)s",
        "--prefer-ffmpeg",
        *links,
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)

    try:
        proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()


def main():
    links = get_links()

    with tempfile.TemporaryDirectory() as tmp_dir:
        download_mp3s(links, tmp_dir)

        for mp3 in os.listdir(tmp_dir):
            mp3_path = os.path.join(tmp_dir, mp3)
            upload_file("/".join(["mp3s", mp3]), mp3_path)
            print(f"uploaded mp3 {mp3}")


if __name__ == "__main__":
    main()
