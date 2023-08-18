"""Script to delete volume from a study."""
import sys
import argparse
import re
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import credential
import query_functions as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vid",
        help="Optional, volume id; required when multiple volumes with the same name are loaded to a directory",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--volume",
        help="Volume name, only optional if the vid option is given",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--run",
        help="Flag to actually run deletion mutations",
        action="store_true",
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name", required=True)

    # parse and return arguments
    args = parser.parse_args()
    study = args.study
    name = args.volume
    vid = args.vid
    run = args.run

    return (study, name, vid, run)


def main(args):
    """Main, take args, run script."""
    study_name, name, vid, run = parse_args(args)

    # check for either vid or name
    if not (name or vid):
        raise ValueError("Either volume name or volume id must provided")

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # convert from names to ids
    volumes = qf.get_study_and_volumes(client, study_name)[1]

    if vid:
        search_vid = re.compile(":" + re.escape(vid) + "$")
        if len(list(filter(search_vid.search, volumes))) == 1:
            # call deletion function
            qf.remove_volume_from_study(client, vid, run)
        else:
            raise ValueError(
                "Something went wrong, volume id either not present in study or appears multiple times. Ensure you are providing the whole volume id."
            )
    else:
        # see how many times the volume was added to the study
        search_name = re.compile(
            "^" + re.escape(name) + ":"
        )  # add : to make sure we get the full volume name
        matching_volumes = list(filter(search_name.search, volumes))
        count = len(matching_volumes)

        if count == 0:
            print("{} volume not found in {}".format(name, study_name))
        elif count == 1:
            # extract volume id from matching_volumes[0]
            volume_id = matching_volumes[0].split(":")[1]
            # call deletion function
            qf.remove_volume_from_study(client, volume_id, run)
        else:
            print(
                "=============================================================================================="
            )
            print("Multiple volumes named {} found in {}".format(name, study_name))
            print(
                "Rerun this script using the '--vid' option with the volume id of the volume you want to delete"
            )
            print("Matching volumes and ids are:")
            print("\n".join(map(str, matching_volumes)))
            print(
                "=============================================================================================="
            )

    # TODO: maybe delete all volume with name if -a option given???

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
