#!/usr/bin/env python3

import pyotp
from getpass import getpass
import keyring
import pyperclip
from .util import check_custom_token, check_duration, ask_user

def set_secret(profile, arn, overwrite=None):
    
    # Check if secret is already registered
    if not overwrite and keyring.get_password(profile, arn):
        if ask_user("MFA secret key exist! Overwrite? (y/n) :"):
           return set_secret(profile, arn, overwrite=True)
        else:
            return False
    try:
        keyring.set_password(profile, arn, getpass(
            prompt='Enter MFA secret key :',))
    except Exception as e:
        print('Error setting secret :{}'.format(e))
        return False
    return True


def del_secret(profile, arn,):

    if keyring.get_password(profile, arn):
        if ask_user("Are you sure? (y/n) :"):
            try:
                keyring.delete_password(profile, arn)
                print("Secret deleted!")
                return True
            except Exception as e:
                print("Error deleting secret :{}".format(e))
                return False
        return False
    else:
        print("Secret key not found for user :{}".format(arn))
        return False



def get_token(profile, arn):

    try:
        mfa_token = keyring.get_password(profile, arn)

    except Exception as e:
        print('MFA secret key not set! {}'.format(e))
        if ask_user("Set secret now? (y/n) :"):
            set_secret(profile, arn)
        else:
            return False
    if not mfa_token:
        if ask_user("MFA secret configuration key not set! \nSet secret now? (y/n) :"):
            if (set_secret(profile, arn)):
                mfa_token = keyring.get_password(profile, arn)
        else:
            print("Cannot get token, MFA secret not set!")
            return False
    totp = pyotp.TOTP(mfa_token)
    return totp.now()


def handle_mfa(parsed_args):

    # For non-aws for each operation this is prompted to add/fetch/delete
    # Currently keyring doesnt have functionality to retrieve/list registered system/services
    # User should remember the application name and user name
    if parsed_args.non_aws:
        parsed_args.profile = input("Enter application name :")
        parsed_args.arn = input("Enter user name or email address :")

    if parsed_args.get_token:
        mfa_token = get_token(parsed_args.profile, parsed_args.arn)
        if not mfa_token:
            return False
    elif parsed_args.add_secret:
        if set_secret(parsed_args.profile, parsed_args.arn):
            mfa_token = get_token(parsed_args.profile, parsed_args.arn)
        else:
            return False
    elif parsed_args.del_secret:
        return del_secret(parsed_args.profile, parsed_args.arn)
    else:
        return False

    pyperclip.copy(mfa_token)
    print("OTP copied to clipboard. Valid for 30 sec only! :{}".format(
        pyperclip.paste()))
    return True
