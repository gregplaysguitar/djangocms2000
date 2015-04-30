#!/usr/bin/env python
# coding: utf8

from setuptools import setup, find_packages
from setuptools.command.test import test

# avoid importing the module 
exec(open('cms/_version.py').read())

setup(
    name='djangocms2000',
    version=__version__,
    description='Flexible Django CMS with edit-in-place capability',
    long_description=open('readme.md').read(),
    author='Greg Brown',
    author_email='greg@gregbrown.co.nz',
    url='https://github.com/gregplaysguitar/djangocms2000',
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=['Django>=1.4',],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)
