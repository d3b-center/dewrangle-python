"""Add volume to a Dewrangle study."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import credential
import query_functions as qf


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
        help="Optional, Bucket AWS region. Default: US East (N. Virginia)",
        default="us-east-1",
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name", required=True)
    required_args.add_argument("-b", "--bucket", help="Bucket name", required=True)
    required_args.add_argument(
        "-c", "--credential", help="Dewrangle AWS credential ID", required=True
    )

    # parse and return arguments
    args = parser.parse_args()
    prefix = args.prefix
    region = args.region
    study = args.study
    bucket = args.bucket
    aws_cred = args.credential

    return (prefix, region, study, bucket, aws_cred)


def main(args):
    """Main, take args, run script."""
    prefix, region, study_name, bucket, aws_cred = parse_args(args)

    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # convert from names to ids

    study_id, aws_cred_id = qf.get_study_and_cred_id(client, study_name, aws_cred)

    # run create volume mutation
    volume_id = qf.add_volume(client, study_id, prefix, region, bucket, aws_cred_id)

    print("Volume id: {}".format(volume_id))

    # run hash mutation
    workflow_id = qf.list_and_hash_volume(client, volume_id)

    print("Hashing job id: {}".format(workflow_id))

    # TODO: verify hash jobs launched? (spit out Cavatica api call????)

    # clean up and finish
    print("Volume(s) successfully added and is being hashed.")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)