class BibCleanException(Exception):
    """Generic parent exception"""
    pass


class BibCleanWarning(Warning):
    """Generic parent warning"""
    pass


class RefConnectError(BibCleanException):
    """Raised for issues connecting to references source"""
    pass


class RefGetError(BibCleanException):
    """Raised for issues getting items from reference source"""
    pass


class RefUpdateError(BibCleanException):
    """Raised for issues updating reference source"""
    pass


class RefNoFieldDefined(BibCleanException):
    """Errors when field is not defined in Item._field_names"""
    pass


class RemoteProxyListError(BibCleanException):
    """When urllib or json parse cannont process request"""
    pass


class RemoteProxyListFormatError(BibCleanException):
    """Remote Proxy List invalid format"""
    pass


class ProxyFormatError(BibCleanException):
    """Proxy string is not correct format"""
    pass


class ProxyNameNotFound(BibCleanWarning):
    """Proxy name is not found in proxy list"""
    pass
