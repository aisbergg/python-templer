class FileExistsError(IOError):
    """ File exist exception
    
    Args:
        message (str): Message passed with the exception
        
    """
    def __init__(self, message):
        super(FileExistsError, self).__init__("File already exists: {0}".format(message))
        
        
class FileNotFoundError(IOError):
    """ File not found exception
    
    Args:
        message (str): Message passed with the exception
        
    """
    def __init__(self, message):
        super(FileNotFoundError, self).__init__("File not found: {0}".format(message))
        

class NotAFileError(IOError):
    """ Is not a file exception
    
    Args:
        message (str): Message passed with the exception
        
    """
    def __init__(self, message):
        super(NotAFileError, self).__init__("Is not a file: {0}".format(message))
        

class NotADirectoryError(IOError):
    """ Path is not a directory
    
    Args:
        message (str): Message passed with the exception
        
    """
    def __init__(self, message):
        super(NotADirectoryError, self).__init__("Is not a dir: {0}".format(message))
        