"""Functions to run Dewrangle Graphql queries."""
from gql import gql


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
            "credentialId": aws_cred,
        }
    }

    if prefix is not None:
        params["input"]["pathPrefix"] = prefix

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # check result
    volume_id = result["volumeCreate"]["volume"]["id"]

    return volume_id


def list_volume(client, volume_id):
    """Run Dewrangle create volume mutation."""

    # prepare mutation
    mutation = gql(
        """
        mutation VolumeListMutation($id: ID!) {
            volumeList(id: $id) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                temporalWorkflow {
                    workflowId
                }    
            }
        }
        """
    )

    params = {"id": volume_id}

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # check result
    workflow_id = result["volumeList"]["temporalWorkflow"]["workflowId"]

    return workflow_id


def list_and_hash_volume(client, volume_id):
    """Run Dewrangle create volume mutation."""

    # prepare mutation
    mutation = gql(
        """
        mutation VolumeListHashMutation($id: ID!) {
            volumeListAndHash(id: $id) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                temporalWorkflow {
                    workflowId
                }    
            }
        }
        """
    )

    params = {"id": volume_id}

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # check result
    workflow_id = result["volumeListAndHash"]["temporalWorkflow"]["workflowId"]

    return workflow_id


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
    for edge in result["viewer"]["studyUsers"]["edges"]:
        study = edge["node"]["study"]
        if study["name"] == study_name:
            study_id = study["id"]
            if len(study["credentials"]["edges"]) > 0:
                # check credential name
                for cred_edge in study["credentials"]["edges"]:
                    cred = cred_edge["node"]
                    cid = cred["id"]
                    cname = cred["name"]
                    if cname == cred_name:
                        cred_id = cid
            else:
                print("no credentials in study")

    if cred_id is None:
        print("{} credential not found in study".format(cred_name))

    return study_id, cred_id


def get_study_and_volumes(client, study_name):
    """Query all available studies and find study id from name"""
    study_id = ""
    study_volumes = []
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
                                volumes {
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
            if len(study['volumes']['edges']) > 0:
                for volume_edge in study['volumes']['edges']:
                    volume = volume_edge['node']
                    vid = volume['id']
                    vname = volume['name']
                    study_volumes.append(":".join([vname, vid]))
            else:
                print("no volumes in study")
    
    return study_id, study_volumes


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
            "type": "AWS",
        }
    }

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # process ouptut
    cred_id = result["credentialCreate"]["credential"]["id"]
    print(cred_id)
    # return credential id
    return cred_id


def remove_volume_from_study(client, vid, run):
    """Remove a volume from the study using the study and volume ids."""

    # prepare mutation
    mutation = gql(
        """
        mutation VolumeDelete($id: ID!) {
            volumeDelete(id: $id) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
            }
        }
        """
    )

    params = {"id": vid}

    # check if run is given and run mutation
    if run:
        result = client.execute(mutation, params)
        print("{} successfully deleted".format(vid))
    else:
        print("{} was not deleted. Run option was not provided.".format(vid))

    return