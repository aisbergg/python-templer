import os
import jinja2
import yaml
import filters

def merge_dicts(x, y):
    """ Recursivly merges two dicts
    
    When keys exist in both the value of 'y' is used. 
    
    Args:
        x (dict): First dict
        y (dict): Second dict
    
    Returns:
        dict.  Merged dict containing values of x and y
        
    """
    if x is None and y is None:
        return dict()
    if x is None:
        return y
    if y is None:
        return x
    
    merged = dict(x,**y)
    xkeys = x.keys()

    # update 'branches' of the individual keys 
    for key in xkeys:
        # if this key is a dictionary, recurse                                  
        if type(x[key]) is dict and y.has_key(key):
            merged[key] = merge_dicts(x[key],y[key])
    return merged

class ContextFile:
    """ Represents a file with a context for jinja2 templates
    
    Args:
        path (str): Path to file
    
    """
    _path = ""
    _output_dir = ""
    _name = ""
    
    def __init__(self, path):
        if not os.path.isfile(path):
            raise IOError(self._format_error("File does not exist", "Loading file"))
        self._path = os.path.dirname(path)
        self._name = os.path.basename(path)
    
    def get_file_path(self):
        """ Gets the absolute path of the context file
        
        Returns:
            str.  Absolute path to context file
            
        """
        return os.path.join(self._path, self._name)
        
    def _read_context_file(self):
        """ Reads the content of the context file
        
        Returns:
            str.  Content of the context file
        
        """
        with open(self.get_file_path(), 'r') as f:
            return f.read().decode('utf-8')
        
    def get_context(self, env_context):
        """ Read the context from a file
        
        Args:
            prerender_context (bool): When true render the context form the files
            env_context (dict): Context to be used to prerender the 'context file'
            
        Returns:
            dict.  Context from the 'context file'
        
        Raises:
            TemplateError: If jinja2 syntax is invalid
            YAMLError: If yaml syntax is invalid
            TypeError: If wrong types are used in the 'defaults' section
            
        """
        file_content = self._read_context_file()
            
        if env_context is not None:
            env = jinja2.Environment(
                undefined=jinja2.Undefined
            )
            # Register additional filters
            env.filters['required'] = filters.required
            try:
                # render file with jinja2
                file_content = env.from_string(file_content) \
                    .render(env_context).encode('utf-8')
            except Exception as e:
                raise jinja2.exceptions.TemplateError(self._format_error("Jinja2 template error: {0}".format(e.message), "Prerendering"))
        
        try:
            parsed_context = yaml.load(file_content) or dict()
        except yaml.YAMLError, e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                raise yaml.YAMLError(self._format_error("YAML parsing error at line {0} column {1}".format(mark.line+1, mark.column+1), "Parsing YAML"))
            else:
                raise yaml.YAMLError(self._format_error("YAML parsing error: {0}".format(e.message), "Parsing YAML"))
        except Exception, e:
            raise Exception(self._format_error("Error: {0}".format(e.message), "Parsing YAML"))
        
        defaults = self._get_defaults(parsed_context, env_context)
        return merge_dicts(parsed_context, defaults)
    
    def _parse_bool(self, s, default_value, complain_wrong_type):
        """ Parses a bool value from a given string
        
        Args:
            s (str): String to be parsed
            default_value (bool): Default value, if the string can't be parsed
            complain_wrong_type (bool): Raise error when given value is of wrong type
        
        Returns:
            bool.  Parsed bool value
            
        Raises:
            TypeError: If the string can't be parsed
            
        """
        bool_true = ['true', '1', 't', 'y', 'yes']
        bool_false = ['false', '0', 'f', 'n', 'no']
        
        b = s.strip().lower()
        if b in bool_true:
            return True
        elif b in bool_false:
            return False
        elif complain_wrong_type:
            raise TypeError()
        else:
            return default_value
        
    def _parse_number(self, s, number_type, default_value, complain_wrong_type):
        """ Parses a number from a given string
        
        Args:
            s (str): String to be parsed
            number_type (type): Type of number to be parsed (int, float)
            default_value (bool): Default value, if the string can't be parsed
            complain_wrong_type (bool): Raise error when given value is of wrong type
        
        Returns:
            int or float.  Parsed number
            
        Raises:
            TypeError: If the string can't be parsed
            
        """
        try:
            i = number_type(s.strip())
            return i
        except ValueError:
            if complain_wrong_type:
                raise TypeError()
            else:
                return default_value
    
    def _get_defaults(self, file_context, env_context):
        """ Gets the default values for unset variables and parses the value types for given ones
        
        Args:
            file_context (dict): Contains the default variables
            env_context (dict): Given Variables
        
        Returns:
            dict.  Context out of the 'defaults' definition
            
        """
        # determine complain mode; default is true
        if file_context.has_key("complain_wrong_type"):
            complain_wrong_type = True if not type(file_context["complain_wrong_type"]) == bool else file_context["complain_wrong_type"]
        else:
            complain_wrong_type = True
        
        variation = None
        if file_context.has_key("variation"):
            file_variation = file_context["variation"]
            if type(file_variation) == str:
                vname = file_variation.strip()
                if env_context.has_key(vname):
                    variation = str(env_context[vname])
            elif type(file_variation) == dict:
                keys = file_variation.keys()
                if len(keys) == 1:
                    vname = keys[0]
                    vval = file_variation[keys[0]]
                    if type(vval) != list:
                        raise TypeError(self._format_error("The value of '{0}' must be of type 'list'".format(vname), "Parse 'variation'"))
                    if env_context.has_key(vname):
                        envval = str(env_context[vname]).strip()
                        if envval in vval:
                            variation = envval
                        elif complain_wrong_type:
                            raise TypeError(self._format_error("'{0}' must be one of the following strings: {1}\nGiven string: {2}".format(vname, ", ".join(str(v) for v in vval), envval), "Parse 'variation'"))
                    else:
                        variation = str(vval[0]).strip()
                else:
                    raise TypeError(self._format_error("When using value type 'dict' it must contain only one entry", "Parse 'variation'"))
            else:
                raise TypeError(self._format_error("Value of 'variation' must be of type 'str' or 'dict'", "Parse 'variation'"))
        
        processed_defaults = self._get_defaults_variation(file_context, env_context, None, complain_wrong_type)
        if variation is not None:
            processed_defaults = merge_dicts(processed_defaults, 
                                             self._get_defaults_variation(file_context, env_context, variation, complain_wrong_type))
        return processed_defaults
        
    def _get_defaults_variation(self, file_context, env_context, variation, complain_wrong_type):
        """ Gets the default values for unset variables and parses the value types for given ones
        
        Args:
            file_context (dict): Contains the default variables
            env_context (dict): Given Variables
            variation (str): Variation of 'defaults'
            complain_wrong_type (bool): Raise an error if given values does not match the type of the default one  
        
        Returns:
            dict.  Context out of the specific variation of 'defaults'
            
        """
        if variation is None:
            key_name = "defaults"
        else:
            key_name = "defaults_" + variation
            
        if file_context.has_key(key_name):
            processed_defaults_list = []
            
            file_defaults = file_context[key_name]
            input_defaults_list = []
            if type(file_defaults) == list:
                for item in file_defaults:
                    if type(item) == dict and len(item) == 1:
                        input_defaults_list.append((item.keys()[0], item.values()[0]))
                    else:
                        raise TypeError(self._format_error("Entries of '{0}' need be of the type 'dict' and contain only one key".format(key_name), "Getting values from '{0}'".format(key_name)))
            elif type(file_defaults) == dict:
                input_defaults_list = file_defaults.items()
            else:
                raise TypeError(self._format_error("'{0}' must be one of the following types: list, dict".format(key_name), "Getting values from '{0}'".format(key_name)))
            
            for var_name, var_default in input_defaults_list:
                if var_default == None:
                    raise TypeError(self._format_error("Type of '{0}' must not be 'None'".format(var_name), "Getting values from '{0}'".format(key_name)))
                
                if env_context.has_key(var_name):
                    if type(var_default) == str:
                        processed_defaults_list.append([var_name, env_context[var_name]])
                    elif type(var_default) == bool:
                        try:
                            val = self._parse_bool(env_context[var_name], var_default, complain_wrong_type)
                            processed_defaults_list.append([var_name, val])
                        except TypeError:
                            raise TypeError(self._format_error("Type of '{0}' must be 'bool'".format(var_name), "Getting values from '{0}'".format(key_name)))
                    elif type(var_default) == int:
                        try:
                            val = self._parse_number(env_context[var_name], int, var_default, complain_wrong_type)
                            processed_defaults_list.append([var_name, val])
                        except TypeError:
                            raise TypeError(self._format_error("Type of '{0}' must be 'int'".format(var_name), "Getting values from '{0}'".format(key_name)))
                    elif type(var_default) == float:
                        try:
                            val = self._parse_number(env_context[var_name], float, var_default, complain_wrong_type)
                            processed_defaults_list.append([var_name, val])
                        except TypeError:
                            raise TypeError(self._format_error("Type of '{0}' must be 'float'".format(var_name), "Getting values from '{0}'".format(key_name)))
                    elif type(var_default) == list:
                        if len(var_default) == 0:
                            raise TypeError(self._format_error("List of '{0}' must contain at least one entry".format(var_name), "Getting values from '{0}'".format(key_name)))
                        val = env_context[var_name].strip()
                        if val in var_default:
                            processed_defaults_list.append([var_name, val])
                        elif complain_wrong_type:
                            raise TypeError(self._format_error("'{0}' must be one of the following strings: {1}\nGiven string: {2}".format(var_name, ", ".join(str(v) for v in var_default), val), "Getting values from '{0}'".format(key_name)))
                        else:
                            processed_defaults_list.append([var_name, var_default[0]])
                    else:
                        raise TypeError(self._format_error("'{0}' must be one of the following types: str, bool, int, float, list\nGiven type: {1}".format(var_name, type(var_default)), "Getting values from '{0}'".format(key_name)))
                elif type(var_default) == list:
                    processed_defaults_list.append([var_name, var_default[0]])
                else:
                    processed_defaults_list.append([var_name, var_default])
            
            return dict(processed_defaults_list)
        else:
            return None
        
    def _format_error(self, msg, task):
        """ Formats an error for pretty cli output
        
        Args:
            msg (str): The error message
            task (str): Task in which the error occurred 
        
        Returns:
            str.  Formatted error message
            
        """
        return "{0}\n  Context  : Context File\n  Task     : {1}\n  File path: {2}".format(msg, task, self.get_file_path())
