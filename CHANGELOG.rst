.. :changelog:

=========
Changelog
=========

v3.0.0 - 2021-08-08
===================

This release provides several improvements and resolves several issues that were
only identified after the initial release of ``Freiner``. Unfortunately some of
these changes necessitate another major version bump.

* Moved strategy classes into separate files, one per strategy class.
* Instead of a "base" ``Storage`` ``Protocol`` class and a ``MovingWindowStorage`` class that extends from it,
  there are now two totally separate ``Protocol`` classes: ``FixedWindowStorage`` and ``MovingWindowStorage``.
  They are compatible with each other, so storage backends can (and do) implement both of them simultaneously.
* All time values are now returned as floats.
  Previously the interfaces claimed to only be returning integers, but I'm pretty sure floats were sometimes returned.
* Some methods that previously returned tuples will now return named tuples.
* Some timing issues that likely only arised in testing code have been resolved.
* More symbols are available for import from the top-level ``freiner`` package.

  * The only modules that aren't available should be ones that rely on external dependencies (eg. redis or memcached).
* An internal locking mechanism has been renamed to properly indicate it is not part of the public API.
* Tightened up the comparison logic for rate limit items.
* Cleaned up some quirks in the rate limit string parser.
* Massive improvements to the documentation, including class and method docstrings.
* Documentation published at https://freiner.readthedocs.io
* Minor adjustments to some exception messages.

v2.0.0 - 2021-08-05
===================

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

v1.0.0 - 2015-01-08
===================

* Initial import of common rate limiting code from `Flask-Limiter <https://github.com/alisaifee/flask-limiter>`_
