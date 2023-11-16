# D3b Dewrangle Python API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python API for interacting with [Dewrangle](https://github.com/kids-first/dewrangle).

## Quick Dewrangle API Overview

The Dewrangle API uses [Relay](https://relay.dev/) GraphQL. The Python API uses the [gql](https://github.com/graphql-python/gql) library.

## Getting Started

Before running any of the API scripts, an authentication tocken must be created on Dewrangle and stored in the credential.py file located in the root directory of this repo.

1. Login to [Dewrangle](https://dewrangle.com/)

1. Click on you profile and go to Settings

1. Click Generate new token and copy the token into `~/.dewrangle/credentials`

1. Install the dewrangle-python package

### credentials file

The `~/.dewrangle/credentials` is a basic INI file with one section `[default]`

```
[default]
	api_key = "<<YOUR_KEY>>"
```

## Installing the dewrangle-python package

To install the package, simply run:
```
pip install dewrangle-python
```

## Get the Code

To get the code and run the predeveloped scripts locally, clone this repo and either install the package via `pip` or build it locally.

Clone this repo:
```
git clone https://github.com/d3b-center/dewrangle-python.git
```

Install the package locally:
```
cd dewrangle-python
pip install -e .
```

## Key Functions

The key functions for using Dewrangle are `load_and_hash_volume`, `get_job_info`, and `download_job_result`.

The `load_and_hash_volume` function takes the bucket name, study name, AWS region, prefx, billing group name, and AWS credential name. The function checks if the bucket is already loaded as volume in the provided study and if it is not, loads it to the study. Then, it will hash the volume and return the job id of the job that gets launched.
This can be used later for tracking the job and downloading the results. On Dewrangle, when a volume is hashed, a series of jobs are created. The job id that is returned by the `load_and_hash_volume` function is the parent job id. That job will only be marked as completed when all of the child jobs are succesfully completed.

```
job_id = load_and_hash_volume(bucket_name, study_name, region, prefix)
```

The `get_job_info` function takes a job id and can be used to track job status and provides additional information such as when the job was created, by whom, the cost, etc.

```
job_res = get_job_info(job_id)
```

The `download_job_result` function take a job id, checks if a job is complete, and if so returns the result of the job. If the provided job is a parent job, only the result of the hash job is returned.

```
job_status, job_res = download_job_result(job_id)
```
