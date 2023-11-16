"""List job status."""
import sys
import argparse
import dewrangle as qf


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

    # query job
    job_res = qf.get_job_info(job)

    print(job_res)

    if job_res["job"]["completedAt"] != "" and job_res["job"]["completedAt"] is not None:
        print("Job Completed!")

    print("Done!")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
