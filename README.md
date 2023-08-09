# D3b Dewrangle Python API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python API for interacting with [Dewrangle](https://github.com/kids-first/dewrangle).

## Quick Dewrangle API Overview

The Dewrangle API uses [Relay](https://relay.dev/) GraphQL. The Python API uses the [gql](https://github.com/graphql-python/gql) library.

## Getting Started

Before running any of the API scripts, an authentication tocken must be created on Dewrangle and stored in the credential.py file located in the root directory of this repo.

1. Login to [Dewrangle](https://dewrangle.com/)

1. Click on you profile and go to Settings

1. Click Generate new token and copy the token into credential.py

### credential.py file

```
api_key = "<<YOUR_KEY>>"
```

## Add and Hash Volume

Currently, to add a volume to a study and hash the volume, the study, AWS credential, and billing group must all be set up in Dewrangle before running `add_and_hash_volume.py`.

If a volume / bucket has already been loaded to the study the volume will be added to the study again and will be treated as a separate volume.

```
python add_and_hash_volume.py -h
usage: add_and_hash_volume.py [-h] [-p PREFIX] [-r REGION] -s STUDY -b BUCKET -c CREDENTIAL

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        Optional, Path prefix. Default: None
  -r REGION, --region REGION
                        Optional, Bucket AWS region. Default: US East (N. Virginia)

required arguments:
  -s STUDY, --study STUDY
                        Study name
  -b BUCKET, --bucket BUCKET
                        Bucket name
  -c CREDENTIAL, --credential CREDENTIAL
                        Dewrangle AWS credential ID
```

## Remove (Delete) a Volume

Remove a volume from a study using either the volumes name or volume id. The script first checks if the volume is attached to the user provided study. If there are multiple volumes with the same volume name (see Add and Hash Volume above), the script will return all a list of all volumes in the study with the volume name and volume id and will require you to rerun the script and provide the volume id.

```
python delete_volume.py -h
usage: delete_volume.py [-h] [--vid VID] [--volume VOLUME] [--run] -s STUDY

optional arguments:
  -h, --help            show this help message and exit
  --vid VID             Optional, volume id; required when multiple volumes with the same name are loaded to a directory
  --volume VOLUME       Volume name, only optional if the vid option is given
  --run                 Flag to actually run deletion mutations

required arguments:
  -s STUDY, --study STUDY
                        Study name
```