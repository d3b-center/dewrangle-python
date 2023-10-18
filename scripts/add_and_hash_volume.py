"""Add volume to a Dewrangle study."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import dewrangle as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--prefix",
        help="Optional, Path prefix. Default: None",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-r",
        "--region",
        help="Optional, Bucket AWS region code. Default: us-east-1",
        default="us-east-1",
        required=False,
    )
    parser.add_argument(
        "-g",
        "--billing",
        help="Optional, billing group name. When not provided, use default billing group for organization",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--skip",
        help="Flag to skip checking if volume is already loaded to study",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--credential",
        help="Dewrangle AWS credential name. Default, try to find available credential.",
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name, global id, or study id", required=True)
    required_args.add_argument("-b", "--bucket", help="Bucket name", required=True)

    # parse and return arguments
    args = parser.parse_args()
    prefix = args.prefix
    region = args.region
    study = args.study
    bucket = args.bucket
    aws_cred = args.credential
    billing = args.billing
    skip = args.skip

    return (prefix, region, study, bucket, aws_cred, billing, skip)


def main(args):
    """Main, take args, run script."""
    prefix, region, study_name, bucket, aws_cred, billing, skip = parse_args(args)

    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # convert from names to ids
    study_id = qf.get_study_id(client, study_name)
    aws_cred_id = qf.get_cred_id(client, study_id, aws_cred)
    org_id = qf.get_org_id_from_study(client, study_id)
    billing_group_id = qf.get_billing_id(client, org_id, billing)

    # check if volume is already added to study
    if not skip:
        volumes = qf.get_study_volumes(client, study_id)
        if bucket in volumes.values():
            raise ValueError(
                "Volume {} already loaded to {}.".format(bucket, study_name)
            )

    # run create volume mutation
    volume_id = qf.add_volume(client, study_id, prefix, region, bucket, aws_cred_id)

    print("Volume id: {}".format(volume_id))

    # run hash mutation
    job_id = qf.list_and_hash_volume(client, volume_id, billing_group_id)

    print("List and Hash job id: {}".format(job_id))

    """
    Removing this for now since the job doesn't get created immediately
    # get job id from volume
    jobid = qf.get_most_recent_job(client, volume_id, "hash")

    print("Hashing job id: {}".format(jobid))
    """

    # clean up and finish
    print("Volume(s) successfully added and is being hashed.")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
