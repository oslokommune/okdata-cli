import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-cli",
    version="5.0.1",
    author="Oslo Origo",
    author_email="dataspeilet@oslo.kommune.no",
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
        "docopt",
        "okdata-sdk>=3.4,<4",
        "PrettyTable",
        # TODO: Upgrade to questionary 2.x.
        "questionary>=1.10.0,<2.0.0",
        # Not a direct dependency, but a dependency for questionary. However
        # questionary breaks with prompt-toolkit 3.0.52 (and possibly later
        # versions as well), so let's pin it sub 3.0.52 for now.
        "prompt-toolkit<3.0.52",
        "requests",
    ],
    entry_points={"console_scripts": ["okdata=okdata.cli.__main__:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
