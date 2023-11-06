"""Download output from Dewrangle job"""
import sys
import argparse
import requests
import credential
import pandas as pd
import query_functions as qf


def parse_args(args):
    """Get arguments."""
    # optional args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        help="Optional, Output basename. Default: 'job_id'_output",
        default=None,
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-j", "--jobid", help="Job ID", required=True)

    # parse and return arguments
    args = parser.parse_args()
    job = args.jobid
    out = args.output

    return job, out


def request_to_df(url, **kwargs):
    """Call api and return response as a pandas dataframe."""
    my_data = []
    with requests.get(url, **kwargs) as response:
        # check if the request was successful
        if response.status_code == 200:
            for line in response.iter_lines():
                my_data.append(line.decode().split(","))
        else:
            print(f"Failed to fetch the CSV. Status code: {response.status_code}")

    my_cols = my_data.pop(0)
    df = pd.DataFrame(my_data, columns=my_cols)
    return df


def main(args):
    """Main, take args, run script."""
    job_id, out_base = parse_args(args)

    endpoint = "https://dewrangle.com/api/rest/jobs/"

    req_header = {"X-Api-Key": credential.api_key}

    if out_base is None:
        out_file = job_id + "_output.csv"
    else:
        out_file = out_base + ".csv"

    url = endpoint + job_id + "/result"

    df = request_to_df(url, headers=req_header, stream=True)

    df.to_csv(out_file, index=False)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
