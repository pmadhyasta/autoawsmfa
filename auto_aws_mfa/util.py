#!/usr/bin/env python3


from argparse import ArgumentTypeError
from os import name, path

# Validate if the duration is within the AWS allowed limits
def check_duration(value):
    ivalue = int(value)
    if ivalue not in range(15, 721):
        raise ArgumentTypeError(
            "Duration in minutes should be between 15 - 720")
    return ivalue

# Depending on the OS the script is run get credentials path
def get_credentials_path():
    if name == 'posix':
        return path.expanduser(r'~/.aws/credentials')
    elif name == 'nt':
        return path.expanduser(r'%UserProfile%\.aws\credentials')
    else:
        return None

# Validate if the custom token is in acceptable range/format
def check_custom_token(value):
    cvalue = str(value).replace(" ", "")
    if len(cvalue) < 6:
        raise ArgumentTypeError(
            "Custom Token should be minimum 6 digit long without space")
    elif not cvalue.isdigit():
        raise ArgumentTypeError(
        "Custom Token should not conain characters")
    return cvalue

# Handle user option
def ask_user(question):
    check = str(input(question)).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input "{}"'.format(check))
            return ask_user(question)
    except Exception as e:
        print('Please enter valid inputs! {}'.format(e))
        return ask_user(question)

