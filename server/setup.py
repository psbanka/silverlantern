#!/usr/bin/env python

#import os
#import sys
#sys.path.insert(0, '.') # Not sure why we need this

from distutils.core import setup
#from src._project_info import PROJECT_INFO
#from src._component_info import COMPONENT_INFO
#from src._version import VERSION_INFO


def main():
    #cmdclasses = {}
    # 'test' is the parameter as it gets added to setup.py

    setup(
        name="SilverLantern",
        description="For learning words",
        version='0.1',
        packages=['main'],
        #package_data=[],
        package_dir={"main": "main"},
        #data_files=PROJECT_INFO.get("data_files"),
        author="Peter Banka",
        author_email="peter.banka@gmail.com",
        #long_description=PROJECT_INFO["long_description"],
        #scripts=PROJECT_INFO.get("scripts"),
        provides=["main"],
        #classifiers=PROJECT_INFO["classifiers"],
        url='http://silverlantern.net',
    )

if __name__ == "__main__":
    main()
