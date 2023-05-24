import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-cli",
    version="2.0.1",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="CLI for services provided by Oslo Origo",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-cli/",
    packages=setuptools.find_namespace_packages(
        include="okdata.cli.*", exclude=["tests*"]
    ),
    namespace_packages=["okdata"],
    package_data={
        "okdata": [
            "cli/data/output-format/*",
        ],
    },
    install_requires=[
        "PrettyTable",
        "docopt",
        "okdata-sdk>=2.3.0,<3.0.0",
        "questionary>=1.10.0,<2.0.0",
        "requests",
    ],
    entry_points={"console_scripts": ["okdata=okdata.cli.__main__:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
