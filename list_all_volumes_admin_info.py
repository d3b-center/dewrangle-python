"""Script to list admin info for all volumes a user has access to"""
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
    required_args.add_argument(
        "-b", "--basename", help="Output basename", required=True
    )

    # parse and return arguments
    args = parser.parse_args()
    basename = args.basename

    return basename


def main(args):
    """Main, run script."""

    basename = parse_args(args)

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": credential.api_key}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    print(
        "CAVEAT: Included here are ONLY contains studies and volumes you have access to."
    )

    studies = qf.get_volumes_admin_info(client)

    # Format Output Tables

    # format study, volume, and users
    # study_list = ["study_id\tstudy_name"]
    study_list = []
    volume_list = []
    user_list = []
    study_volume = []
    study_user = []
    user_volume = []

    for study in studies:
        study_info = ",".join([study, studies[study]["name"]])
        study_list.append(study_info)
        volumes = studies[study]["volumes"]
        for vol in volumes:
            vol_info = ",".join(
                [
                    vol,
                    volumes[vol]["volume_name"],
                    str(volumes[vol]["pathPrefix"]),
                    volumes[vol]["credential_name"],
                    volumes[vol]["credential_id"],
                ]
            )
            volume_list.append(vol_info)
            study_volume.append(",".join([study, vol]))
        users = studies[study]["users"]
        for su in users:
            su_info = ",".join(
                [
                    su,
                    users[su]["user_id"],
                    users[su]["user_name"],
                    users[su]["role"],
                ]
            )
            user_list.append(su_info)
            study_user.append(",".join([study, su]))
            for vol in volumes:
                user_volume.append(",".join([su, vol]))
        
    # write output files
    out_files = [
        basename + "_studies.csv",
        basename + "_volumes.csv",
        basename + "_users.csv",
        basename + "_study_volume_connections.csv",
        basename + "_study_user_connections.csv",
        basename + "_user_volume_connections.csv",
    ]

    headers = [
        "study_id,study_name",
        "volume_id,volume_name,pathPrefix,credential_name,credential_id",
        "study_user_id,user_id,user_name,role",
        "study_id,volume_id",
        "study_id,study_user_id",
        "study_user_id,volume_id",
    ]

    data_lists = [study_list, volume_list, user_list, study_volume, study_user, user_volume]

    i = 0
    for data in data_lists:
        data = list(set(data))
        data.insert(0, headers[i])
        with open(out_files[i], 'w') as fp:
            for item in data:
                fp.write("{}\n".format(item))
        i += 1

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
