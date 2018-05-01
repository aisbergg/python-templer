import argparse
import os
import sys
import traceback
import jinja2
import yaml
import io

from ast import literal_eval
from templer import __version__
from templer import jinja_filter


def merge_dicts(x, y):
    """ Recursively merges two dicts.

    When keys exist in both the value of 'y' is used.

    Args:
        x (dict): First dict
        y (dict): Second dict

    Returns:
        dict: Merged dict containing values of x and y

    """
    if x is None and y is None:
        return dict()
    if x is None:
        return y
    if y is None:
        return x

    merged = dict(x, **y)
    xkeys = x.keys()

    for key in xkeys:
        if type(x[key]) is dict and key in y:
            merged[key] = merge_dicts(x[key], y[key])
    return merged


class Log(object):
    """ Stupid logger that writes messages to stdout or stderr accordingly"""

    ERROR = 30
    INFO = 20
    DEBUG = 10
    level = ERROR

    @staticmethod
    def debug(msg):
        if Log.level <= 10:
            sys.stdout.write(msg + "\n")

    @staticmethod
    def info(msg):
        if Log.level <= 20:
            sys.stdout.write(msg + "\n")

    @staticmethod
    def error(msg):
        sys.stderr.write(msg + "\n")


class Templer(object):
    """ Render template files using Jinja2.

    Args:


    """

    def __init__(self, templates, destination, variables=dict(), contextfiles=[], file_mode=None, defaults_type_check=False, dynamic_contextfiles=False, remove_templates=False, force_overwrite=False, ignore_undefined_variables=False):
        self.contextfile_paths = contextfiles
        self.file_mode = file_mode
        self.defaults_type_check = defaults_type_check
        self.dynamic_contextfiles = dynamic_contextfiles
        self.remove_templates = remove_templates
        self.force_overwrite = force_overwrite
        self.ignore_undefined_variables = ignore_undefined_variables

        self.template_paths = templates
        if not templates:
            raise ValueError("Templates must be specified")

        self.destination_path = destination
        if not destination or type(destination) is not str:
            raise ValueError("Destination must be specified")

        self.variables = variables
        if type(variables) is not dict:
            raise ValueError("Variables must be of type 'dict'")

        self._create_context()
        self._create_templates()

    def _create_context(self):
        """ Creates the context that is used to render the templates. """
        contextfiles = []
        if self.contextfile_paths:
            for p in self.contextfile_paths:
                if os.path.isdir(p):
                    flist = sorted(self.find_files(p, [".yml", ".yaml"]))
                    for f in flist:
                        contextfiles.append(
                            ContextFile(
                                path=f,
                                defaults_type_check=self.defaults_type_check,
                                dynamic_contextfile=self.dynamic_contextfiles,
                                ignore_undefined_variables=self.ignore_undefined_variables))
                else:
                    contextfiles.append(
                        ContextFile(
                            path=p,
                            defaults_type_check=self.defaults_type_check,
                            dynamic_contextfile=self.dynamic_contextfiles,
                            ignore_undefined_variables=self.ignore_undefined_variables))

            if len(contextfiles) == 0:
                raise IOError(
                    "No context files (*.yml, *.yaml) found in given path(s)")

        self.context = Context(self.variables, contextfiles)

    def _create_templates(self):
        """ Get all template files

        Args:
            path (str): Path to a file or dir
            root_output_dir (str): Root output directory
            delete_after (bool): Delete template files after rendering
            force_replacement (bool): Replace rendered files when they already exist

        Returns:
            list: Template files

        """

        file_extensions = [".j2", ".jinja2"]
        templates = []

        if len(self.template_paths) > 1 or os.path.isdir(self.template_paths[0]):
            if os.path.exists(self.destination_path) and \
                    not os.path.isdir(self.destination_path):
                raise ValueError(
                    "Destination exists and is not a directory. When multiple templates are specified the destination must be a directory")

            for path in self.template_paths:
                path = os.path.abspath(path)
                if os.path.isdir(path):
                    flist = self.find_files(
                        path, file_extensions, relative_paths=True)
                    for frel in flist:
                        fabs = os.path.join(path, frel)
                        dest = os.path.join(
                            self.destination_path, os.path.splitext(frel)[0])
                        templates.append(
                            TemplateFile(
                                src=fabs,
                                dest=dest,
                                file_mode=self.file_mode,
                                remove_template=self.remove_templates,
                                force_overwrite=self.force_overwrite,
                                ignore_undefined_variables=self.ignore_undefined_variables))
                else:
                    if path.endswith(tuple(file_extensions)):
                        filename = os.path.splitext(os.path.basename(path))[0]
                    else:
                        filename = os.path.basename(path)
                    templates.append(
                        TemplateFile(
                            src=path,
                            dest=os.path.join(self.destination_path, filename),
                            file_mode=self.file_mode,
                            remove_template=self.remove_templates,
                            force_overwrite=self.force_overwrite,
                            ignore_undefined_variables=self.ignore_undefined_variables))

        elif len(self.template_paths) == 1:
            if os.path.exists(self.destination_path) and os.path.isdir(self.destination_path):
                dest = os.path.join(self.destination_path,
                                    os.path.basename(self.template_paths[0]))
            else:
                dest = self.destination_path
            templates.append(
                TemplateFile(
                    src=self.template_paths[0],
                    dest=dest,
                    file_mode=self.file_mode,
                    remove_template=self.remove_templates,
                    force_overwrite=self.force_overwrite,
                    ignore_undefined_variables=self.ignore_undefined_variables))

        if len(templates) == 0:
            raise IOError(
                "No template files (*.j2, *.jinja2) found in given path(s)")

        self.templates = templates

    def find_files(self, path, extensions, relative_paths=False):
        """ Recursively find files that match one of the given extensions.

        Args:
            path (str): Search path
            extensions (list): List of file extensions
            relative_paths (boolean): If true the found file paths will be relative to the given path instead of absolute paths

        Returns:
            list: List of files that match one of the given extensions

        """
        path = os.path.abspath(path)
        found_files = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(tuple(extensions)):
                    if relative_paths:
                        found_files.append(os.path.relpath(
                            os.path.join(root, filename), path))
                    else:
                        found_files.append(os.path.join(root, filename))

        return found_files

    def render(self):
        """ Renders all templates """
        for tplf in self.templates:
            tplf.render(self.context.get())


