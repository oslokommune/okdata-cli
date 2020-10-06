import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="origo-cli",
    version="0.4.0",
    author="Oslo Origo",
    author_email="dataplattform@oslo.kommune.no",
    description="CLI for services provided by Oslo Origo",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/origo-cli/",
    packages=setuptools.find_packages(".", exclude=["tests*"]),
    package_data={
        "origocli": [
            "data/boilerplate/bin/*",
            "data/boilerplate/data/*",
            "data/boilerplate/dataset/*",
            "data/boilerplate/pipeline/*",
            "data/output-format/*",
        ],
    },
    install_requires=[
        "PrettyTable",
        "Sphinx",
        "docopt",
        "inquirer",
        "origo-sdk-python>=0.2.6",
        "pygments",
        "recommonmark",
        "requests",
        "questionary",
    ],
    entry_points={"console_scripts": ["origo=bin.cli:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
