import os
import jinja2

import filters

from exceptions import FileExistsError, NotAFileError, NotADirectoryError

        
class TemplateFile:
    """ Represents a template file to be rendered with jinja2
    
    Args:
        path (list): List containing all context files
        delete_after (bool): Delete the template files after rendering
        force_replacement (bool): Replace rendered files when they already exist
    
    """
    _path = ""
    _output_dir = ""
    _name = ""
    _delete_after = False
    _force_replacement = False
    
    def __init__(self, path, output_dir, delete_after=False, force_replacement=False):
        if not os.path.isfile(path):
            print path
            raise jinja2.TemplateNotFound(path)
        self._path = os.path.dirname(path)
        self._output_dir = output_dir
        self._name = os.path.basename(path)
        self._delete_after = delete_after
        self._force_replacement = force_replacement

    def get_rendered_file_path(self):
        """ Gets the absolute path of the rendered file
        
        Returns:
            str.  Absolute path to rendered file
            
        """
        if self._output_dir is not None:
            return os.path.join(self._output_dir, os.path.splitext(self._name)[0])
        else:
            return os.path.join(self._path, os.path.splitext(self._name)[0])
    
    def get_file_path(self):
        """ Gets the absolute path of the template file
        
        Returns:
            str.  Absolute path to template file
            
        """
        return os.path.join(self._path, self._name)

    def render(self, context, verbose):
        """ Renders the template file with jinja2
        
        Args:
            context (dict): Variables that can be used in the template
            verbose (bool): Whether the program shall print some output or not
        
        """
        env = jinja2.Environment(
            undefined=jinja2.Undefined
        )
    
        # Register additional filters
        env.filters['required'] = filters.required
        
        # render file with jinja2
        try:
            file_content = env.from_string(self._read_template_file()).render(context).encode('utf-8')
        except Exception as e:
            raise jinja2.exceptions.TemplateError("Error in template file '{0}': {1}".format(self.get_file_path(), e.message))
        
        # Write rendered file
        self._write_rendered_file(file_content)
        if verbose:
            print("Rendered template file: {0}".format(self.get_rendered_file_path()))
        
        if self._delete_after:
            os.remove(self.get_file_path())
        
    def _read_template_file(self):
        """ Reads the content of the template file
        
        Returns:
            str.  Content of the template file
        
        """
        with open(self.get_file_path(), 'r') as f:
            return f.read().decode('utf-8')
        
    def _get_template_file_permission_mask(self):
        """ Gets the permission mask of the template file
        
        Returns:
            int.  Permission mask of the template as octal
        
        """
        #return int(oct(os.stat(self.get_file_path()).st_mode & 0777))
        return os.stat(self.get_file_path()).st_mode
        
    def _write_rendered_file(self, content):
        """ Writes the rendered content into the rendered file
        
        Args:
            content (str): Rendered content
            
        Raises:
            FileExistsError: If desired output file exists and overwriting is not enforced
            NotAFileError: If output path is not a file
            NotADirectoryError: If output directory for given path is not a directory 
        
        """
        rendered_file_path = self.get_rendered_file_path()
        rendered_file_dir_path = os.path.dirname(self.get_rendered_file_path())
        if os.path.exists(rendered_file_path):
            if os.path.isfile(rendered_file_path):
                if not self._force_replacement:
                    raise FileExistsError(self.get_rendered_file_path())
            else:
                raise NotAFileError(self.get_rendered_file_path())
        elif os.path.exists(rendered_file_dir_path):
            if not os.path.isdir(rendered_file_dir_path):
                raise NotADirectoryError(self.get_rendered_file_path())
        else: 
            os.makedirs(rendered_file_dir_path, 0755)
        
        with open(rendered_file_path, 'w') as f:
            f.write(content)
        
        # set the file permission the same as the template file
        permisson_mask = self._get_template_file_permission_mask()
        os.chmod(rendered_file_path, permisson_mask)

