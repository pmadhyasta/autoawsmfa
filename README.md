# Auto AWS MFA

Auto AWS MFA (autoawsmfa) is a script for managing AWS Session tokens enabled with MFA, this can also be used to generate MFA tokens for other applications that provides secret key while configuring MFA.



# Installation

## Requirements

autoawsmfa is built using the `botocore & boto3` library and Python 3.5+. Python 2  is not supported. autoawsmfa 
also requires `keyring, pyotp and pyperclip` (available on `pip`).

## Installation from Pip

~~~bash
pip install AutoAWSMFA
~~~

## Installation From Source Code

Clone the repository:

~~~bash
git clone git@github.com:pmadhyasta/autoawsmfa.git
~~~

Then install with Pip:

~~~bash
cd autoawsmfa
pip install .
~~~

# Usage

~~~bash
usage: autoawsmfa [-h] [-v] [-p PROFILE] [--credential-path CREDENTIAL_PATH] [--arn ARN] {mfa,session} ...

Auto update your AWS CLI MFA session token

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show the version number and exit
  -p PROFILE, --profile PROFILE
                        AWS profile to store the session token. Default looks for "AWS_PROFILE"
  --credential-path CREDENTIAL_PATH
                        path to the aws credentials file
  --arn ARN             AWS ARN from the IAM console (Security credentials -> Assigned MFA device). This is saved to your .aws/credentials file

subcommand:
  The subcommand to use among this suite of tools

  {mfa,session}         Select a subcommand to execute
    mfa                 Add MFA secret configuration key or get a token for registered MFA secret
    session             Start AWS CLI MFA session, use stored token or provide custom token "--custom-token"
~~~

## Manage MFA

### Add Secret
Add a new MFA secret to a specific AWS Profile

~~~bash
autoawsmfa --profile <profile name> mfa --add-secrete
~~~

Profile name should exist in '~/.aws/credentials' for posix or in '%UserProfile%\.aws\credentials' fot NT/windows 

### Get Secret
Get MFA token from earlier added secret, token copied to clipboard to be used to login to AWS Console

~~~bash
autoawsmfa --profile <profile name> mfa --get-token
~~~

If the secret is not added earlier for the specified profile, it will prompt to add secret

### Delete Secret
Delete secret from keyring

~~~bash
autoawsmfa --profile <profile name> mfa --del-secret
~~~

Optional arguments that can be used
~~~bash
usage: autoawsmfa mfa [-h] (--add-secret | --get-token | --del-secret) [--non-aws]

Manage MFA

optional arguments:
  -h, --help    show this help message and exit
  --add-secret  Add MFA secret configuration key and genereate session tokens
  --get-token   Display token, valid for 30 sec. Token added to clipboard to be used for GUI console login
  --del-secret  Delete stored secret
  --non-aws     Store non aws secret and generate MFA token
~~~

### Non AWS MFA
This can be used to register the non AWS secrets such as OKTA or any thirdparty MFA enabled application.
This option prompts for application name and user name to register and retrieve token. You shoud make a note of application name and user name while registring as currently there is no option to list view the secrets stored. 

~~~bash
autoawsmfa mfa --non-aws --get-token
~~~

## Manage AWS Session

### Start session
Start the session for MFA secret registered profile

~~~bash
autoawsmfa --profile <profile name> session --start
~~~

Optional arguments can be given for duration and if a third party MFA device token should be used

~~~bash
usage: autoawsmfa session [-h] --start [--duration DURATION] [--custom-token CUSTOM_TOKEN]

Manage AMS CLI MFA session

optional arguments:
  -h, --help            show this help message and exit
  --start               Start AWS MFA session for the selected profile
  --duration DURATION   Specify session token duration in minutes before it expires. Duration limitation as per AWS is
                        minimum 15 and maximum 720 minutes, default is 720 minutes/12 Hrs
  --custom-token CUSTOM_TOKEN
                        Provide 6 digit token from your MFA devices
~~~

