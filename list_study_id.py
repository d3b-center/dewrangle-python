"""List ids for a study."""
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
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name", required=True)

    # parse and return arguments
    args = parser.parse_args()
    study = args.study

    return study


def main(args):
    """Main, take args, run script."""
    study_name = parse_args(args)

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # get our study id
    study_id = qf.get_study_id(client, study_name)

    # get the study's org id
    org_id = qf.get_org_id_from_study(client, study_id)

    # get all studies and find ours (a little redundant, but this shouldn't take long)
    all_studies = qf.get_all_studies(client)

    # get the info for our study
    study_info = all_studies[study_id]

    url = "dewrangle.com/" + org_id + "/" + study_id

    print(
        "====================================================================================="
    )
    print("Study id: study name, global_id, url")
    print("{}: {}, {}, {}".format(study_id, study_info["name"], study_info["global_id"], url))
    print(
        "====================================================================================="
    )

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
