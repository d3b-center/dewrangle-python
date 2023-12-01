"""Hash all volumes in a list."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd
import dewrangle as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "-f", "--file", help="File with volumes to be loaded.", required=True
    )

    # parse and return arguments
    args = parser.parse_args()
    file = args.file

    return file


def main(args):
    """Main, take args, run script."""
    file = parse_args(args)

    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # read file to df
    df = pd.read_csv(file)
    df = df.replace({float("nan"): None})

    print(df)

    # call wrapper function
    df["job_id"] = df.apply(
        lambda row: qf.load_and_hash_volume(
            client, row["bucket"], row["account"], row["region"], row["prefix"]
        ),
        axis=1,
    )

    print(df)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
