import sys
import os
import importlib

def load_module(fileName, app):
    """
    Load a custom module from a file and execute it within the given application.

    Args:
    - fileName (str): The path to the module file.
    - app: The application object.

    This function imports a custom module from a file, starts it, and executes it within the provided application.

    """
    # Separate the path and the module name from the file name
    aux = fileName.split("/")
    path = '/'
    for i in range(1, len(aux)-1):
        path += aux[i] + '/'
    module_name = aux[-1][:-3]
    # Add the module path to sys.path
    sys.path.append(os.path.realpath('./MODULES/'))
    # Import the module dynamically
    module = importlib.import_module(module_name)
    custom_object = module.pipeline(app)
    try:
        custom_object.start()
    except:
        print('Loaded module must have a callable -> execute() <- function')
