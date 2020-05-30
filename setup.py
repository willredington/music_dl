from setuptools import setup

setup(
    name="music_dl",
    version="0.0.1",
    author="William Redington",
    author_email="wcr5048@gmail.com",
    packages=["music_dl"],
    install_requires=["youtube_dl", "boto3"],
    include_package_data=True,
    zip_safe=False,
)
