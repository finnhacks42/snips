{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}


{{ cookiecutter.project_short_description }}


Project Structure
-----------------

.. code-block:: raw
   
   project_name
   ├── docs                            <- project documentation
   ├── reference                       <- data dictionaries, manuals and other references
   ├── notebooks                       <- jupyter notebooks
   ├── tests                           <- unit/functional tests for this project                 
   ├── {{cookiecutter.project_slug}}   <- source code for this project
   │   ├── __init__.py                 <- makes this folder a package
   │   ├── cli.py                      <- command line scripts
   │   ├── core.py                     <- core module, these functions are available in the top level namespace
   │   └── submod1.py                  <- an example submodule
   ├── .gitignore                      <- files not to track with git
   ├── README.rst                      <- The top-level README this project.
   ├── requirements.txt                <- The requirements file for reproducing the analysis environment, e.g. generated with `pip freeze > requirements.txt`                   
   ├── setup.cfg                       <- configuration for the project
   └── setup.py                        <- makes project pip installable (pip install -e .)




Features
--------

* TODO