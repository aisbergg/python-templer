from .contextfile import merge_dicts

class Context:
    """ Represents a context creator for a jinja2
    
    Args:
        paths (list): List containing all context files
        environ (dict): Environment variables
        cli_vars (list): Variables passed as command line arguments
        prerender_context (bool): When true render the context form the files
        
    """
    context = dict()
    
    def __init__(self, context_files, environ, cli_vars, prerender_context):
        # parse additional variables
        cli_context = self._parse_cli_context(cli_vars)
        env_context = merge_dicts(environ, cli_context)
        
        for context_file in context_files:
            self.context = merge_dicts(self.context,
                                       context_file.get_context(env_context))
                
        # merge additional context into global context
        self.context = merge_dicts(self.context, {'env': env_context })
    
    def get(self):
        """ Gets the context to be used with jinja2
        
        Returns:
            dict.  All context
            
        """
        return self.context
    
    def _parse_cli_context(self, cli_vars):
        """ Gets variables from command line args
        
        Args:
            cli_vars (list): Variables passed as command line arguments
        
        Returns:
            dict.  Context passed from cli
            
        """
        if len(cli_vars) == 0:
            return dict()
        data = filter(
            lambda l: len(l) == 2 ,(
                map(str.strip, var.split('='))
                for var in cli_vars
            )
        )
        return {item[0] : item[1] for _, item in enumerate(data)}
    