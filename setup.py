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
    tests_require=['pytest==2.9.2'],
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='debian packaging  package daemon dh-make',
)
