import argparse
import os
import sys

from jinja2 import __version__ as jinja2_version
from . import __version__
from .exceptions import NotADirectoryError, FileNotFoundError
from .templatefile import TemplateFile
from .context import Context 


def create_file_list(path, *extensions):
    """ Create a list of files found in the specified path
    
    Args:
        path (str): Path to search for files
        *extensions (str): Find files based on file endings
    
    Returns:
        list.  Files that match the given extensions
        
    """
    if not os.path.exists(path):
        return ([], [])
        
    if os.path.isfile(path):
        return ([os.path.abspath(path)], [os.path.basename(path)])
    elif os.path.isdir(path):
        create_file_list._matching_files = []
        create_file_list._matching_files_relative_path = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(tuple(extensions)):
                    create_file_list._matching_files.append(os.path.join(root, filename))
                    create_file_list._matching_files_relative_path \
                        .append(os.path.relpath(os.path.join(root, filename), path))
        return (create_file_list._matching_files, create_file_list._matching_files_relative_path)


def _get_template_files(path, root_output_dir, delete_after, force_replacement):
    """ Get all template files
    
    Args:
        path (str): Path to a file or dir
        root_output_dir (str): Root output directory
        delete_after (bool): Delete template files after rendering
        force_replacement (bool): Replace rendered files when they already exist
    
    Returns:
        list.  Template files
        
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            abs_paths,rel_paths = ([os.path.abspath(path)], [os.path.basename(path)])
        else:
            abs_paths,rel_paths = create_file_list(path, ".j2")
            if len(abs_paths) == 0:
                raise FileNotFoundError("No Template files (.j2) found in search path '{0}'".format(path))
    else:
        raise FileNotFoundError("Template file: {0}".format(path))
    
    template_files = []
    for i in range(0, len(abs_paths)):
        if root_output_dir is not None:
            output_dir = os.path.dirname(os.path.join(root_output_dir,rel_paths[i]))
        else:
            output_dir = None
        template_files.append(TemplateFile(abs_paths[i], output_dir, delete_after, force_replacement))
    
    return template_files


def _get_context(path, environ, cli_vars, prerender_context):
    """ Get context from files, command line input and environment
    
    Args:
        path (str): Path to a file or dir
        environ (dict): Environment variables
        cli_vars (list): Variables passed as command line arguments
        prerender_context (bool): When true render the context files itself
    
    Returns:
        dict.  The jinja2 context
        
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            flist = [os.path.abspath(path)]
        else:
            flist,_ = create_file_list(path, ".yml", ".yaml")
            if len(flist) == 0:
                raise FileNotFoundError("No Context files (.yml, .yaml) found in search path '{0}'".format(path))
    else:
        raise FileNotFoundError("Context file: {0}".format(path))
    
    context = Context(flist, environ, cli_vars, prerender_context)
    return context.get()


def render_templates(environ, cwd, argv):
    """ Render all templates
    
    Args:
        environ (dict): Environment variables
        cwd (str): Current working directory
        argv (list): Command line arguments
        
    """
    parser = argparse.ArgumentParser(
        prog='templer',
        description='Create files based on templates and the power of Jinja2.',
        epilog=''
    )
    parser.add_argument('-d', '--delete-templates-after', action='store_true', 
                        dest='delete_after', default=False, 
                        help='Delete template files after rendering')
    parser.add_argument('-f', '--force', action='store_true', 
                        dest='force_replacement', default=False, 
                        help='Replace rendered files when they already exist')
    parser.add_argument('-o', '--output', dest='root_output_dir', default=None, 
                        help='Output dir; The output will have the same dir structure')
    parser.add_argument('-p', '--prerender-context', action='store_true', 
                        dest='prerender_context', default=False, 
                        help='Render the context files itself')
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose', default=False, 
                        help='Enables output')
    parser.add_argument('--version', action='version',
                        version='templer {}, Jinja2 {}'.format(__version__, jinja2_version), 
                        help='Prints the program version and quits')
    parser.add_argument('template', help='Path to \'template file\' or dir containing \'template files\'')
    parser.add_argument('context', help='Path to \'context file\' or dir containing \'context files\'')
    parser.add_argument('additional_variables', nargs='*', help='Additional variables may be used for templating \'context files\'')
    args = parser.parse_args(argv)
    
    if args.root_output_dir is None:
        root_output_dir = None
    else:
        if os.path.isabs(args.root_output_dir):
            root_output_dir = args.root_output_dir
        else:
            root_output_dir = os.path.join(cwd, args.root_output_dir)
        if os.path.exists(root_output_dir) and not os.path.isdir(root_output_dir):
            raise NotADirectoryError(root_output_dir)
    
    # Get context
    context = _get_context(args.context, environ, args.additional_variables, args.prerender_context)
    
    # Get template files
    template_files = _get_template_files(args.template, root_output_dir, args.delete_after, args.force_replacement)
    
    # Render templates
    for template_file in template_files:
        template_file.render(context, args.verbose)
    
    
def main():
    """ CLI Entry point 
    
    """
    try:
        render_templates(
            os.environ,
            os.getcwd(),
            sys.argv[1:]
        )
        exit(0)
    except Exception as e:
        sys.stderr.write(e.message + "\n")
        exit(1)
