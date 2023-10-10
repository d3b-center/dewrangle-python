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
        "--run",
        help="Flag to actually run create study mutation",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--skip",
        help="Flag to skip checking if study already exists",
        action="store_true",
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name or global id", required=True)
    required_args.add_argument("-o", "--org", help="Organization name", required=True)

    # parse and return arguments
    args = parser.parse_args()
    study = args.study
    org = args.org
    run = args.run
    skip = args.skip

    return (study, org, run, skip)


def main(args):
    """Main, take args, run script."""
    study_name, org_name, run, skip = parse_args(args)

    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # convert from names to ids
    org_id = qf.get_org_id(client, org_name)

    # check if study already exists
    if not skip:
        studies = qf.get_all_studies(client)
        if study_name in studies.values():
            raise ValueError("Study {} already loaded!.".format(study_name))

    # run create volume mutation
    study_id = qf.create_study(client, study_name, org_id, run)

    print("Study id: {}".format(study_id))

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
