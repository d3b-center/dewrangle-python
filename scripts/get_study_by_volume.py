"""Get a list of study ids from volume names."""
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
    required_args.add_argument(
        "-v", "--volume", help="Comma separated list of volume names", required=True
    )

    # parse and return arguments
    args = parser.parse_args()
    volumes = args.volume

    return volumes


def main(args):
    """Main, take args, run script."""
    volume_names = parse_args(args)

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # setup output categories
    not_founds = []
    multiples = {}
    good_volumes = {}

    # convert from names to ids
    volumes = list(set(volume_names.split(",")))
    for vol in volumes:
        study_ids, message = qf.get_study_from_volume(client, vol)
        if message == "Volume not found":
            not_founds.append(vol)
        elif message is not None and "Volume loaded" in message:
            multiples[vol] = study_ids
        else:
            good_volumes[vol] = study_ids

    # process results
    print(
        "====================================================================================="
    )
    print("Volumes only loaded once:")
    print("Volume: study_id")
    for vol in good_volumes:
        print("{}: {}".format(vol, good_volumes[vol]))
    print(
        "====================================================================================="
    )
    print("Volumes that are not loaded:")
    print(not_founds)
    print(
        "====================================================================================="
    )
    print("Volumes loaded to multiple studies or in multiple times in the same study")
    print("Volume: study_id")
    for vol in multiples:
        print("{}: {}".format(vol, multiples[vol]))
    print(
        "====================================================================================="
    )

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
