# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 11:30:47 2025

@author: Lucian
"""

from setuptools import setup, find_packages

setup(
    name='tally',  # Or whatever you want to call your project
    version='0.1.0',  # Or your initial version
    packages=find_packages(),
    install_requires=[
        # List your dependencies here (from requirements.txt)
        'Flask==3.0.2',
        'cryptography==42.0.5',
        'pytest==8.2.0',
        'requests==2.31.0',
        'click==8.1.7',
    ],
    entry_points={
        'console_scripts': [
            'tally_wallet = tally_wallet.cli:cli',  # Create a command-line entry point
        ],
    },
)