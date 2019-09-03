#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

from binks import __version__

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['werkzeug_raw', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="xdd1874",
    author_email='bepox0531@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A simple WSGI web server.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='binks',
    name='binks',
    packages=find_packages(include=['binks']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Caratpine/binks',
    version=__version__,
    zip_safe=False,
    entry_points="""

    [console_scripts]
    binks=binks.main:main
    """
)
