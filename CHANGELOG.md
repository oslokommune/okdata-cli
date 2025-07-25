## ?.?.? - Unreleased

* Dropped support for Python 3.8 which has reached end of life. Python 3.9+ is
  now required.
* New commands `datasets delete-version`, `datasets delete-edition`, and
  `datasets delete-distribution` for deleting dataset versions, editions, and
  distributions respectively.

## 4.4.0 - 2025-05-14

* Added new scope for Brønnøysundregistrene: `brreg:data:enhetsregisteret:auto:roller`.
* Providers and scopes are now fetched from an API instead of being hard coded
  in the CLI code, so updating the CLI for new providers and scopes won't be
  necessary in the future.
* Providers and scopes are sorted alphabetically in the public registry wizard.

## 4.3.1 - 2025-02-24

* Fix previous release (the new `skatteetaten:testnorge/testdata.read` scope was
  not included).

## 4.3.0 - 2025-02-20

* New command `datasets create-pipeline` for creating pipelines for existing
  datasets.
* The dataset creation wizard can now create event type datasets. The database
  dataset type has been removed.
* More robust dataset/version/edition URI parsing.
* Added new scope for skatteetaten:testnorge/testdata.read.

## 4.2.0 - 2024-06-18

* New commands `okdata -e` and `okdata -v` for printing the current environment
  and the current version of okdata-cli, respectively.
* The default choice for dataset visibility is now non-public (red). Also warn
  when a dataset is about to be registered as public (green).

## 4.1.0 - 2024-04-22

* The minimum required version of `okdata-sdk` is now 3.1.1. This ensures
  compatibility with a much newer version of `python-keycloak`, eliminating
  reliance on certain vulnerable dependencies.
* Added support for creating JSON->Delta dataset pipelines.
* The dataset creation wizard has been simplified (it no longer asks
  about geodata details, standards conformity and contact phone
  number).

## 4.0.0 - 2024-03-11

* The `okdata pubreg` family of commands has been renamed to `okdata pubs` (for
  "public services") to reflect that they now don't only handle Maskinporten
  clients, but also ID-porten clients.
* Added support for creating CSV->Delta dataset pipelines.
* Added a shorthand for granting a user all permissions on a resource by not
  specifying the `scope` parameter to the `permissions add` command, similar to
  the way `permissions rm` works.
* Fixed extraneous newline printing in table output.
* Improved error messages in the `datasets ls` and `datasets cp` commands when a
  given dataset doesn't exist.

## 3.2.0 - 2024-01-15

* The `okdata status` command can now be set to watch the status of a dataset
  upload with the `--watch` option.
* The `datasets ls` command now accepts a single optional URI argument that can
  denote either a dataset, version, or edition:

  - `okdata datasets ls {dataset_id}`
  - `okdata datasets ls {dataset_id}/{version}`
  - `okdata datasets ls {dataset_id}/{version}/{edition}`

* Automatically created editions now get timestamped correctly. Previously it
  was assumed that the user always operated in UTC+2.

## 3.1.0 - 2023-11-17

* Added support for Python 3.12.
* Fix a bug in the version requirement for urllib3 by requiring `okdata-sdk`
  version 3 or higher.

## 3.0.0 - 2023-09-01

* Dropped support for Python 3.7 which has reached end of life. Python 3.8+ is
  now required.
* Improved output on data upload when trace ID is missing.

## 2.0.1 - 2023-05-24

* Improved output from the `datasets cp` command.

## 2.0.0 - 2023-04-24

* All `okdata pipelines` commands have been removed. Pipelines can still be
  configured for datasets when using the the dataset creation wizard (`okdata
  datasets create`).
* Improved error message handling in the `pubreg` and `teams` families of
  commands.
* The correct maintainer team is named in error messages.

## 1.6.0 - 2023-03-21

* The `pubreg list-keys` command now supports listing all client keys
  simultaneously across different clients.
* Updated the action URL for the `pubreg delete-client` command. Updating to
  this version is required for the command to continue working in the future.
* Dataset title errors are caught earlier in the registration form.
* Exiting a prompt by typing `Ctrl+D` no longer results in a stack trace.
* Pygments is no longer a dependency.
* The `datasets boilerplate` command has been removed as it has been largely
  subsumed by the `datasets create` wizard.

