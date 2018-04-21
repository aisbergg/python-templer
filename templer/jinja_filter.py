""" Custom Jinja2 filters """

from jinja2 import StrictUndefined, UndefinedError


class MandatoryError(UndefinedError):
    def __init__(self, message):
        super().__init__(message)


def mandatory(value, error_message=u''):
    """ Throws an 'UndefinedError' with an custom error massage, when value is undefined

    Args:
        value: Some value
        error_message (str): Massage to be displayed, when an exception is thrown

    Returns:
        value.  Unchanged value

    """
    if type(value) is StrictUndefined:
        raise MandatoryError(error_message)

    return value


# register the filters
filters = {
    'mandatory': mandatory
}
