# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

def readfile(path):
    with open(path, 'rb') as stream:
        return stream.read().decode('utf-8')

version = readfile('runwith/version.txt').strip()
readme = readfile('README.rst')

setup(
    name='runwith',
    maintainer='Andre Caron',
    maintainer_email='andre.l.caron@gmail.com',
    url='https://github.com/AndreLouisCaron/runwith',
    description="Poor man's shell operations",
    long_description=readme,
    version=version,
    packages=find_packages(),
    package_data={
        'runwith': [
            'version.txt',
        ],
    },
    entry_points={
        'console_scripts': [
            'runwith = runwith:main',
        ],
    },
)
