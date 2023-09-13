"""Functions to run Dewrangle Graphql queries."""
from gql import gql
from datetime import datetime


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


def create_study(client, study_name, org_id, run):
    """Run Dewrangle create study mutation."""
    
    study_id = None

    # prepare mutation
    mutation = gql(
        """
        mutation StudyCreateMutation($input: StudyCreateInput!) {
            studyCreate(input: $input) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                study {
                    name
                    id
                }    
            }
        }
        """
    )

    params = {
        "input": {
            "name": study_name,
            "organizationId": org_id,
        }
    }

    # check if run is given and run mutation
    if run:
        result = client.execute(mutation, variable_values=params)
        study_id = result["studyCreate"]["study"]["id"]
    else:
        print("{} was not created. Run option was not provided.".format(study_name))

    return study_id


def list_volume(client, volume_id):
    """Run Dewrangle list volume mutation."""

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


def list_and_hash_volume(client, volume_id, billing_id=None):
    """Run Dewrangle list and hash volume mutation."""

    # prepare mutation
    mutation = gql(
        """
        mutation VolumeListHashMutation($id: ID!, $input: VolumeListAndHashInput) {
            volumeListAndHash(id: $id, input: $input) {
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

    if billing_id is not None:
        params["input"] = {"billingGroupId": billing_id}

    # run mutation
    result = client.execute(mutation, variable_values=params)

    # check result
    workflow_id = result["volumeListAndHash"]["temporalWorkflow"]["workflowId"]

    return workflow_id


def get_cred_id(client, study_id, cred_name):
    """Get credential ids from a study."""

    # query all studies and credentials the user has access to.
    # in the future, this should be a simpler query to get study id from study name
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

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result["viewer"]["studyUsers"]["edges"]:
        study = edge["node"]["study"]
        if study["id"] == study_id:
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

    return cred_id


def get_org_id(client, org_name):
    """Query all available organizations, return org id"""

    org_id = ""
    org_ids = []
    # set up query to get all available studies
    query = gql(
        """
        query {
            viewer {
                organizationUsers {
                    edges {
                        node {
                            organization {
                                id
                                name
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

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result["viewer"]["organizationUsers"]["edges"]:
        org = edge["node"]["organization"]
        if org["name"] == org_name:
            org_ids.append(org["id"])

    if len(org_ids) == 1:
        org_id = org_ids[0]
    elif len(org_ids) == 0:
        raise ValueError("Organization {} not found".format(org_name))
    else:
        raise ValueError(
            "Organization {} found multiple times. Please delete or rename studies so there is only one {}".format(
                org_name, org_name
            )
        )

    return org_id


def get_all_studies(client):
    """Query all available studies, return study ids and names"""

    studies = {}

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

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result["viewer"]["studyUsers"]["edges"]:
        study = edge["node"]["study"]
        id = study["id"]
        name = study["name"]
        studies[id] = name

    return studies


def get_study_id(client, study_name):
    """Query all available studies, return study id"""

    # this function could be split into two get_studies and get_study_id and separate the query
    # from checking the study name like how get_study_billing_groups and get_billing_id work

    study_id = ""
    study_ids = []
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

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result["viewer"]["studyUsers"]["edges"]:
        study = edge["node"]["study"]
        if study["name"] == study_name:
            study_ids.append(study["id"])

    if len(study_ids) == 1:
        study_id = study_ids[0]
    elif len(study_ids) == 0:
        raise ValueError("Study {} not found".format(study_name))
    else:
        raise ValueError(
            "Study {} found multiple times. Please delete or rename studies so there is only one {}".format(
                study_name, study_name
            )
        )

    return study_id


def get_study_volumes(client, study_id):
    """Query all available studies, find study id, and return volumes in that study"""
    study_volumes = {}
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

    # loop through query results, find the study we're looking for and it's volumes
    for edge in result["viewer"]["studyUsers"]["edges"]:
        study = edge["node"]["study"]
        if study["id"] == study_id:
            if len(study["volumes"]["edges"]) > 0:
                for volume_edge in study["volumes"]["edges"]:
                    # get volume from study and format as dict
                    vid = volume_edge["node"]["id"]
                    vname = volume_edge["node"]["name"]
                    study_volumes[vid] = vname
            else:
                raise ValueError("No volumes in study.")

    return study_volumes


'''
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
'''


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


def get_study_billing_groups(client, study_id):
    """Get available billing groups for a study."""

    billing_groups = {}

    # query all organizations, studies, and billing groups the user has access to.
    # set up query to get all available studies
    query = gql(
        """
        query {
            viewer {
                organizationUsers {
                    edges {
                        node {
                            organization {
                                id
                                name
                                billingGroups {
                                    edges {
                                        node {
                                            id
                                            name
                                        }
                                    }
                                }
                                studies{
                                    edges {
                                        node {
                                            id
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

    org_count = 0
    # find organization the study is in, find billing groups, and format output
    for org in result["viewer"]["organizationUsers"]["edges"]:
        for study in org["node"]["organization"]["studies"]["edges"]:
            if study_id == study["node"]["id"]:
                org_count += 1
                # get billing group from org and format similarly
                for node in org["node"]["organization"]["billingGroups"]["edges"]:
                    bid = node["node"]["id"]
                    bname = node["node"]["name"]
                    billing_groups[bid] = bname

    if org_count > 1:
        raise ValueError("Study {} found in multiple organizations.".format(study_id))

    return billing_groups


def get_billing_id(client, study_id, billing):
    "Get billing group id from billing group name."

    # first get a list of organizations and billing groups
    billing_group_list = get_study_billing_groups(client, study_id)

    billing_id = None

    for bg in billing_group_list:
        if billing == bg:
            billing_id = bg

    if billing_id is None:
        raise ValueError("Billing group not found.")

    return billing_id


def process_volumes(study, volumes, **kwargs):
    """Process a dict of volume names and ids, if there's only 1, check it's in the study,
    and returns volume_id."""
    volume_id = kwargs.get("vid", None)
    vname = kwargs.get("vname", None)

    if volume_id:
        if volume_id not in volumes.keys():
            raise ValueError(
                "Volume id not present in study. Ensure you are providing the whole volume id."
            )
    else:
        # see how many times the volume was added to the study
        matching_volumes = []
        for vol in volumes:
            if volumes[vol] == vname:
                matching_volumes.append(vol)
        count = len(matching_volumes)

        if count == 0:
            print("{} volume not found in {}".format(vname, study))
        elif count == 1:
            volume_id = matching_volumes[0]
        else:
            print(
                "=============================================================================================="
            )
            print("Multiple volumes named {} found in {}".format(vname, study))
            print(
                "Rerun this script using the '--vid' option with the volume id of the volume you want to delete"
            )
            print("Matching volumes and ids are:")
            for mvol in matching_volumes:
                print("{}: {}".format(vname, mvol))
            print(
                "=============================================================================================="
            )

    return volume_id


def get_job_info(client, jobid):
    """Query job info with job id"""

    query = gql(
        """
        query Job_Query($id: ID!) {
            job: node(id: $id) {
                id
                ... on Job {
                    operation
                    createdAt
                    completedAt
                }
            }
        }
        """
    )

    params = {
        "id": jobid
    }

    # run query
    result = client.execute(query, variable_values=params)

    return result


def get_volume_jobs(client, vid):
    """Query volume for a list of jobs"""
    jobs = {}

    query = gql(
        """
        query Volume_Job_Query($id: ID!) {
            volume: node(id: $id) {
                id
                ... on Volume {
                    jobs {
                        edges {
                            node {
                                id
                                operation
                                completedAt
                                createdAt
                            }
                        }
                    }
                }
            }
        }
        """
    )

    params = {
        "id": vid
    }

    # run query
    result = client.execute(query, variable_values=params)

    # format result
    for vol in result:
        for job in result[vol]["jobs"]:
            for node in result[vol]["jobs"][job]:
                id = node["node"]["id"]
                # convert createdAt from string to datetime object
                created = datetime.strptime(node["node"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                op = node["node"]["operation"]
                comp = node["node"]["completedAt"]
                jobs[id] = {"operation": op, "createdAt": created, "completedAt": comp}

    return jobs


def get_most_recent_job(client, vid, job_type):
    """Query volume and get most recent job"""
    jid = None
    recent_date = None

    jobs = get_volume_jobs(client, vid)

    if job_type.upper() in ["HASH", "VOLUME_HASH"]:
        job_type = "VOLUME_HASH"
    elif job_type.upper() in ["LIST", "VOLUME_LIST"]:
        job_type = "VOLUME_LIST"
    else:
        raise ValueError("Unsupported job type: {}".format(job_type))

    for job in jobs:
        if jobs[job]["operation"] == job_type:
            # check if date is most recent
            if recent_date is None or jobs[job]["createdAt"] > recent_date:
                recent_date = jobs[job]["createdAt"]
                jid = job

    if jid is None:
        raise ValueError("no job(s) matching job type: {} found in volume".format(job_type))

    return jid


def get_volumes_admin_info(client):
    """
    Query dewrangle for all volumes and studies
    Get volume name, id, prefix, and credential
    Get study users and roles
    """

    volumes = {}

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
                                            name
                                            pathPrefix
                                            credential {
                                                id
                                                name
                                            }
                                        }
                                    }
                                }
                                studyUsers {
                                    edges {
                                        node {
                                            id
                                            role
                                            user {
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
        }
        """
    )

    # run query
    result = client.execute(query)

    print(result)

    return volumes