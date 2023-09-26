"""Functions to run Dewrangle Graphql queries."""
from gql import gql
from datetime import datetime


def check_mutation_result(result):
    """Check the result of a mutation and handle error(s)"""

    for my_key in result:
        my_error = result[my_key]["errors"]
        if my_error is not None:
            raise RuntimeError(
                "The following error occurred when running mutation:\n{}".format(
                    my_error
                )
            )

    return


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

    check_mutation_result(result)

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
        check_mutation_result(result)
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
                job {
                    id
                }
            }
        }
        """
    )

    params = {"id": volume_id}

    # run mutation
    result = client.execute(mutation, variable_values=params)

    check_mutation_result(result)

    job_id = result["volumeList"]["job"]["id"]

    return job_id


def list_and_hash_volume(client, volume_id, billing_id):
    """Run Dewrangle list and hash volume mutation."""

    # prepare mutation
    mutation = gql(
        """
        mutation VolumeListHashMutation($id: ID!, $input: VolumeListAndHashInput!) {
            volumeListAndHash(id: $id, input: $input) {
                errors {
                    ... on MutationError {
                        message
                        field
                    }
                }
                job {
                    id
                }    
            }
        }
        """
    )

    params = {"id": volume_id}
    params["input"] = {"billingGroupId": billing_id}

    # run mutation
    result = client.execute(mutation, variable_values=params)

    check_mutation_result(result)

    job_id = result["volumeListAndHash"]["job"]["id"]

    return job_id


def get_cred_id(client, study_id, cred_name):
    """Get credential id"""

    cred_id = None

    # get all credentials in study
    credentials = get_study_credentials(client, study_id)

    for cred in credentials:
        if cred_name == credentials[cred]["name"]:
            cred_id = cred

    message = ""

    if len(credentials) == 1:
        ((cred_id, info),) = credentials.items()
        print("Only one credential available: {}".format(info["name"]))
        cred_id = list(credentials.keys())[0]
    elif cred_name:
        for cred in credentials:
            if cred_name == credentials[cred]["name"]:
                cred_id = cred
        if cred_id is None:
            message = "{} credential not found in study".format(cred_name)
    elif len(credentials) == 0:
        message = "No credentials in study."
    else:
        message = "Multiple credentials found in study but none provided. Please run again and provide one of the following crdentials ids:{}{}".format(
            "\n", credentials
        )

    if cred_id is None:
        raise ValueError(message)

    return cred_id


def get_study_credentials(client, study_id):
    """Get credential ids from a study."""

    # query all studies and credentials the user has access to.
    # in the future, this should be a simpler query to get study id from study name
    credentials = {}

    # set up query to get all credentials in the study
    query = gql(
        """
        query Study_Query($id: ID!) {
            study: node(id: $id) {
                id
                ... on Study {
                    credentials {
                        edges {
                            node {
                                id
                                name
                                key
                            }
                        }
                    }
                }
            }
        }
        """
    )

    params = {"id": study_id}

    # run query
    result = client.execute(query, variable_values=params)

    # loop through query results, find the study we're looking for and it's volumes
    for study in result:
        for cred_edge in result[study]["credentials"]["edges"]:
            cred = cred_edge["node"]
            cid = cred["id"]
            name = cred["name"]
            key = cred["key"]
            credentials[cid] = {"name": name, "key": key}

    return credentials


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


def get_org_id_from_study(client, study_id):
    """Query study id and get the id of the organization it's in"""

    org_id = ""
    # set up query to get all available studies
    query = gql(
        """
        query Study_Query($id: ID!) {
            study: node(id: $id) {
                ... on Study {
                    organization {
                        id
                    }
                }
            }
        }
        """
    )

    params = {"id": study_id}

    # run query
    result = client.execute(query, params)

    org_id = result["study"]["organization"]["id"]

    return org_id


def get_all_studies(client):
    """Query all available studies, return study ids and names"""

    studies = {}

    # set up query to get all available studies
    query = gql(
        """
        query {
            viewer {
                organizationUsers {
                    edges {
                        node {
                            organization {
                                name
                                id
                                studies {
                                    edges {
                                        node {
                                            name
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

    for org_edge in result["viewer"]["organizationUsers"]["edges"]:
        for study_edge in org_edge["node"]["organization"]["studies"]["edges"]:
            study = study_edge["node"]
            id = study["id"]
            name = study["name"]
            studies[id] = name

    return studies


def get_study_id(client, study_name):
    """Query all available studies, return study id"""

    study_id = ""
    study_ids = []

    # get a dictionary of all study ids and names
    studies = get_all_studies(client)

    # loop through query results, find the study we're looking for and it's volumes
    for study in studies:
        if studies[study] == study_name:
            study_ids.append(study)

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
    """Query study id, and return volumes in that study"""
    study_volumes = {}
    # set up query to get all available studies
    query = gql(
        """
        query Study_Query($id: ID!) {
            study: node(id: $id) {
                ... on Study {
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
        """
    )

    params = {"id": study_id}

    # run query
    result = client.execute(query, params)

    for study in result:
        for volume_edge in result["study"]["volumes"]["edges"]:
            volume = volume_edge["node"]
            vid = volume["id"]
            vname = volume["name"]
            study_volumes[vid] = vname

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
        check_mutation_result(result)
        print("{} successfully deleted".format(vid))
    else:
        print("{} was not deleted. Run option was not provided.".format(vid))

    return


def get_billing_groups(client, org_id):
    """Get available billing groups for an organization."""

    billing_groups = {}

    # query all organizations, studies, and billing groups the user has access to.
    # set up query to get all available studies
    query = gql(
        """
        query Org_Query($id: ID!) {
            organization: node(id: $id) {
                ... on Organization {
                    billingGroups {
                        edges {
                            node {
                                name
                                id
                                default            
                            }
                        }
                    }
                }
            }
        }
        """
    )

    params = {"id": org_id}

    # run query
    result = client.execute(query, params)

    for bg in result["organization"]["billingGroups"]["edges"]:
        name = bg["node"]["name"]
        id = bg["node"]["id"]
        default = bg["node"]["default"]
        billing_groups[id] = {"name": name, "default": default}

    return billing_groups


def get_billing_id(client, org_id, billing):
    "Get billing group id. If a name is provided, check it exists. If not return org default."

    # first get a list of organizations and billing groups
    billing_groups = get_billing_groups(client, org_id)

    billing_id = None

    for bg in billing_groups:
        if billing and billing == billing_groups[bg]["name"]:
            billing_id = bg
        elif billing_groups[bg]["default"]:
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
                    billingGroup {
                        name
                    }
                    cost {
                        cents
                    }
                    parentJob {
                        id
                        operation
                        createdAt
                        completedAt
                        billingGroup {
                            name
                        }
                        cost {
                            cents
                        }
                    }
                    children {
                        id
                        operation
                        createdAt
                        completedAt
                        billingGroup {
                            name
                        }
                        cost {
                            cents
                        }
                    }
                }
            }
        }
        """
    )

    params = {"id": jobid}

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

    params = {"id": vid}

    # run query
    result = client.execute(query, variable_values=params)

    # format result
    for vol in result:
        for job in result[vol]["jobs"]:
            for node in result[vol]["jobs"][job]:
                id = node["node"]["id"]
                # convert createdAt from string to datetime object
                created = datetime.strptime(
                    node["node"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
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
        raise ValueError(
            "no job(s) matching job type: {} found in volume".format(job_type)
        )

    return jid
