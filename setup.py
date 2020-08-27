import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="origo-cli",
    version="0.2.0",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="CLI for origo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "PrettyTable",
        "docopt",
        "requests",
        "origo-sdk-python>=0.2.2",
        "inquirer",
        "pygments",
    ],
    entry_points={"console_scripts": ["origo=bin.cli:main"]},
)
