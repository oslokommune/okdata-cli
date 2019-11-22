import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# TODO: remove python-keycloak-client, PyJWT & urllib3 - these are really requirements
#   from the SDK moved here temporarily
setuptools.setup(
    name="origo-cli",
    version="0.0.1",
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
        "python-keycloak-client",
        "PyJWT",
        "urllib3",
    ],
)
