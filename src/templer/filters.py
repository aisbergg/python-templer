""" Custom Jinja2 filters """

from jinja2 import Undefined, UndefinedError


def required(value, error_massage=u''):
    """ Throws an 'UndefinedError' with an custom error massage, when value is undefined
    
    Args:
        value: Some value
        error_massage (str): Massage to be displayed, when an exceptin is thrown
    
    Returns:
        value.  Unchanged value
        
    """

    if type(value) is Undefined:
        raise UndefinedError(error_massage)
    
    return value