from setuptools import setup

setup(
    name="music_dl",
    version="0.0.1",
    author="William Redington",
    author_email="willredington315@gmail.com",
    packages=["music_dl"],
    install_requires=["youtube_dl", "azure-storage-blob"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["music_dl=music_dl.main:main"]},
)
