# -*- encoding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
from setuptools.command.install import install
from distutils import log
import io
import os
import sys
import shutil

import zoro

here = os.path.abspath(os.path.dirname(__file__))
user_home_path = os.getenv("HOME")
user_plugins_path = os.path.join(user_home_path, '.zoro/plugins/')
user_config_path = os.path.join(user_home_path, '.zoro/config.json')


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGES.md')

class OverrideInstall(install):
    def run(self):
        install.run(self)
        if not os.path.exists(user_plugins_path):
            log.info("mkdir %s", user_plugins_path)
            os.makedirs(user_plugins_path)

        if not os.path.exists(user_config_path):
            log.info("copy config.json to %s", user_plugins_path)
            shutil.copy('./zoro/etc/config.json', user_config_path)

setup(
    name='zoro',
    version=zoro.__version__,
    url='https://github.com/onlytiancai/zoro',
    license='MIT License (MIT)',
    author='onlytiancai',
    install_requires=['python-daemon'],
    cmdclass={'install': OverrideInstall},
    author_email='onlytiancai@gmail.com',
    description=u'一个可扩展的单机监控软件',
    long_description=long_description,
    packages=['zoro'],
    include_package_data=True,
    platforms='any',
    test_suite='zoro.test.test_zoro',
    entry_points = {"console_scripts": ["zoro= zoro.zoromain:run"]},
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
)
