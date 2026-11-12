import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-cli",
    version="7.0.0",
    author="Oslo kommune",
    author_email="dataspeilet@oslo.kommune.no",
    description="CLI access to public services for Oslo kommune",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/okdata-cli",
    license_expression="MIT",
    packages=setuptools.find_namespace_packages(include=["okdata.*"]),
    package_data={"okdata.cli": ["data/output-format/*"]},
    install_requires=[
        "docopt",
        "okdata-sdk>=5,<6",
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
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
