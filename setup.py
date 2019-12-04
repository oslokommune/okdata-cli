import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="origo-cli",
    version="0.0.1",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="CLI for origo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["PrettyTable", "origo-sdk-python", "docopt", "requests"],
    entry_points={"console_scripts": ["origo=bin.cli:main"]},
)
