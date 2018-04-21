# Templer - templating with Jinja2

This is a Python 3 module for rendering template files using [Jinja2](http://jinja.pocoo.org/). Sources for variables is the environment and context files.

The documentation of the Jinja2 syntax can be found [here](http://jinja.pocoo.org/docs/dev/templates/).

**Features:**
* templating using Jinja2
* providing variables via environment variables and context files
* using YAML for context files
* easy definition of default values
* dynamic context files (render context files themselves)

**Table of contents**
<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Installation](#installation)
- [Usage](#usage)
	- [Environment Variables](#environment-variables)
	- [Context Files](#context-files)
	- [Templates](#templates)
	- [Examples](#examples)
- [Extra Jinja2 Filters](#extra-jinja2-filters)
- [License](#license)

<!-- /TOC -->

---

## Installation

Install directly from Github:
```
pip install git+https://github.com/Aisbergg/python-templer@v1.1.2
```

Install from PyPi:
```
pip install Templer
```

## Usage

```
usage: templer [-c CONTEXTFILE] [-d] [-r] [-f] [-h] [-i] [-m FILE_MODE] [-t]
               [-v] [--version]
               template [template ...] destination

Render template files with the power of Jinja2

positional arguments:
  template              File to be rendered. Path can be either a file or
                        directory containing multiple files (*.j2)
  destination           Destination for the rendered file(s)

optional arguments:
  -c CONTEXTFILE, --contextfile CONTEXTFILE
                        Context file to be used for rendering. Path can be
                        either a file or directory containing multiple files
                        (*.yml). The option can be used multiple times to
                        specify multiple paths
  -d, --dynamic-contextfiles
                        Render the context files like the templates before
                        parsing them
  -r, --remove-templates
                        Delete the templates after rendering
  -f, --force           Overwrite existing files
  -h, --help            Show this help message and exit
  -i, --ignore-undefined-variables
                        Ignore undefined variables
  -m FILE_MODE, --mode FILE_MODE
                        File mode for rendered files
  -t, --defaults-type-check
                        Check if the environment variables match the data type
                        of the defaults specified in a context file
  -v, --verbose         Enable verbose mode (-vv for debug mode)
  --version             Prints the program version and quits

```

There are two sources for variables that are used to render the templates. The first source is the system environment and the second one the context files.

### Environment Variables

When an env is defined like `FOO=BAR` it can be used as `{{ FOO }}` or `{{ env.FOO }}` in the template file.

### Context Files

The intend of the context files is to be the main source for default variables while the environment variables add dynamic to the rendering. Thus the context files can provide a generic default configuration and the environment variables used to customize it.

The context files are written in nice, human-readable YAML. When desired the context files can also be rendered using the environment variables and Jinja2 before parsing them.

Here is an extensive example with all features explained:
```yaml
# Using the YAML syntax the definition of static variables is simple. Following
# lines create three different variables that can be used in the templates like
# `{{ static.var1 }}`.
static:
  var1: "foo"
  var2: 1
  var3: True

# When the option `--dynamic-contextfiles` is supplied, then the context will be
# rendered with Jinja2 using the environment variables before parsing its
# content.
dynamic:
  var4: "{{ VAR4 | default('bar') }}"
  var5: {{ 1.0 if VAR5 == 'True' else 2.0 }}

# A handy shortcut for defining defaults for variables is the `defaults`
# section. `defaults` is a mapping where every key represents a default for a
# variable. The format is simply: `VARIABLE: DEFAULT_VALUE`
# Thus the environment variables will be checked if a variable with the name
# `VARIABLE` is defined and if not it will be declared and set to the value
# `DEFAULT_VALUE`. Templer takes the data type of the `DEFAULT_VALUE` into
# account and tries to parse the given environment variable accordingly.
# When the option `--defaults-type-check` is supplied, a failure in parsing the
# right data type will result in an error and program termination.
defaults:
  # type string
  VAR6: "some string"
  # type bool
  VAR7: False
  # type int
  VAR8: 1
  # type float
  VAR9: 3.0
  # type list (env must be specified in json format like: ["a", "b", "c"])
  VAR10:
    - "foo"
    - "bar"
    - "uff"

  # ----------------------------------------------------------------------------
  # To simplify some more use cases there are a couple of special defaults
  # available:

  # Type: Choice
  # This type checks a user choice against a list of possible choices. If the
  # given choice is not in the list, then an error is thrown. In the following
  # example a given env `VAR11=c` is considered a valid choice. A value like
  # `VAR11=z` is considered invalid and therefore the program will terminate.
  VAR11:
    type: choice           # type of special defaults
    default: b             # default choice
    case_sensitive: False  # optional (default: false)
    strip: True            # optional (default: true)
    choices:               # list of available choices
      - a
      - b
      - c

  # Type: List
  # This type extends the simple 'list' default, so lists don't have to be
  # defined as json list. Instead a delimiter can be defined to split up a
  # string into a list:
  VAR12:
    type: list
    delimiter: ","         # delimiter for splitting the string
    strip: True            # optional (default: true)
    default:               # default list to use
      - a
      - b
      - c

  # Type: Variation
  # This type adds different variations of default values. In the following
  # example there are three variation (`SMALL`, `MEDIUM`, `LARGE`) defined. A
  # variation is used when the related environment variable is defined. So for
  # example if `SMALL=''` is defined then the variables `VAR13: 1` and
  # `VAR14: "a"` will be used.
  SMALL:
    type: variation
    defaults:              # can be same structure as the main `defaults`
      VAR13: 1
      VAR14: "a"
  MEDIUM:
    type: variation
    defaults:
      VAR13: 10
      VAR14: "aaa"
  LARGE:
    type: variation
    defaults:
      VAR13: 100
      VAR14: "aaaaaaaaa"
```

### Templates

The templates are rendered with Jinja2 using the variables defined in the context files and environment. Therefore any Jinja2 specific syntax can be used.

Multiple templates can be rendered at ones by either providing paths to multiple files or a path to a directory which might contain multiple template files. When a path to a directory is supplied then it will be searched for files with the extensions `.j2` or `.jinja2`. Those will be rendered and put under the destination path while the directory structure is preserved.

### Examples

Render a single template file using only the environment variables (`examples/1`):
```bash
NOUN=fool templer -f template.ini.j2 rendered.ini
```

Render multiple templates with the use of a context file (`examples/2`):
```bash
templer -f -c context.yml templates/ rendered/
```

A fully featured example that is described in the [Context File section](#context-files) (`examples/3`):
```bash
VAR4=ui VAR5=True VAR8=3 VAR11=b VAR12="1,2,3" LARGE=0 templer -d -f -c context.yml template.ini.j2 rendered.ini
```

An example that is used in production (`examples/4`):
```bash
export NGINX_TLS_CERT=''
export NGINX_TLS_KEY=''
export PHPMYADMIN_BLOWFISH_SECRET="$( </dev/urandom tr -dc '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%' | head -c40; echo "")"
templer -d -f -t -c vars/ templates/ rendered/
```

The `mandatory` filter in action (`examples/5`):
```bash
templer -d -c context.yml -f template.ini.j2 rendered.ini
```

More real life examples can be found in those [Dockerfiles](https://github.com/Aisbergg/dockerfiles) where *Templer* is used extensively.

## Extra Jinja2 Filters

Filter | Description
--|--
`mandatory(msg)` | If the variable is not defined an error with a message `msg` will be thrown

## License

Templer is released under the LGPL v3 License. See [LICENSE.txt](LICENSE.txt) for more information.