## 1.5.2 - 2023-02-27

* Attempting to upload a non-existent file to a dataset no longer produces a
  stack trace, but rather displays a nicer error message instead.
* Datasets without a `latest` version is handled better.

## 1.5.1 - 2023-02-17

* The dataset creation wizard no longer crashes when canceled.

## 1.5.0 - 2023-02-13

* Added support for Python 3.11.

## 1.4.0 - 2022-09-08

* New commands `teams add-member` and `teams remove-member` added, allowing for
  management of team members.

## 1.3.0 - 2022-08-26

* A new command `pubreg audit-log` for viewing audit logs of Maskinporten
  clients has been added.
* Automatic client key rotation is now offered when creating a new client key.
* A new family of `team` commands and been added for viewing and editing teams.

## 1.2.0 - 2022-07-04

* The `pubreg delete-client` command now offers to delete the SSM key parameters
  belonging to a client when it's deleted.

## 1.1.0 - 2022-06-22

* Numerous UI improvements in the `pubreg` sub-commands.
* Better keyboard interrupt handling.
* Dropped dependency on Sphinx for documentation generation.

## 1.0.0 - 2022-05-23

* The previously internal `pubreg` command is now made public and documented.
* Support for managing event streams has been removed (i.e. all `okdata events`
  commands).
* Support for managing webhooks has been removed (i.e. all `okdata webhooks`
  commands).
* Added support for Python 3.10.
* Dropped support for Python 3.6 which reached end-of-life in December 2021.
* The current version of `okdata-cli` is now displayed in the help text.

## 0.13.0 - 2021-07-06

* Added support for showing collected error messages in status trace output.

## 0.12.1 - 2021-06-10

* Updated dependencies to fix security vulnerability in urllib3.

## 0.12.0 - 2021-05-26

* The new permission API based `WebhookClient` from the SDK is now used instead
  of the deprecated `SimpleDatasetAuthorizerClient`.

* [Webhook tokens](doc/webhooks.md) are now tied to an operation on a dataset
  (read, write), instead of a specific service.

## 0.11.0 - 2021-05-19

* [Permissions](doc/permissions.md) can now be administered from the CLI.

## 0.10.6 - 2021-04-29

* Enabled retries for file uploads.

* The minimum required version of `okdata-sdk` is now 0.6.3.

## 0.10.5 - 2021-03-30

* Fixed `okdata pipelines instances wizard`, where an outdated version of
  `PipelineInstance` was assumed.

## 0.10.4 - 2021-03-04

* Dataset license is now chosen from a preset list instead of free text.

## 0.10.3 - 2021-02-22

* Fixed a bug where event stream creation would result in a "Forbidden" error.

## 0.10.2 - 2021-02-15

* The dataset source type is now selected in the dataset creation wizard.

## 0.10.1 - 2021-02-09

* Authentication is no longer necessary for downloading public ("green")
  datasets.

## 0.10.0 - 2021-01-26

* Added additional metadata fields to dataset creation wizard.

* The `confidentiality` metadata field is now fully replaced by `accessRights`.

## 0.9.0 - 2020-12-22

* A pipeline for transforming Excel to CSV is now offered in the dataset
  creation wizard.

## 0.8.0 - 2020-12-16

* The `okdata` namespace package now uses the old-style `pkg_resources`
  declaration instead of being an implicit namespace package.

* The dataset creation wizard can now be used to create datasets without a
  pipeline.

## 0.7.0 - 2020-11-13

### Breaking

* Name change
  - Command changed to `okdata` from `origo`
  - PyPI package name `okdata-cli`
  - Repository `okdata-cli`
  - Python modules moved to `okdata.cli.*` with `okdata` as an implicit namespace

### Other

* `origo datasets download` is no longer presented in the `origo datasets` help
  text, since the command is gone. Use `origo datasets cp` instead.

## 0.6.0 - 2020-11-03

* `origo datasets create` now runs a dataset creation wizard for setting up a
  new dataset complete with a processing pipeline, ready to receive files. The
  `--file` parameter can still be used when you want to create a dataset from a
  configuration file.

* The boilerplate command no longer prompts for an AWS account ID, dataset
  edition start time, or dataset edition end time.

* The questions on dataset access rights and confidentiality have been unified
  in the boilerplate questionnaire.

