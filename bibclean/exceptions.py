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
