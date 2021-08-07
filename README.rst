.. |ci| image:: https://github.com/djmattyg007/freiner/workflows/CI/badge.svg?branch=master
   :target: https://github.com/djmattyg007/freiner/actions?query=branch%3Amaster+workflow%3ACI
.. |codecov| image:: https://codecov.io/gh/djmattyg007/freiner/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/djmattyg007/freiner
.. |pypi| image:: https://img.shields.io/pypi/v/freiner.svg
   :target: https://pypi.python.org/pypi/freiner
.. |license| image:: https://img.shields.io/pypi/l/freiner.svg
   :target: https://pypi.python.org/pypi/freiner

*******
Freiner
*******
|ci| |codecov| |pypi| |license|

*Freiner* provides utilities to implement rate limiting using various strategies and storage
backends such as Redis & Memcached.

The French word "freiner" means "to slow down", which is what you'll need to do if you are
rate-limited :)

Currently this project supports Python 3.7, 3.8 and 3.9.

History
-------

Freiner is a fork of a project named `limits <https://github.com/alisaifee/limits>`_. I forked it
to add type hints, and to resolve several outstanding problems at the time.

Links
-----

* `Documentation <http://limits.readthedocs.org>`_
* `Changelog <http://limits.readthedocs.org/en/stable/changelog.html>`_
