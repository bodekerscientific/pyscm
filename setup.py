from os.path import join, dirname
from setuptools import setup, find_packages

import versioneer


def read(fname):
    return open(join(dirname(__file__), fname)).read()


setup(
    name="pySCM",
    version=versioneer.get_version(),
    author="Jared Lewis",
    author_email="jared@bodekerscientific.com",
    description="A basic simple climate model in Python",
    license="MIT",
    keywords="simple climate model SCM climate science",
    url="http://pythonhosted.org/pySCM",
    packages=find_packages(),
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "matplotlib",
        "numpy"
    ],
    project_urls={
        "Bug Reports": "https://github.com/bodekerscientific/pyscm/issues",
        "Source": "https://github.com/bodekerscientific/pyscm/",
    },
    tests_require=["pytest", "pytest-cov", "codecov"],
    setup_requires=["pytest-runner"],
    extras_require={
        "docs": ["sphinx >= 1.4", "sphinx_rtd_theme", "sphinx-autodoc-typehints"],
        "dev": [
            "setuptools>=38.6.0",
            "twine>=1.11.0",
            "wheel>=0.31.0",
        ],
    },
    cmdclass=versioneer.get_cmdclass()
)
