"""Add volume to a Dewrangle study."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import credential


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


# def add_volume(client, study_id, aws_cred_id, prefix, region, bucket):
def add_volume(client, study_id, prefix, region, bucket, aws_cred):
    """Run Dewrangle create volume mutation."""

    # prepare mutation

    mutation = gql(
        """
        mutation VolumeCreateMutation($input: VolumeCreateInput!) {
            volumeCreate(input: $input) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                volume {
                    name
                    id
                }    
            }
        }
        """
    )

    params = {
        "input": {
            "name": bucket,
            "region": region,
            "studyId": study_id,
            "credentialId": aws_cred
        }
    }

    if prefix is not None:
        params["input"]["pathPrefix"] = prefix

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # check result
    volume_id = result['volumeCreate']['volume']['id']

    return volume_id
    


def get_study_and_cred_id(client, study_name, cred_name):
    """Get study and credential ids from study name."""

    # query all studies and credentials the user has access to.
    # in the future, this should be a simpler query to get study id from study name
    study_id = None
    cred_id = None
    # set up query to get all available studies
    query = gql(
        """
        query {
            viewer {
                studyUsers {
                    edges {
                        node {
                            study {
                                id
                                name
                                credentials {
                                    edges {
                                        node {
                                            id
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
    )

    # run query
    result = client.execute(query)

    # TODO: add section to handle study not existing (or user not having access)

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result['viewer']['studyUsers']['edges']:
        study = edge['node']['study']
        if study['name'] == study_name:
            study_id = study['id']
            if len(study['credentials']['edges']) > 0:
                # check credential name
                for cred_edge in study['credentials']['edges']:
                    cred = cred_edge['node']
                    cid = cred['id']
                    cname = cred['name']
                    if cname == cred_name:
                        cred_id = cid
            else:
                print("no credentials in study")
    
    if cred_id is None:
        print("{} credential not found in study".format(cred_name))

    return study_id, cred_id


def make_cred(client, cred_name, study_id):
    """Get aws credential id from name.
    Have to use credentialCreate mutation until query is available."""
    cred_id = ""

    # prepare mutation
    mutation = gql(
        """
        mutation CredentialCreate($input: CredentialCreateInput!) {
            credentialCreate(input: $input) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                credential {
                    id
                    name
                }
            }
        }
        """
    )

    params = {
        "input": {
            "studyId": study_id,
            "name": cred_name,
            "key": credential.aws_key,
            "secret": credential.aws_secret,
            "type": "AWS"
        }
    }

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # process ouptut
    cred_id = result['credentialCreate']['credential']['id']
    print(cred_id)
    # return credential id
    return cred_id


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

    study_id, aws_cred_id = get_study_and_cred_id(client, study_name, aws_cred)

    # run create volume mutation
    ## TODO: figure out what the result is and make a better name
    # temp_res = add_volume(client, study_id, aws_cred_id, prefix, region, bucket)
    volume_id = add_volume(client, study_id, prefix, region, bucket, aws_cred_id)

    print(volume_id)

    # TODO: run hash mutation

    # TODO: verify hash jobs launched? (spit out Cavatica api call????)

    # clean up and finish
    print("Volume(s) successfully added.")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
