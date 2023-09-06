"""Script to list admin info for all volumes a user has access to"""
import sys
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import credential
import query_functions as qf


def main(args):
    """Main, run script."""

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    volumes = qf.get_volumes_admin_info(client)

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
