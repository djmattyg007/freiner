.. :changelog:

Changelog
---------

v2.0.0 - 2021-08-05
-------------------

First release after the fork from ``limits``.

* Renamed ``HISTORY.rst`` to ``CHANGELOG.rst``.
* Support only Python 3.7 and above.

  * Support for Python 2.7 has been completely removed.
  * Support for pypy may exist, but is not being tested for. Patches are welcome, even if support for some storage backends is missing.
* Removed code related to Google App Engine (GAE), as I cannot meaningfully maintain it.
* Removed old references to Flask code from before the original split from Flask-Limiter.
* Removed tests for Redis Cluster. Support is provided on a best-effort basis. Patches welcome.
* Removed Dependabot config. This may return at some point.
* Removed versioneer, CodeQL tooling, and overcommit config.
* Removed OS-specific stuff for running tests. The new test suite is currently only tested on Linux, with the latest versions of docker and docker-compose.
  Patches are welcome as long as they don't introduce significant complexity.
* Removed the primary Makefile. Replaced it with ``invoke``, which is OS-agnostic.
* Replaced all code quality and formatting tools with ``flake8``, ``black``, and ``isort``.
* Introduced type annotations and ``mypy``.
* Moved all configuration out of ``setup.py``, mostly in to ``setup.cfg``.
* Eliminated the storage registry. There is no generic URI parsing system or generic storage factory now.
* Changed the ``Storage`` base class to a ``Protocol``.
* Storage classes no longer accept URIs to their constructors.

  * Most storage classes have a ``from_uri`` class method to parse URIs.
  * Storage class constructors now accept instances of the actual backend client.
    This allows you to initialise the relevant client however you want, rather than being restricted to what the URI parser function is capable of.
* Removed usage of deprecated ``inspect`` functionality.
* Added many new tests to improve test quality and coverage.
* Replaced usage of ``hiro`` with ``freezegun`` in tests.
* Various error types and messages have been improved.
* Two unmerged PRs submitted to ``limits`` have been applied to this project.

  * https://github.com/alisaifee/limits/pull/69
  * https://github.com/alisaifee/limits/pull/71

Documentation is still a work in progress at this stage. It will eventually be published to ReadTheDocs.

v1.5.1 - 2020-02-25
-------------------

* Bug fix

  * Remove duplicate call to ttl in RedisStorage
  * Initialize master/slave connections for RedisSentinel once

v1.5 - 2020-01-23
----

* Bug fix for handling TTL response from Redis when key doesn’t exist
* Support Memcache over unix domain socket
* Support Memcache cluster
* Pass through constructor keyword arguments to underlying storage
  constructor(s)
* CI & test improvements

v1.4.1 - 2019-12-15
-------------------

* Bug fix for implementation of clear in MemoryStorage
  not working with MovingWindow

v1.4 - 2019-12-14
-----------------

* Expose API for clearing individual limits
* Support for redis over unix domain socket
* Support extra arguments to redis storage

v1.3 - 2018-01-28
-----------------

* Remove pinging redis on initialization

v1.2.1 - 2017-01-02
-------------------

* Fix regression with csv as multiple limits

v1.2.0 - 2016-09-21
-------------------

* Support reset for RedisStorage
* Improved rate limit string parsing

v1.1.1 - 2016-03-14
-------------------

* Support reset for MemoryStorage
* Support for `rediss://` storage scheme to connect to redis over ssl

v1.1 - 2015-12-20
-----------------

* Redis Cluster support
* Authentiation for Redis Sentinel
* Bug fix for locking failures with redis.

v1.0.9 - 2015-10-08
-------------------

* Redis Sentinel storage support
* Drop support for python 2.6
* Documentation improvements

v1.0.7 - 2015-06-07
-------------------

* No functional change

v1.0.6 - 2015-05-13
-------------------

* Bug fixes for .test() logic

v1.0.5 - 2015-05-12
-------------------

* Add support for testing a rate limit before hitting it.

v1.0.3 - 2015-03-20
-------------------

* Add support for passing options to storage backend

v1.0.2 - 2015-01-10
-------------------

* Improved documentation
* Improved usability of API. Renamed RateLimitItem subclasses.

v1.0.1 - 2015-01-08
-------------------

* Example usage in docs.

v1.0.0 - 2015-01-08
-------------------

* Initial import of common rate limiting code from `Flask-Limiter <https://github.com/alisaifee/flask-limiter>`_

















