"""Download output from Dewrangle job"""
import sys
import argparse
import requests
import credential
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

    response = requests.get(url, headers=req_header)

    with requests.get(url, headers=req_header, stream=True) as response:
    # check if the request was successful
        if response.status_code == 200:
            with open(out_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):  # 8K chunks
                    f.write(chunk)
            print("CSV file downloaded successfully!")
        else:
            print(f"Failed to fetch the CSV. Status code: {response.status_code}")

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
