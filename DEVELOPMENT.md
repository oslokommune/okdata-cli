# Developing Okdata CLI

## Setup

Requirement: Python 3.8+

Setup:

```sh
git clone git@github.com:oslokommune/okdata-cli.git
cd okdata-cli
python3 -m venv .venv
source .venv/bin/activate
make init
```

## Environment

Okdata CLI can be run in either `dev` or `prod`.

When determining in which environment to run a command, the application loads
the environment in the following order, and chooses the first it encounters:

1. `--env=prod|dev` option for every command
2. `OKDATA_ENVIRONMENT` from the current environment
3. Default: `prod`

## Tests

Automatic tests are run with the following command:

```sh
make test
```

## Documentation

Documentation is written in Markdown and is located in the `doc` directory.

## Making a new release

Make sure that `CHANGELOG.md` is up to date and committed to `main`, then run:

```sh
make bump-version-{patch,minor,major}
```

Use the `-patch`, `-minor`, or `-major` variant of the command according to
whether the new release is a patch, minor, or major version respectively.

### Uploading to PyPI

Okdata CLI releases are hosted at [PyPI](https://pypi.org/project/okdata-cli/),
making it easy to install using `pip install okdata-cli`.

Run the following command to build the new version:

```sh
make build
```

Then upload it PyPI by running the following command:

```sh
make publish
```

### Making a GitHub release

Making a GitHub release will automatically notify subscribers of the repository
and members of our support channel on Slack about the new release.

The `bump-version` command from before should have created a new Git tag. Push
it to GitHub:

```sh
git push origin tag <version-tag-name>
```

Run `git tag -l` if you're unsure about the tag name.

After pushing the tag, navigate to
`https://github.com/oslokommune/okdata-cli/tags` and find the newly pushed tag
in the top of the list. Select the three dots (…), and then "Create release".

Use the same format for the title and description as previous releases. The
bullet points are copied from the changelog file.
