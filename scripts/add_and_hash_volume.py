"""Add volume to a Dewrangle study."""
import sys
import argparse
import dewrangle as qf


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
        help="Optional, Bucket AWS region code. Default: us-east-1",
        default="us-east-1",
        required=False,
    )
    parser.add_argument(
        "-g",
        "--billing",
        help="Optional, billing group name. When not provided, use default billing group for organization",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-c",
        "--credential",
        help="Dewrangle AWS credential name. Default, try to find available credential.",
        required=False,
    )
    # required args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("-s", "--study", help="Study name, global id, or study id", required=True)
    required_args.add_argument("-b", "--bucket", help="Bucket name", required=True)

    # parse and return arguments
    args = parser.parse_args()
    prefix = args.prefix
    region = args.region
    study = args.study
    bucket = args.bucket
    aws_cred = args.credential
    billing = args.billing

    return (prefix, region, study, bucket, aws_cred, billing)


def main(args):
    """Main, take args, run script."""
    prefix, region, study_name, bucket, aws_cred, billing = parse_args(args)

    # call wrapper function
    job_id = qf.load_and_hash_volume(
        bucket, study_name, region, prefix, billing, aws_cred
    )

    print("List and Hash job id: {}".format(job_id))

    # clean up and finish
    print("Volume(s) successfully added and is being hashed.")


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
