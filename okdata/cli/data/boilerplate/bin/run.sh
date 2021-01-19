#!/bin/bash
# Create dataset and pipeline to process any data pushed to the dataset

# This is the first edition of the script, if it fails: please review the setup and
# re-run the script -->
#   If a dataset_id is created and you have to re-run the script because creating the
#   version fails: set dataset_id to the ID you get from the output of this script, then comment out the
#   "Dataset" block further below
if [ "$BASH_VERSION" = '' ]; then
  echo "This script should only be run with bash, support of other shells will come later"
  exit 1
fi

if ! [ -x "$(command -v jq)" ]; then
  echo 'Error: jq is not installed.' >&2
  exit 1
fi

echo "Update json files in this directory before running"
echo "### Comment out this line to run ###\n" && exit 1

echo "Creating a dataset, edition, pipeline and uploading a file to test"
echo "Please wait....."

######### Input files #########
# These files MUST be updated:
dataset_file="dataset.json"
dataset_version_edition_file="dataset-version-edition.json"
# No need to update the following files:
dataset_upload_file="hello_world.csv"
pipeline_instance_file="pipeline.json"
pipeline_input_file="pipeline-input.json"

######### Basic check to see if user have updated data in files #########
dataset_data=`cat $dataset_file`
if [[ $dataset_data =~ "boilerplate" || $dataset_data =~ "my.address@example.org" || $dataset_data =~ "Publisher Name" ]]
then
   echo "Error: $dataset_file has not been updated correctly - please change the data to represent the dataset you want to create and the organization creating it!"
   echo "Note: Change all occurence of 'boilerplate', contact and publisher must be a real contact point"
   exit
fi


version_data=`cat $dataset_version_edition_file`
if [[ $version_data =~ "Boilerplate" || $version_data =~ "2020-00-00" ]]
then
   echo "Error: $dataset_version_edition_file has not been updated correctly - please change the data to represent the edition you want to create"
   exit
fi

######### Dataset #########
dataset=`okdata datasets create --file=$dataset_file --format=json`
dataset_id=`echo "$dataset" | jq  -r '.Id'`
version_id=1
if [[ $dataset_id == null ]]; then
    echo "Could not create dataset"
    echo $dataset | jq
    exit
fi
echo "Created dataset: $dataset_id"
echo "Created version: $version_id"

######### Dataset Edition #########
# Format for dataset-version-edition.json fields:
#   DATE_SHORT=`date +%Y-%m-%d`
#   DATE_EDITION=`date +%Y-%m-%dT%H:%M:%S+02:00`
edition=`okdata datasets create-edition $dataset_id $version_id --file=$dataset_version_edition_file --format=json`
edition_id=`echo "$edition" | jq  -r '.Id'`
if [[ $edition_id == null ]]; then
    echo "Could not create edition"
    echo $edition | jq
    exit
fi
edition_id=`echo $edition_id | cut -d "/" -f 3`
echo "Created edition: $edition_id"

######### Pipeline instance #########
cat $pipeline_instance_file | sed "s/DATASET_ID/$dataset_id/" | sed "s/DATASET_VERSION/$version_id/" > generated_pipeline.json
pipeline=`okdata pipelines instances create generated_pipeline.json --format=json`
if [[ $pipeline == "" ]]; then
    echo "Could not create pipeline instance"
    exit
fi
error=`echo $pipeline | jq -r '.error'`
if [[ "$error" =~ ^[1]+$ ]]; then
  echo "Could not create instance"
  echo $pipeline | jq
  exit
fi
pipeline_id=`echo $pipeline | jq -r '.id'`
echo "Created pipeline instance $pipeline_id for dataset: $dataset_id "

######### Pipeline input #########
cat $pipeline_input_file | sed "s/DATASET_ID/$dataset_id/" | sed "s/DATASET_VERSION/$version_id/" | sed "s/PIPELINEINSTANCE/$pipeline_id/"  > generated_pipeline_input.json
input=`okdata pipelines inputs create generated_pipeline_input.json --format=json`
error=`echo $input | jq -r '.error'`
if [[ "$error" =~ ^[1]+$ ]]; then
  echo "Could not create inputs"
  echo $input | jq
  exit
fi
echo "Created input for $dataset_id"

######### Copy file to dataset #########
upload=`okdata datasets cp $dataset_upload_file ds:$dataset_id/$version_id/$edition_id --format=json`
error=`echo $upload | jq -r '.error'`
if [[ "$error" =~ ^[1]+$ ]]; then
  echo "Could not upload file"
  echo $upload | jq
  exit
fi
trace_id=`echo "$upload" | jq  -r '.trace_id'`
if [[ $trace_id == false ]]; then
  echo "Error: File uploaded to okdata, but could not get the trace ID of the upload"
  exit
fi
echo "Uploaded test file to dataset $dataset_id, trace id for upload is $trace_id"

######### Check status for the newly uploaded file #########
uploaded=false
echo "Checking status for uploaded file"
while ! $uploaded; do
  echo "\Checking upload status....."
  upload_status=`okdata status $trace_id --format=json`
  uploaded=`echo $upload_status | jq -r '.done'`
done
echo "Uploaded file is processed and ready to be consumed"
