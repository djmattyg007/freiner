from freiner.errors import FreinerConfigurationError


SCHEMES = {}


class StorageRegistry(type):
    def __new__(mcs, name, bases, dct):
        storage_scheme = dct.get('STORAGE_SCHEME', None)
        if not bases == (object,) and not storage_scheme:
            raise FreinerConfigurationError(
                "%s is not configured correctly, "
                "it must specify a STORAGE_SCHEME class attribute"
                % name
            )

        cls = super(StorageRegistry, mcs).__new__(mcs, name, bases, dct)
        if storage_scheme:
            if isinstance(storage_scheme, str):
                SCHEMES[storage_scheme] = cls
            else:
                for scheme in storage_scheme:
                    SCHEMES[scheme] = cls

        return cls
