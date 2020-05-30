import os
import subprocess
import tempfile
from typing import Set

from azure.storage.blob import BlobServiceClient

_BLOB_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
_READ_CONTAINER_NAME = "music-links"
_WRITE_CONTAINER_NAME = "music"

CLIENT = BlobServiceClient.from_connection_string(_BLOB_CONN_STR)


def get_links() -> Set[str]:
    links = set()

    container_client = CLIENT.get_container_client(_READ_CONTAINER_NAME)
    blob_list = container_client.list_blobs()

    for blob in blob_list:
        blob_client = CLIENT.get_blob_client(
            container=_READ_CONTAINER_NAME, blob=blob.name
        )

        raw_byte_str = blob_client.download_blob().readall()

        if raw_byte_str:
            lines = "".join(chr(x) for x in raw_byte_str)
            for line in lines.split("\n"):
                links.add(line)

    return links


def upload_file(file_name: str, file_path: str):
    blob_client = CLIENT.get_blob_client(
        container=_WRITE_CONTAINER_NAME, blob=file_name
    )

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


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
            upload_file(mp3, mp3_path)
            print(f"uploaded mp3 {mp3}")


if __name__ == "__main__":
    main()
