## 0.5.0

* Support new event stream API (including updated SDK).
* Add new commands for managing event stream sinks and subscriptions.
* Combine existing sub-commands from `events` and `event_streams` into `events`.
* Add `--data` option for `events put` (alterantive to stdin/`--file`).
* Use dataset URIs as arguments (with or without `ds:` prefix).
* `~` is now expanded to the home directory in arguments to the `--file` option,
  such as in `origo datasets create --file=~/Documents/my-dataset.json`.

## 0.4.0

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

## 0.3.2

* Use Sphinx for documentation generation.

## 0.3.1

* Include package data in distribution.

## 0.3.0

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

## 0.2.0

* Add dataset authorizer.
* Describe dataset access and webhook tokens in README.
* Use common base options for docopt.
* Update to common output format.
* Update to latest Origo SDK release.

## 0.1.0

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

## 0.0.1

* Initial release.
