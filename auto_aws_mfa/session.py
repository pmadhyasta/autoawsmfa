#!/usr/bin/env python3

from .mfa import get_token
from botocore.exceptions import ClientError

def handle_session(parsed_args, sts_client, config):

    if parsed_args.start:

        if parsed_args.custom_token:
            token_code = parsed_args.custom_token
        else:
            token_code = get_token(parsed_args.profile, parsed_args.arn)

        try:
            # Get AWS Session details
            session_token = sts_client.get_session_token(
                DurationSeconds=parsed_args.duration*60,
                SerialNumber=parsed_args.arn,
                TokenCode=str(token_code)
            )

        except ClientError as e:
            print(e)
            return False

        except Exception as e:
            print('MFA Token could be expired {}, try again!'.format(e))
            return False

        if session_token['ResponseMetadata']['HTTPStatusCode'] == 200:
            
            # Assign session specific key:values
            options = [
                ('aws_access_key_id', 'AccessKeyId'),
                ('aws_secret_access_key', 'SecretAccessKey'),
                ('aws_session_token', 'SessionToken'),
                ('aws_security_token', 'SessionToken'),
            ]
            for option, value in options:
                
                # Store session data to credentials
                config.set(
                    parsed_args.profile,
                    option,
                    session_token['Credentials'][value]
                )
            config.set(
                parsed_args.profile,
                'expiration',
                session_token['Credentials']['Expiration'].strftime(
                    '%Y-%m-%d %H:%M:%S')
            )

            with open(parsed_args.credential_path, 'w') as configfile:
                config.write(configfile)
            print('Session token updated into credentials file!\nSession will expire on {}'.format(
                session_token['Credentials']['Expiration'].strftime('%Y-%m-%d %H:%M:%S')))
            return True
