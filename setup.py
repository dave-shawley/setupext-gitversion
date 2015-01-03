#!/usr/bin/env python
import codecs
import setuptools
import sys

from setupext import gitversion


local_id = ''
try:
    with open('LOCAL-VERSION', 'r') as version_file:
        local_id = version_file.readline().strip()
except IOError:
    pass

with codecs.open('README.rst', 'rb', encoding='utf-8') as file_obj:
    long_description = '\n' + file_obj.read()

install_requirements = []
test_requirements = []

with open('requirements.txt', 'r') as file_obj:
    install_requirements.extend(
        line.strip() for line in file_obj
        if not line.startswith('#')
    )

with open('test-requirements.txt', 'r') as file_obj:
    test_requirements.extend(
        line.strip() for line in file_obj
        if not line.startswith('#')
    )

if sys.version_info < (2, 7):
    test_requirements.append('unittest2')
if sys.version_info < (3, ):
    test_requirements.append('mock>1.0,<2')


setuptools.setup(
    name='setupext-gitversion',
    version=gitversion.__version__ + local_id,
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Setuptools Plugin',
        'Development Status :: 4 - Beta',
    ],
    entry_points={
        'distutils.commands': [
            'git_version = setupext.gitversion:GitVersion',
        ],
    },
    cmdclass={
        'git_version': gitversion.GitVersion,
    },
)
