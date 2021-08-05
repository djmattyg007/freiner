.. currentmodule:: freiner

Custom storage backends
-----------------------

TODO: This section is out of date. Gotta re-word it to discuss the Protocol classes.

The **Freiner** package ships with a few storage implementations which allow you
to get started with some common data stores (redis & memcached) used for rate limiting.

To accommodate customizations to either the default storage backends or
different storage backends altogether, **Freiner** uses a registry pattern that
makes it painless to add your own custom storage (without having to submit patches
to the package itself).

Creating a custom backend requires:

    #. Subclassing :class:`freiner.storage.Storage`
    #. Providing implementations for the abstract methods of :class:`freiner.storage.Storage`
    #. If the storage can support the :ref:`moving-window` strategy - additionally implementing
       the `acquire_entry` instance method.
    #. Providing naming *schemes* that can be used to lookup the custom storage in the storage registry.
       (Refer to :ref:`storage-scheme` for more details)

Example
=======
The following example shows two backend stores: one which doesn't implement the
:ref:`moving-window` strategy and one that does.::

    from urllib.parse import urlparse
    from freiner.storage import Storage
    import time

    class AwesomeStorage(Storage):
        def __init__(self, uri: str, **kwargs):
            self.awesomesness = kwargs.get("awesomeness", None)
            parsed_uri = urlparse(uri)
            self.host = parsed_uri.netloc
            self.port = parsed_uri.port

        def check(self) -> bool:
            return True

        def get_expiry(self, key: str) -> int:
            return int(time.time())

        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0


    class AwesomerStorage(Storage):
        def __init__(self, uri: str, **kwargs):
            self.awesomesness = kwargs.get("awesomeness", None)
            parsed_uri = urlparse(uri)
            self.host = parsed_uri.netloc
            self.port = parsed_uri.port

        def check(self) -> bool:
            return True

        def get_expiry(self, key: str) -> int:
            return int(time.time())

        def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
            return 1

        def get(self, key: str) -> int:
            return 0

        def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
            return True
