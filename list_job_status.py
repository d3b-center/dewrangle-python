"""List job status."""
import sys
import argparse
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import query_functions as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-j", "--jobid", help="Job ID", required=True)

    # parse and return arguments
    args = parser.parse_args()
    job = args.jobid

    return job


def main(args):
    """Main, take args, run script."""
    job = parse_args(args)

    # set up api and authentication
    endpoint = "https://dewrangle.com/api/graphql"

    req_header = {"X-Api-Key": qf.get_api_credential()}

    transport = AIOHTTPTransport(
        url=endpoint,
        headers=req_header,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # query job
    job_res = qf.get_job_info(client, job)

    print(job_res)

    if job_res["job"]["completedAt"] != "" and job_res["job"]["completedAt"] is not None:
        print("Job Completed!")

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
