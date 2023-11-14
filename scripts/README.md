# D3b Dewrangle Python Scripts

This directory contains a group of helpful scripts for using the `dewrangle-python package`.

## Add and Hash Bucket

Add a bucket / volume to a study and hash the files in it. By default, the default billing group of the organization is used.
Before hashing the files in a volume, the files are first listed. Listing and hashing are both run on [Cavatica](cavatica.sbgenomics.com/).


If a volume / bucket has already been loaded to the study, it will not be loaded again, but it will still be hashed.
Additionally, if an error occurs at any step in the process, previous steps will not be rolled back.
For example, if an error occurs launching the hash job, the volume will still be loaded to the study if it was not previously loaded.


Volumes can either be loaded individually or as a group.


### Loading a single bucket
```
python add_and_hash_volume.py -h
usage: add_and_hash_volume.py [-h] [-p PREFIX] [-r REGION] [-g BILLING] [--skip] [-c CREDENTIAL] -s STUDY -b BUCKET

options:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        Optional, Path prefix. Default: None
  -r REGION, --region REGION
                        Optional, Bucket AWS region code. Default: us-east-1
  -g BILLING, --billing BILLING
                        Optional, billing group name. When not provided, use default billing group for organization
  -c CREDENTIAL, --credential CREDENTIAL
                        Dewrangle AWS credential name. Default, try to find available credential.

required arguments:
  -s STUDY, --study STUDY
                        Study name
  -b BUCKET, --bucket BUCKET
                        Bucket name
```


### Loading a group of buckets

Input csv file format:
```
bucket,account,region,prefix
```

```
python scripts/hash_volume_list.py -h
usage: hash_volume_list.py [-h] -f FILE

options:
  -h, --help            show this help message and exit

required arguments:
  -f FILE, --file FILE  File with volumes to be loaded.
```

### AWS Credential

To generate an AWS credential for Dewrangle, go to the Dewrangle page for the study, click settings, in the Credentials section click Add Credential, and fill in the
Credential Name, AWS Key, and AWS Secret Key. Only the name of the credential needs to be noted and provided to the script.


## Hash or List Files in an Existing Volume

The `hash_volume.py` or `list_volume_files.py` allow you to hash or list files in an existing volume. They both take the same options and return the job id of the main job that is launched on Dewrangle.

```
python hash_volume.py -h
usage: hash_volume.py [-h] [--vid VID] [--volume VOLUME] -s STUDY

options:
  -h, --help            show this help message and exit
  --vid VID             Optional, volume id; required when multiple volumes with the same name are loaded to a directory
  --volume VOLUME       Volume name, only optional if the vid option is given

required arguments:
  -s STUDY, --study STUDY
                        Study name
```

## Create Study

Create a study in an organization. The script will first check if a study is loaded to any other organizations.

```
python create_study.py -h
usage: create_study.py [-h] [--run] -s STUDY -o ORG

options:
  -h, --help            show this help message and exit
  --run                 Flag to actually run create study mutation

required arguments:
  -s STUDY, --study STUDY
                        Study name
  -o ORG, --org ORG     Organization name
```


## Download Job Result

After a job is completed, a csv output file is created.

```
python download_job_result.py -h
usage: download_job_result.py [-h] [-o OUTPUT] -j JOBID

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Optional, Output basename. Default: 'job_id'_output

required arguments:
  -j JOBID, --jobid JOBID
                        Job ID
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

## List Scripts

The `list_billing_groups.py`, `list_volumes_in_study.py`, and `list_credentials.py` scripts provided similar functionality. These scripts list the billing groups, volumes,
or credentials currently available in
the provided study. The `list_volume_jobs.py` script lists the jobs that were run on the volume and also lists the job ids of the most recent hash and list jobs.
The `list_job_status.py` script lists the job status from a provided job id.

```
python list_billing_groups.py -h
usage: list_billing_groups.py [-h] -s STUDY

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -s STUDY, --study STUDY
                        Study name
```