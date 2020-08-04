#!/usr/bin/env python3

"""Code for installing the AutoAWSMFA script."""

#  Copyright (c) Prashant Madhyasta 2020. This file is part of AutoAWSMFA Script.
#
#      AutoAWSMFA is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      AutoAWSMFA is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with AutoAWSMFA.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import auto_aws_mfa

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='AutoAWSMFA',
    version=auto_aws_mfa.__version__,
    description='A Python script and library for managing MFA token and AWS Session tokens.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='AGPLv3',
    url='https://github.com/pmadhyasta/autoawsmfa',
    author='Prashant Madhyasta',
    author_email='prashanth.madhyasta@gmail.com',
    scripts=[],
    include_package_data=True,
    packages=find_packages(),
    package_data={},
    python_requires='>=3.5, <4',  # assume Python 4 will break
    install_requires=['botocore', 'packaging', 'python-dateutil', 'boto3', 'keyring', 'pyotp', 'pyperclip'],
    entry_points={
        'console_scripts': [
            'autoawsmfa = auto_aws_mfa.__main__:main'
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Security'
    ],
    keywords=[
        'AWS', 'IAM', 'Security', 'MFA', 'AWS Session Token', 'AWS MFA', 'autoawsmfa', 'auto_aws_mfa', 'AWS MFA', 'Token'
    ],
    zip_safe=False
)