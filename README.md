# Templer - templating with Jinja2

This is a Python module for rendering template files using [Jinja2](http://jinja.pocoo.org/). Variables can be passed as command line arguments or defined in a context file.

Features:
* templating using Jinja2
* context files are written in YAML
* use multiple context files to render multiple templates at ones
* render jinja2 context files themselves before using those to render the templates
* easy definition of default values

This module is widely used in those [Dockerfiles](https://github.com/Aisbergg/dockerfiles)

## Usage

```
usage: templer [-h] [-d] [-f] [-o ROOT_OUTPUT_DIR] [-p] [-v] [--version]
               template context
               [additional_variables [additional_variables ...]]

Create files based on templates and the power of Jinja2.

positional arguments:
  template              Path to 'template file' or dir containing 'template
                        files'
  context               Path to 'context file' or dir containing 'context
                        files'
  additional_variables  Additional variables may be used for templating
                        'context files'

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete-templates-after
                        Delete template files after rendering
  -f, --force           Replace rendered files when they already exist
  -o ROOT_OUTPUT_DIR, --output ROOT_OUTPUT_DIR
                        Output dir; The output will have the same dir
                        structure
  -p, --prerender-context
                        Render the context files itself
  -v, --verbose         Enables output
  --version             Prints the program version and quits
```

## Example

see `example\`

Execute with:
```
templer -p -f example/template.j2 example/context.yml VAR4=ui VAR5=True VAR8=3 VAR10=uff
```
