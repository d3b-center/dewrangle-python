"""List available credentials in a study."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import dewrangle as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name, global id, or study id", required=True)

    # parse and return arguments
    args = parser.parse_args()
    study = args.study

    return study


def main(args):
    """Main, take args, run script."""
    study_name = parse_args(args)

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # find all
    study_id = qf.get_study_id(client, study_name)
    credentials = qf.get_study_credentials(client, study_id)

    print(
        "================================================================================================="
    )
    print("Available billing groups:")
    print("Name | Key | ID")

    for cred in credentials:
        print(
            "{} | {} | {}".format(
                credentials[cred]["name"], credentials[cred]["key"], cred
            )
        )

    print(
        "================================================================================================="
    )

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
