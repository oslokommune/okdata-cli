import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okdata-cli",
    version="0.13.0",
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
            "cli/data/boilerplate/bin/*",
            "cli/data/boilerplate/data/*",
            "cli/data/boilerplate/dataset/*",
            "cli/data/boilerplate/pipeline/*",
            "cli/data/boilerplate/pipeline/csv-to-parquet/*",
            "cli/data/boilerplate/pipeline/data-copy/*",
            "cli/data/output-format/*",
        ],
    },
    install_requires=[
        "PrettyTable",
        "Sphinx",
        "docopt",
        "inquirer",
        "okdata-sdk>=0.9.0,<1.0.0",
        "pygments",
        "recommonmark",
        "requests",
        "questionary",
    ],
    entry_points={"console_scripts": ["okdata=okdata.cli.__main__:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
