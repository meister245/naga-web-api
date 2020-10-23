#!/usr/bin/env python3

import re
from setuptools import setup


with open('./naga_web_api/__init__.py', 'r') as f:
    version = re.search(r'(?<=__version__ = .)([\d\.]*)', f.read()).group(1)

with open('./README.md', 'r') as f:
    readme = f.read()


if __name__ == '__main__':
    setup(
        name='naga-web-api',
        version=version,
        author='Zsolt Mester',
        author_email='',
        description='Unoffial client for Naga.com broker',
        long_description=readme,
        license='MIT',
        url='https://github.com/meister245/naga-web-api',
        project_urls={
            "Code": "https://github.com/meister245/naga-web-api",
            "Issue tracker": "https://github.com/meister245/naga-web-api/issues",
        },
        packages=[
            'naga_web_api'
        ],
        install_requires=[
            'cachetools',
            'requests'
        ],
        python_requires='>=3.6',
        include_package_data=False
    )