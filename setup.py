# -*- encoding: utf-8 -*-
import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand

import zoro


class PyTest(TestCommand):
    test_package_name = 'zoro'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        _test_args = [
            '--verbose',
            '--ignore=build',
            '--cov={0}'.format(self.test_package_name),
            '--cov-report=term-missing',
            '--pep8',
        ]
        extra_args = os.environ.get('PYTEST_EXTRA_ARGS')
        if extra_args is not None:
            _test_args.extend(extra_args.split())
        self.test_args = _test_args
        self.test_suite = True

    def run_tests(self):
        import pytest
        from pkg_resources import normalize_path, _namespace_packages

        # Purge modules under test from sys.modules. The test loader will
        # re-import them from the build location. Required when 2to3 is used
        # with namespace packages.
        if sys.version_info >= (3,) and getattr(self.distribution, 'use_2to3', False):
            #module = self.test_args[-1].split('.')[0]
            module = self.test_package_name
            if module in _namespace_packages:
                del_modules = []
                if module in sys.modules:
                    del_modules.append(module)
                module += '.'
                for name in sys.modules:
                    if name.startswith(module):
                        del_modules.append(name)
                map(sys.modules.__delitem__, del_modules)

            ## Run on the build directory for 2to3-built code
            ## This will prevent the old 2.x code from being found
            ## by py.test discovery mechanism, that apparently
            ## ignores sys.path..
            ei_cmd = self.get_finalized_command("egg_info")

            ## Replace the module name with normalized path
            #self.test_args[-1] = normalize_path(ei_cmd.egg_base)
            self.test_args.append(normalize_path(ei_cmd.egg_base))

        errno = pytest.main(self.test_args)
        sys.exit(errno)


tests_require = [
    'pytest',
    'pytest-pep8',
    'pytest-cov',
]

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='zoro',
    version=zoro.__version__,
    url='https://github.com/onlytiancai/zoro',
    license='MIT License (MIT)',
    author='onlytiancai',
    install_requires=[],
    author_email='onlytiancai@gmail.com',
    description=u'一个可扩展的单机监控软件',
    long_description=open('README.md').read(),
    packages=['zoro'],
    include_package_data=True,
    platforms='any',
    test_suite='zoro.tests',
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
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    **extra

)
