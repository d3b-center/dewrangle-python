"""Download output from Dewrangle job"""
import sys
import argparse
import dewrangle as qf


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

    #client = qf.create_client()

    if out_base is None:
        out_file = job_id + "_output.csv"
    else:
        out_file = out_base + ".csv"

    status, res = qf.download_job_result(job_id)

    print(status)

    if res is not None:
        res.to_csv(out_file, index=False)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
