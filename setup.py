# -*- encoding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import io
import os
import sys

import zoro

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGES.md')


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name='zoro',
    version=zoro.__version__,
    url='https://github.com/onlytiancai/zoro',
    license='MIT License (MIT)',
    author='onlytiancai',
    tests_require=['pytest', 'tox'],
    install_requires=['python-daemon'],
    cmdclass={'test': Tox},
    author_email='onlytiancai@gmail.com',
    description=u'一个可扩展的单机监控软件',
    long_description=long_description,
    packages=['zoro'],
    include_package_data=True,
    platforms='any',
    test_suite='zoro.test.test_zoro',
    classifiers=['Programming Language :: Python',
                 'Development Status :: 3 - Alpha',
                 'Natural Language :: Chinese (Simplified)',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: POSIX :: Linux',
                 'Topic :: System :: Monitoring',
                 # https://pypi.python.org/pypi?:action=list_classifiers
                 ],
    extras_require={
        'testing': ['pytest'],
    }
)
