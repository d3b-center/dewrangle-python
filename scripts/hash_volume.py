"""Hash files in a volume."""
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
        "-g",
        "--billing",
        help="Optional, billing group name. When not provided, use default billing group for organization",
        default=None,
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name, global id, or study id", required=True)

    # parse and return arguments
    args = parser.parse_args()
    study = args.study
    name = args.volume
    vid = args.vid
    billing = args.billing

    return (study, name, vid, billing)


def main(args):
    """Main, take args, run script."""
    study_name, name, vid, billing = parse_args(args)

    # check for either vid or name
    if not (name or vid):
        raise ValueError("Either volume name or volume id must provided")

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # convert from names to ids
    study_id = qf.get_study_id(client, study_name)
    org_id = qf.get_org_id_from_study(client, study_id)
    billing_id = qf.get_billing_id(client, org_id, billing)
    volumes = qf.get_study_volumes(client, study_id)

    if name:
        volume_id = qf.process_volumes(study_name, volumes, vname=name)
    else:
        volume_id = qf.process_volumes(study_name, volumes, vid=vid)

    if volume_id is not None:
        job_id = qf.list_and_hash_volume(client, volume_id, billing_id)
        print("Hash job id: {}".format(job_id))

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
