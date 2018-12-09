import os

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pySCM",
    version="0.1.1",
    author="Jared Lewis",
    author_email="jared@bodekerscientific.com",
    description="A basic simple climate model in Python.",
    license="BSD",
    keywords="simple climate model SCM climate science",
    url="http://pythonhosted.org/pySCM",
    packages=['pySCM'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Science/Research"
    ]
)
