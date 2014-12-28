#!/usr/bin/env python
import codecs
import setuptools
import sys

from setupext import gitversion


with codecs.open('README.rst', 'rb', encoding='utf-8') as file_obj:
    long_description = '\n' + file_obj.read()

install_requirements = []
test_requirements = []

with open('test-requirements.txt', 'r') as file_obj:
    test_requirements.extend(
        line.strip() for line in file_obj
        if not line.startswith('#')
    )

if sys.version_info < (3, ):
    test_requirements.append('mock>1.0,<2')


setuptools.setup(
    name='setupext-gitversion',
    version=gitversion.__version__,
    author='Dave Shawley',
    author_email='daveshawley@gmail.com',
    url='http://github.com/dave-shawley/setupext-gitversion',
    description='PEP-440 compliant versioning helper',
    long_description=long_description,
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    namespace_packages=['setupext'],
    zip_safe=True,
    platforms='any',
    install_requires=install_requirements,
    tests_require=test_requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Setuptools Plugin',
        'Development Status :: 1 - Planning',
    ],
    entry_points={
        'distutils.commands': [
        ],
    },
)
