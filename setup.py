from setuptools import setup, find_packages
from pip.req import parse_requirements

from debpackager.main import __version__

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='debpackager',
    version=__version__,
    packages=find_packages(),
    author='Sergey R.',
    url='https://github.com/urban48/debpackager',
    license='MIT',
    author_email='segrog@gmail.com',
    description='debpackager package any project to debian package',
    entry_points={
        'console_scripts': [
            'debpackager=debpackager.main:main'
        ]
    },
    install_requires=reqs,
    tests_require=['pytest==2.9.2', 'pytest-pythonpath==0.7'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='debian deb packaging package daemon dh-make',
)