class Context(object):
    """ Represents a context creator for a jinja2

    Args:
        paths (list): List containing all context files
        environ (dict): Environment variables
        cli_vars (list): Variables passed as command line arguments
        prerender_context (bool): When true render the context form the files

    """

    def __init__(self, variables, contextfiles):
        if type(variables) is not dict:
            ValueError("Variables must be of type 'dict'")

        self.context = variables
        for ctxf in contextfiles:
            self.context = merge_dicts(
                self.context, ctxf.get_context(variables))

        # merge additional context into global context
        self.context = merge_dicts(self.context, {'env': variables})

    def get(self):
        """ Gets the context to be used with jinja2

        Returns:
            dict: All context

        """
        return self.context


class SilentUndefined(jinja2.Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''


class ContextFile(object):
    """ Represents a file with a context for jinja2 templates

    Args:
        path (str): Path to file

    """

    def __init__(self, path, defaults_type_check, dynamic_contextfile, ignore_undefined_variables):
        self.path = path
        self.defaults_type_check = defaults_type_check
        self.dynamic_contextfile = dynamic_contextfile
        self.ignore_undefined_variables = ignore_undefined_variables
        if not os.path.exists(path):
            raise IOError(self._format_error("File does not exist"))
        if not os.path.isfile(path):
            raise IOError(self._format_error("Given path is not a file"))

    def get_context(self, variables):
        """ Read the context from a file

        Args:
            prerender_context (bool): When true render the context form the files
            variables (dict): Context to be used to prerender the 'context file'

        Returns:
            dict: Context from the 'context file'

        Raises:
            TemplateError: If jinja2 syntax is invalid
            YAMLError: If YAML syntax is invalid
            TypeError: If wrong types are used in the 'defaults' section

        """
        Log.debug("Loading context file: {0}".format(self.path))
        with io.open(self.path, 'r', encoding='utf8') as f:
            file_content = f.read()

        if self.dynamic_contextfile:
            env = jinja2.Environment(
                undefined=SilentUndefined if self.ignore_undefined_variables else jinja2.StrictUndefined
            )
            # register additional filters
            env.filters = merge_dicts(env.filters, jinja_filter.filters)
            try:
                # render file with jinja2
                Log.debug("Rendering context file...")
                file_content = env.from_string(file_content).render(variables)
            except jinja_filter.MandatoryError as e:
                raise
            except jinja2.UndefinedError as e:
                raise jinja2.exceptions.UndefinedError(
                    self._format_error("Variable {0}".format(str(e.message))))
            except jinja2.TemplateError as e:
                raise jinja2.exceptions.TemplateError(
                    self._format_error("Template error: {0}".format(str(e))))
            except Exception as e:
                raise Exception(self._format_error(
                    "Error: {0}".format(str(e))))

        try:
            Log.debug("Parsing context file...")
            parsed_context = yaml.load(file_content) or dict()
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                raise yaml.YAMLError(self._format_error(
                    "YAML parsing error at line {0} column {1}".format(mark.line + 1, mark.column + 1)))
            else:
                raise yaml.YAMLError(self._format_error(
                    "YAML parsing error: {0}".format(str(e))))
        except Exception as e:
            raise Exception(self._format_error("Error: {0}".format(str(e))))

        defaults = self._get_defaults(parsed_context, variables)
        parsed_context.pop('defaults', None)
        return merge_dicts(parsed_context, defaults)

    def _get_defaults(self, file_context, variables):
        """ Gets the default values for unset variables and parses the value types for given ones

        Args:
            file_context (dict): Contains the default variables
            variables (dict): Given Variables

        Returns:
            dict: Context out of the 'defaults' definition

        """
        Log.debug("Getting default values...")
        if 'defaults' in file_context:
            return self._parse_defaults(file_context['defaults'], variables)

    def _parse_defaults(self, defaults_data, env_context):
        """ Gets the default values for unset variables and parses the value types for given ones

        Args:
            defaults_data (list): Contains the default variables
            env_context (dict): Given Variables
            variation (str): Variation of 'defaults'
            self.defaults_type_check (bool): Raise an error if given values does not match the type of the default one

        Returns:
            dict: Context out of the specific variation of 'defaults'

        """
        if type(defaults_data) is not dict or len(defaults_data) == 0:
            raise TypeError(self._format_error(
                "'defaults' must be of type 'dict' and contain at least one key"))

        default_getter = {
            str: self._get_default_str,
            bool: self._get_default_bool,
            int: self._get_default_number,
            float: self._get_default_number,
            list: self._get_default_list,
            dict: self._get_default_dict,
            type(None): (lambda n, d, e: (_ for _ in ()).throw(TypeError(self._format_error("Variable '{0}' must not be of type 'None'".format(n)))))
        }

        parsed_defaults = dict()
        for var_name, var_default in defaults_data.items():
            val = default_getter[type(var_default)](
                var_name, var_default, env_context)
            # a special default might return a dict -> merge into results
            if type(val) is dict:
                parsed_defaults = merge_dicts(parsed_defaults, val)
            else:
                parsed_defaults[var_name] = val

        return parsed_defaults

    def _get_default_str(self, name, default, variables):
        """ Checks if a variable is defined and converts it to the right type. If the variable is not defined the default value is returned.

        Args:
            name (str): Name of the default variable
            default (str): The default value
            variables (dict): Given variables for lookup

        Returns:
            str: Parsed str value

        """
        if name in variables:
            return variables[name]
        else:
            return default

    def _get_default_bool(self, name, default, variables):
        """ Checks if a variable is defined and converts it to the right type. If the variable is not defined the default value is returned.

        Args:
            name (str): Name of the default variable
            default (bool): The default value
            variables (dict): Given variables for lookup

        Returns:
            bool: Parsed bool value

        Raises:
            TypeError: If the variable cannot be parsed

        """
        if name in variables:
            bool_true = ['true', '1', 't', 'y', 'yes']
            bool_false = ['false', '0', 'f', 'n', 'no']
            b = variables[name].strip().lower()
            if b in bool_true:
                return True
            elif b in bool_false:
                return False
            elif self.defaults_type_check:
                raise TypeError(self._format_error(
                    "Variable '{0}' must be of type 'bool'".format(name)))
            else:
                return variables[name]
        else:
            return default

    def _get_default_number(self, name, default, variables):
        """ Checks if a variable is defined and converts it to the right type. If the variable is not defined the default value is returned.

        Args:
            name (str): Name of the default variable
            default (int or float): The default value
            variables (dict): Given variables for lookup

        Returns:
            int or float: Parsed number

        Raises:
            TypeError: If the variable cannot be parsed

        """
        if name in variables:
            try:
                return type(default)(variables[name].strip())
            except ValueError:
                if self.defaults_type_check:
                    raise TypeError(self._format_error(
                        "Variable '{0}' must be of type '{1}'".format(name, type(default))))
                else:
                    return variables[name]
        else:
            return default

    def _get_default_list(self, name, default, variables):
        """ Checks if a variable is defined and converts it to the right type. If the variable is not defined the default value is returned.

        Args:
            name (str): Name of the default variable
            default (list): The default value
            variables (dict): Given variables for lookup

        Returns:
            list: Parsed list value

        Raises:
            TypeError: If the variable cannot be parsed

        """
        if name in variables:
            try:
                return literal_eval(variables[name].strip())
            except ValueError:
                if self.defaults_type_check:
                    raise TypeError(self._format_error(
                        "Variable '{0}' must be a list in json format".format(name)))
                else:
                    return variables[name]
        else:
            return default

    def _get_default_dict(self, name, options, variables):
        """ Checks if a variable is defined and converts it to the right type. If the variable is not defined the default value is returned.

        Args:
            name (str): Name of the default variable
            options (dict): Options
            variables (dict): Given variables for lookup

        Returns:
            list: Parsed list value

        Raises:
            TypeError: If the variable cannot be parsed

        """
        if not 'type' in options:
            raise ValueError(self._format_error(
                "Variable '{0}': When using a special default the 'type' is required").format(name))

        if options['type'] == 'choice':
            if not 'default' in options:
                raise ValueError(self._format_error(
                    "Variable '{0}': When using 'choice' the 'default' value must be specified").format(name))
            if not 'choices' in options or type(options['choices']) is not list:
                raise ValueError(self._format_error(
                    "Variable '{0}': When using 'choice' a list of 'choices' must be specified").format(name))

            default = options['default']
            choices = options['choices']
            case_sensitive = options['case_sensitive'] if 'case_sensitive' in options else False
            strip = options['strip'] if 'strip' in options else True

            if name in variables:
                choice = variables[name].strip() if strip else variables[name]
                valid_choice = False
                if case_sensitive:
                    if variables[name] in choices:
                        choice = variables[name]
                        valid_choice = True
                else:
                    import unicodedata

                    def normalize_caseless(s): return unicodedata.normalize(
                        "NFKD", s.casefold())

                    def caseless_equal(s1, s2): return normalize_caseless(
                        s1) == normalize_caseless(s2)
                    for c in choices:
                        if caseless_equal(choice, c):
                            choice = c
                            valid_choice = True
                            break

                if not valid_choice:
                    raise ValueError("Variable '{0}': Your choice '{1}' is not available. The available choices are: {2}".format(
                        name, choice, ', '.join(choices)))

                return choice
            else:
                return default

        elif options['type'] == 'list':
            if not 'delimiter' in options:
                raise ValueError(self._format_error(
                    "Variable '{0}': When using 'list' the 'delimiter' must be specified").format(name))
            if not 'default' in options or type(options['default']) is not list:
                raise ValueError(self._format_error(
                    "Variable '{0}': When using 'list' the 'default' must be specified").format(name))

            default = options['default']
            delimiter = options['delimiter']
            strip = options['strip'] if 'strip' in options else True

            if name in variables:
                # split(delimiter) does not necessarily retrun an empty list
                # when the string is empty therefore check string first
                if variables[name] == '':
                    return []
                elif strip:
                    return list(map((lambda s: s.strip()), variables[name].split(delimiter)))
                else:
                    return variables[name].split(delimiter)
            else:
                return default

        elif options['type'] == 'variation':
            if not 'defaults' in options or type(options['defaults']) is not dict:
                raise ValueError(self._format_error(
                    "Variable '{0}': When using 'variation' the 'defaults' must be specified and be of type 'dict'").format(name))

            if name in variables:
                return self._parse_defaults(options['defaults'], variables)
            else:
                return dict()

        else:
            raise ValueError(self._format_error(
                "Variable '{0}': Unknown special default type '{1}'. Available types are: choice, list, variation").format(name, options['type']))

    def _format_error(self, msg):
        """ Formats an error for pretty cli output

        Args:
            msg (str): The error message

        Returns:
            str: Formatted error message

        """
        return "{0}\n  Scope: Context File\n  Path:  {1}".format(msg, self.path)


class TemplateFile(object):
    """ Represents a template file to be rendered with jinja2

    Args:
        path (str): Path to file
        delete_after (bool): Delete the template files after rendering
        force_replacement (bool): Replace rendered files when they already exist

    """

    def __init__(self, src, dest, file_mode=None, remove_template=False, force_overwrite=False, ignore_undefined_variables=False):
        self.src = src
        self.dest = dest
        self.file_mode = file_mode
        self.remove_template = remove_template
        self.force_overwrite = force_overwrite
        self.ignore_undefined_variables = ignore_undefined_variables

        if not os.path.exists(src):
            raise IOError(self._format_error("File does not exist"))
        if not os.path.isfile(src):
            raise IOError(self._format_error("Path is not a file"))

    def render(self, context):
        """ Renders the template file with jinja2

        Args:
            context (dict): Variables that can be used in the template
            verbose (bool): Whether the program shall print some output or not

        """
        Log.debug("Loading template file: {0}".format(self.src))
        with io.open(self.src, 'r', encoding='utf8') as f:
            file_content = f.read()

        env = jinja2.Environment(
            undefined=SilentUndefined if self.ignore_undefined_variables else jinja2.StrictUndefined
        )

        # Register additional filters
        env.filters = merge_dicts(env.filters, jinja_filter.filters)

        # render file with jinja2
        try:
            Log.debug("Rendering template file...")
            rendered_file_content = env.from_string(
                file_content).render(context) + u'\n'
        except jinja_filter.MandatoryError as e:
            raise
        except jinja2.UndefinedError as e:
            raise jinja2.exceptions.UndefinedError(
                self._format_error("Variable {0}".format(str(e.message))))
        except jinja2.TemplateError as e:
            raise jinja2.exceptions.TemplateError(
                self._format_error("Template error: {0}".format(str(e))))
        except Exception as e:
            raise Exception(self._format_error("Error: {0}".format(str(e))))

        # Write rendered file
        self._write_rendered_file(rendered_file_content)
        Log.info("Created file '{0}' from '{1}'".format(self.dest, self.src))

        if self.remove_template:
            os.remove(self.src)

    def _write_rendered_file(self, content):
        """ Writes the rendered content into the rendered file

        Args:
            content (str): Rendered content

        Raises:
            FileExistsError: If desired output file exists and overwriting is not enforced
            NotAFileError: If output path is not a file
            NotADirectoryError: If output directory for given path is not a directory

        """
        if os.path.exists(self.dest):
            if os.path.isfile(self.dest):
                if not self.force_overwrite:
                    raise IOError(self._format_error(
                        "Destination already exists. Use '-f' flag to overwrite the file".format(self.dest)))
            else:
                raise IOError(self._format_error(
                    "Destination exists and is not a file".format(self.dest)))
        else:
            # create dir
            if os.path.dirname(self.dest):
                os.makedirs(os.path.dirname(self.dest), exist_ok=True)

        # write content to file
        Log.debug("Saving template file to: {0}".format(self.dest))
        with io.open(self.dest, 'w', encoding='utf8') as f:
            f.write(content)

        # set file permissions
        if self.file_mode:
            Log.debug(
                "Setting file mode of the template file...".format(self.dest))
            os.chmod(self.dest, int(self.file_mode, 8))

    def _format_error(self, msg):
        """ Formats an error for pretty cli output

        Args:
            msg (str): The error message

        Returns:
            str: Formatted error message

        """
        return "{0}\n  Scope: Template File\n  Path:  {1}".format(msg, self.src)


def cli():
    """ CLI entry point """
    # parsing arguments
    parser = argparse.ArgumentParser(
        prog='templer',
        description='Render template files with the power of Jinja2',
        add_help=False)
    parser.add_argument('-c', '--contextfile', dest='contextfile', action='append',
                        help="Context file to be used for rendering. Path can be either a file or directory containing multiple files (*.yml). The option can be used multiple times to specify multiple paths")
    parser.add_argument('-d', '--dynamic-contextfiles', dest='dynamic_contextfiles', default=False,
                        action='store_true', help="Render the context files like the templates before parsing them")
    parser.add_argument('-r', '--remove-templates', dest='remove_templates',
                        default=False, action='store_true', help="Delete the templates after rendering")
    parser.add_argument('-f', '--force', dest='force_overwrite',
                        action='store_true', default=False, help="Overwrite existing files")
    parser.add_argument("-h", "--help", action="help",
                        help="Show this help message and exit")
    parser.add_argument('-i', '--ignore-undefined-variables', dest='ignore_undefined_variables',
                        action='store_true', default=False, help="Ignore undefined variables")
    parser.add_argument('-m', '--mode', dest='file_mode',
                        help="File mode for rendered files")
    parser.add_argument('-t', '--defaults-type-check', dest='defaults_type_check', action='store_true', default=False,
                        help="Check if the environment variables match the data type of the defaults specified in a context file")
    parser.add_argument('-v', '--verbose', dest='verbose', action='count',
                        default=0, help="Enable verbose mode (-vv for debug mode)")
    parser.add_argument('--version', action='version', version='Templer {0}, Jinja2 {1}'.format(
        __version__, jinja2.__version__), help="Prints the program version and quits")
    parser.add_argument('template', nargs='+',
                        help="File to be rendered. Path can be either a file or directory containing multiple files (*.j2)")
    parser.add_argument(
        'destination', help="Destination for the rendered file(s)")
    args = parser.parse_args(sys.argv[1:])

    # initialize dumb logger
    levels = [Log.ERROR, Log.INFO, Log.DEBUG]
    Log.level = levels[min(len(levels) - 1, args.verbose)]

    try:
        # execute main logic
        templer = Templer(
            templates=args.template,
            destination=args.destination,
            variables=dict(os.environ),
            contextfiles=args.contextfile,
            file_mode=args.file_mode,
            defaults_type_check=args.defaults_type_check,
            dynamic_contextfiles=args.dynamic_contextfiles,
            remove_templates=args.remove_templates,
            force_overwrite=args.force_overwrite,
            ignore_undefined_variables=args.ignore_undefined_variables)
        templer.render()

    except Exception as e:
        # catch errors and print to stderr
        if args.verbose >= 2:
            Log.error(traceback.format_exc())
        else:
            Log.error(str(e))
        exit(1)

    exit(0)
