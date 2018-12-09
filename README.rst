pySCM
=====

+----------------+-----------+--------+
| |Build Status| | |Codecov| | |Docs| |
+----------------+-----------+--------+

.. sec-begin-index


pySCM is a simple climate model developed in Python for producing timeseries of
annual mean global mean surface temperature from projections of greenhouse gases.
pySCM is purposely very simple using only a few couple differential equations.
This means that pySCM is very fast and is controlled using only a few parameters.

.. sec-end-index

Documentation
-------------

Instructions for using pySCM and a description of the equations used in pySCM are
provided in the `Documentation <https://openscm.readthedocs.io/en/latest/>`_.

.. sec-begin-development

Development
-----------

.. code:: bash

    git clone git@github.com:bodekerscientific/pyscm.git
    pip install -e .

Tests can be run locally with

::

    python setup.py test

.. sec-end-development

.. |Build Status| image:: https://img.shields.io/travis/bodekerscientific/pyscm.svg
    :target: https://travis-ci.org/bodekerscientific/pyscm
.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
    :target: https://pyscm.readthedocs.io/en/latest/
.. |Codecov| image:: https://img.shields.io/codecov/c/github/bodekerscientific/bodekerscientific.svg
    :target: https://codecov.io/gh/bodekerscientific/pyscm