* The boilerplate script now uses the new `datasets cp` syntax for file
  uploading.

* The status (`status`) and upload (`datasets cp`) commands now support the new
  status-api format.

## 0.5.1 - 2020-10-15

* A bug that made the `origo events put` command unusable has been fixed.

* All datafiles required by the boilerplate command are now included in the
  package distribution.

* The `write_to_latest` flag in the boilerplate templates are now set in the
  correct pipeline step.

* The boilerplate script no longer creates a dataset version explicitly, as new
  datasets now include a version "1" by default.

## 0.5.0 - 2020-10-07

* Support new event stream API (including updated SDK). Existing sub-commands from `events` and `event_streams` are now combined into `events`, and new commands for managing event stream sinks and subscriptions are added.

  **Note:** These commands now use dataset URIs instead of separate positional arguments for dataset ID and version.

* Add `--data` option for `events put` (alterantive to stdin/`--file`).
* `~` is now expanded to the home directory in arguments to the `--file` option,
  such as in `origo datasets create --file=~/Documents/my-dataset.json`.

## 0.4.0 - 2020-10-06

* New syntax for the `origo datasets cp` command. Four different URI formats are
  now supported when specifying the dataset to upload to or download from:

  - `ds:{dataset_id}`
  - `ds:{dataset_id}/{version}`
  - `ds:{dataset_id}/{version}/latest`
  - `ds:{dataset_id}/{version}/{edition}`

  The two first forms will automatically create new editions on upload.

  Note that support for the `ds://` prefix and support for providing positional
  versions and editions has been removed.

* Add command `origo webhooks list-tokens` for listing webhook tokens for a dataset.

## 0.3.2 - 2020-09-04

* Use Sphinx for documentation generation.

## 0.3.1 - 2020-08-31

* Include package data in distribution.

## 0.3.0 - 2020-08-28

* Remove `wheel` install from Makefile `init` rule.
* Add prompt for boilerplate to make it easier to create a dataset and pipeline.
* Remove `fuzzywuzzy` and `python-levenshtein` dependencies.
* Add `csv_validator` step in boilerplate setup for `csv-to-parquet`.
* Add a new generic data pipeline `data-copy` for copying data to the platform
  without touching the data.
* Add bidirectional copy command.
* Add download command.
* Add support for Python 3.6.
* Tweak message from boilerplate run script.
* Consistent parameter handling in documentation.
* Split documentation into separate parts.
* Ensure that table rows are aligned.
* Set account ID as a configurable parameter that needs to be set by the user.
* Ensure Bash when running the boilerplate script.
* Allow reading stdin from a tty.
* Remove processing stage from example dataset JSON.

## 0.2.0 - 2020-04-27

* Add dataset authorizer.
* Describe dataset access and webhook tokens in README.
* Use common base options for docopt.
* Update to common output format.
* Update to latest Origo SDK release.

## 0.1.0 - 2020-04-22

* Ensure `jq` is installed.
* Add boilerplate for creating a dataset, pipeline, and input for pipeline.
* Correct printing of dictionaries to ensure output data can be passed to `jq`.
* Create output format for copy file to dataset.
* Correct JSON format for dataset list.
* Remove duplicate output text.
* Add support for status in CLI.
* Type check for dict before applying dict methods on response payload.
* Print JSON, not Python dictionary with `--format=json`.
* Add field for indicating error in output JSON.
* Add standard method for printing error feedback.
* Update dependencies.
* Add documentation for installing Python 3.7.
* Split development documentation from user documentation.
* Move `esq eventstat <datasetid>` command to `events stat <datasetid>`.
* Only print raw JSON when `--format=json` flag is set.
* Add Elasticsearch query command.
* Add support for event streams.
* Exclude virtual environments, `.serverless`, etc. from black check.
* Add environment setup to README.
* Fix `origo help` command.
* Add commands to get, list, and create schemas.
* Add wizard.
* Add support for pipelines.
* Add possibility to create distribution via CLI.
* Stop pushing empty dates to metadata API.
* Correct handling of date format when creating an edition.
* Update documentation and add filter for listing all datasets.
* Create edition when no edition is specified when uploading a file.
* Fix dependencies in tox.
* Test with GitHub actions.
* Use Origo SDK from PyPI.

## 0.0.1 - 2019-11-22

* Initial release.
