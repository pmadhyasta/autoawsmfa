#!/usr/bin/env python3


import boto3
import getpass
import argparse
import subprocess
import configparser
from boto3 import client
from . import __version__
from .mfa import handle_mfa
from os import getenv, path, name
from datetime import datetime
from .session import handle_session
from sys import exit, stderr, argv
from botocore.exceptions import ClientError
from .util import check_duration, check_custom_token, get_credentials_path


def main() -> int:

    argument_parser = argparse.ArgumentParser(
        prog='AutoAWSMFA',
        description='Auto update your AWS CLI MFA session token'
    )

    argument_parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    argument_parser.add_argument(
        '-p',
        '--profile',
        help='AWS profile to store the session token. Default looks for "AWS_PROFILE"',
        default=getenv('AWS_PROFILE')
    )

    argument_parser.add_argument(
        '--credential-path',
        help='path to the aws credentials file',
        default=get_credentials_path()
    )

    argument_parser.add_argument(
        '--arn',
        help='AWS ARN from the IAM console (Security credentials -> Assigned MFA device). This is saved to your .aws/credentials file'
    )

    subparser = argument_parser.add_subparsers(
        title='subcommand',
        description='The subcommand to use among this suite of tools',
        dest='picked_cmd',
        help='Select a subcommand to execute'
    )

    manage_mfa = subparser.add_parser(
        'mfa',
        description='Manage MFA',
        help='Add MFA secret configuration key or get a token for registered MFA secret'

    )

    manage_session = subparser.add_parser(
        'session',
        description='Manage AMS CLI MFA session',
        help='Start AWS MFA session, use stored token or provide custom token "--custom-token"'
    )

    mfa_group = manage_mfa.add_mutually_exclusive_group(required=True)
    mfa_group.add_argument(
        '--add-secret',
        action='store_true',
        help='Add MFA secret configuration key and genereate session tokens'
    )

    mfa_group.add_argument(
        '--get-token',
        action='store_true',
        help='Display token, valid for 30 sec. Token added to clipboard to be used for GUI console login'
    )

    mfa_group.add_argument(
        '--del-secret',
        action='store_true',
        help='Delete stored secret'
    )

    manage_mfa.add_argument(
        '--non-aws',
        action='store_true',
        help='Store non aws secret and generate MFA token'
    )

    session_group = manage_session.add_mutually_exclusive_group(required=True)
    session_group.add_argument(
        '--start',
        action='store_true',
        help='Start AWS MFA session for the selected profile'
    )

    manage_session.add_argument(
        '--duration',
        help='Specify session token duration in minutes before it expires. Duration limitation as per AWS is minimum 15 and maximum 720 minutes, default is 720 minutes/12 Hrs',
        type=check_duration,
        default=720
    )

    manage_session.add_argument(
        '--custom-token',
        help='Provide 6 digit token from your MFA devices',
        type=check_custom_token
    )

    if len(argv) == 1:
        argument_parser.print_help(stderr)
        return False

    parsed_args = argument_parser.parse_args()

    # Make sure either of the sub-command is specified
    if parsed_args.picked_cmd is None:
        argument_parser.print_help(stderr)
        return False

    config = configparser.ConfigParser()
    config.read(parsed_args.credential_path)
    permanent_profile = '{}-permanent'.format(parsed_args.profile)

    # Check if the profile exist in credentials file
    if parsed_args.profile not in config.sections():
        profile_name = permanent_profile
    else:
        profile_name = parsed_args.profile
    
    # We want to skip profile check if the picked command is mfa and non-aws
    if parsed_args.picked_cmd == 'session':
        non_aws = False
    elif parsed_args.picked_cmd == 'mfa':
        non_aws = parsed_args.non_aws

    if (not non_aws) and (profile_name not in config.sections()):
        print('Profile "{}" not found in ~/.aws/credentials or in env variable AWS_PROFILE.\nSet the profile (--profile <name>) to any one from available list - \
             \n\n {}'.format(parsed_args.profile, config.sections()))
        return False

    # Manage non aws MFA token
    if parsed_args.picked_cmd == 'mfa' and parsed_args.non_aws:
        return handle_mfa(parsed_args)
    
    # This will add suffix '-permanent' to the original profile
    if (parsed_args.profile and not permanent_profile) in config.sections():
        config.add_section(permanent_profile)
        for key in config.items(parsed_args.profile):
            config.set(permanent_profile, key[0], key[1])
        with open(parsed_args.credential_path, 'w') as configfile:
            config.write(configfile)

    config.read(parsed_args.credential_path)

    # Establish STS connection with profiles access key and secret
    try:
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=config.get(
                permanent_profile, 'aws_access_key_id'),
            aws_secret_access_key=config.get(
                permanent_profile, 'aws_secret_access_key')
        )
    except Exception as e:
        print(e)
        return False
    
    # Get AWS MFA ARN to be used as service name in keyring and getting session token for MFA
    if parsed_args.arn is None:

        if 'aws_arn_mfa' in config[profile_name]:
            parsed_args.arn = config[profile_name]['aws_arn_mfa']
        else:

            # Generate user_arn and replace "user" with "mfa"
            try:
                arn_result = sts_client.get_caller_identity()

            except ClientError as e:
                print(e)
                return False

            if arn_result['ResponseMetadata']['HTTPStatusCode'] != 200:
                argument_parser.error(
                    arn_result['ResponseMetadata']['HTTPStatusCode'])

            # This should result in mfa_arn
            #"arn:aws:iam::<AWS acount ID>:user/<user name>" ==> arn:aws:iam::<AWS acount ID>:mfa/<user name
            parsed_args.arn = arn_result['Arn'].replace(':user/', ':mfa/', 1)
    
    # Handle MFA or SESSION based on picked command
    if parsed_args.picked_cmd == 'mfa':
        return handle_mfa(parsed_args)
    elif parsed_args.picked_cmd == 'session':
        return handle_session(parsed_args, sts_client, config)

    return 64


if __name__ == '__main__':
    exit(main())
