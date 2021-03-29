import os
import re
import json
import shutil

from okdata.cli.command import BaseCommand, BASE_COMMAND_OPTIONS
from okdata.cli.date import date_now, DATE_METADATA_EDITION_FORMAT

from .config import available_pipelines, boilerplate_prompt


class DatasetsBoilerplateCommand(BaseCommand):
    __doc__ = f"""
usage:
   okdata datasets boilerplate <name> [--file=<file> --prompt=<prompt> --pipeline=<pipeline> options]

Examples:
  okdata datasets boilerplate oslo-traffic-data
  okdata datasets boilerplate oslo-traffic-data --file=/tmp/initial-file.csv
  okdata datasets boilerplate oslo-traffic-data --pipeline=data-copy --prompt=no
  okdata datasets boilerplate geodata-from-my-iot-devices

Options:{BASE_COMMAND_OPTIONS}
  --file=<file>         # Initial file to upload
  --prompt=<prompt> # Use input prompt to collect data, default "yes"
  --pipeline=<pipeline>  # Required when --prompt=no
    """

    def __init__(self, sdk):
        super().__init__(sdk)
        self.handler = self.default

    def default(self):
        if self.opt("prompt") == "no":
            self.boilerplate_no_prompt()
        else:
            self.boilerplate_with_prompt()

    def get_name(self):
        name = self.arg("name").strip()
        pattern = re.compile("^[a-zA-Z0-9-]+$")
        if pattern.match(name) is None:
            raise Exception(
                f"Error: {name} is not valid, only 'a-z', 'A-Z', '0-9' and '-' are valid characters"
            )
        return name

    def read_config_from_user(self):
        config = boilerplate_prompt(include_extra_metadata=False)
        return config

    def get_out_dir(self, name):
        # For now we only create the folder in current directory, we can later
        # supply support for --dir=<dir> if needed
        basedir = "."
        outdir = f"{basedir}/{name}"
        return outdir

    def copy_files(self, name, pipeline):
        outdir = self.get_out_dir(name)
        self.log.info(f"Creating: {name} boilerplate to {outdir}")
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.mkdir(name)
        currentdir = os.path.dirname(os.path.realpath(__file__))
        boilerplatedir = f"{currentdir}/../../../data/boilerplate"
        inputfiles = [
            "bin/run.sh",
            "dataset/dataset.json",
            "dataset/dataset-version-edition.json",
            f"pipeline/{pipeline}/pipeline.json",
            "pipeline/pipeline-input.json",
            "data/hello_world.csv",
        ]
        for file in inputfiles:
            tmp = file.split("/")
            fromfile = f"{boilerplatedir}/{file}"
            tofile = f"{outdir}/{tmp[-1]}"
            self.log.info(f"Copying from {fromfile} to {tofile}")
            shutil.copyfile(fromfile, tofile)

    def update_files_with_config(self, name, config):
        outdir = self.get_out_dir(name)

        # Look at a smoother way of updating run.sh later,
        # for now we do a replace based on known values
        run_file_path = f"{outdir}/run.sh"
        with open(run_file_path) as run_file:
            data = run_file.read()
            data = data.replace('echo "### Comment', '# echo "### Comment')
            if self.opt("file"):
                data = data.replace("hello_world.csv", self.opt("file"))
        with open(run_file_path, "w") as run_file_write:
            run_file_write.write(data)

        # Update generated dataset.json file with input values
        # supplied by the user in the prompt
        dataset_file = f"{outdir}/dataset.json"
        with open(dataset_file) as json_file:
            data = json.load(json_file)
            title = config.get("title")
            data["title"] = title
            data["description"] = config.get("description") or title
            data["objective"] = config.get("objective") or title
            access_rights = config.get("accessRights")
            data["accessRights"] = access_rights
            data["publisher"] = config.get("publisher")
            data["contactPoint"] = {
                "name": config.get("name"),
                "email": config.get("email"),
                "phone": config.get("phone"),
            }
            data["keywords"] = config["keywords"]
        with open(dataset_file, "w") as outfile:
            json.dump(data, outfile, indent=4)

        edition_file = f"{outdir}/dataset-version-edition.json"
        with open(edition_file) as json_file:
            data = json.load(json_file)
            data["edition"] = date_now().strftime(DATE_METADATA_EDITION_FORMAT)
            data["description"] = config.get("description") or title
        with open(edition_file, "w") as outfile:
            json.dump(data, outfile, indent=4)

    def boilerplate_with_prompt(self):
        try:
            name = self.get_name()
            config = self.read_config_from_user()
            self.copy_files(name, config["pipeline"])
            self.update_files_with_config(name, config)

            outdir = self.get_out_dir(name)
            self.print(f"Boilerplate set up in folder: {outdir}\n")
            self.print(f"\tGo to {outdir} and execute ´bash run.sh´\n")
        except Exception as e:
            self.print(f"Error: could not generate boilerplate: {str(e)}")

    def boilerplate_no_prompt(self):
        self.log.info("Creating boilerplate without prompt")

        pipeline = self.opt("pipeline")
        if pipeline not in available_pipelines:
            self.print(f"Error: pipeline {pipeline} does not exist!")
            self.print(
                f"\tValid pipelines: {', '.join(str(x) for x in available_pipelines)}"
            )
            return

        name = self.get_name()
        self.copy_files(name, pipeline)
        outdir = self.get_out_dir(name)

        if self.opt("file"):
            run_file_path = f"{outdir}/run.sh"
            with open(run_file_path, "rt") as run_file:
                data = run_file.read()
                data.replace("hello_world.csv", self.opt("file"))

        self.log.info("Done creating boilerplate")
        self.print(f"Boilerplate set up in folder: {outdir}\n")
        self.print(
            f"Edit the following files: \n\t{outdir}/run.sh\n\t{outdir}/dataset.json\n\t{outdir}/dataset-version-edition.json"
        )
        self.print(f"\nFollow instructions in {outdir}/run.sh\n")
