import types

import jinja2
import yaml
import filters

def _parse_env(data_string):
    """ Parse variables from string in env format

    """
    if len(data_string) == 0:
        return dict()
    data = filter(
        lambda l: len(l) == 2 ,(
            map(str.strip, line.split('='))
            for line in data_string.split("\n")
        )
    )
    return {item[0] : item[1] for _, item in enumerate(data)}
    

class Context:
    """ Represents a context creator for a jinja2
    
    Args:
        paths (list): List containing all context files
        environ (dict): Environment variables
        cli_vars (list): Variables passed as command line arguments
        prerender_context (bool): When true render the context form the files
        
    """
    context = dict()
    
    def __init__(self, paths, environ, cli_vars, prerender_context):
        # parse additional variables
        additional_context = self._get_additional_context(environ, cli_vars)
        self._read_from_files(paths, prerender_context, additional_context)
        
        # merge additional context into global context
        self.context = self._merge_dicts(self.context, additional_context)
    
    def get(self):
        """ Gets the context to be used with jinja2
        
        Returns:
            dict.  All context
            
        """
        return self.context
    
    def _read_from_files(self, paths, prerender, additional_context):
        """ Read context from files
        
        Args:
            paths (list): List of all files to be read in
            prerender_context (bool): When true render the context form the files
            additional_context (dict): Context to be used in the templates
        
        Raises:
            TemplateError: If context file contains invalid syntax
            
        """
        for fpath in paths:
            with open(fpath) as f:
                file_content = f.read()
                if prerender:
                    env = jinja2.Environment(
                        undefined=jinja2.Undefined
                    )
                    # Register additional filters
                    env.filters['required'] = filters.required
                    try:
                        # render file with jinja2
                        file_content = env.from_string(file_content) \
                            .render(additional_context).encode('utf-8')
                    except Exception as e:
                        raise jinja2.exceptions.TemplateError("Error in context file '{0}': {1}".format(fpath, e.message))
                parsed_context = yaml.load(file_content)
                self.context = self._merge_dicts(self.context, parsed_context)
    
    def _get_additional_context(self, environ, cli_vars):
        """ Gets variables from command line args and environment
        
        Args:
            environ (dict): Environment variables
            cli_vars (list): Variables passed as command line arguments
        
        Returns:
            dict.  All additional context
            
        """
        additional_context = {'env': environ }
        cli_vars_string = "\n".join(cli_vars)
        additional_context = self._merge_dicts(additional_context, _parse_env(cli_vars_string))
        return additional_context

    def _merge_dicts(self, x, y):
        """ Recursivly merges two dicts
        
        When keys exist in both the value of 'y' is used. 
        
        Args:
            x (dict): First dict
            y (dict): Second dict
        
        Returns:
            dict.  Merged dict containing values of x and y
            
        """
        # when one of the dicts is empty, than just return the other one
        if type(x) is types.NoneType:
            if type(y) is types.NoneType:
                return dict()
            else:
                return y
        if type(y) is types.NoneType:
            if type(x) is types.NoneType:
                return dict()
            else:
                return x
        
        merged = dict(x,**y)
        xkeys = x.keys()
    
        # update 'branches' of the individual keys 
        for key in xkeys:
            # if this key is a dictionary, recurse                                  
            if type(x[key]) is types.DictType and y.has_key(key):
                merged[key] = self._merge_dicts(x[key],y[key])
        return merged
