import imp
import os
import sys

<<<<<<< HEAD
def module_has_submodule(mod, submod_name):
    # If the module was loaded from an egg, __loader__ will be set and
    # its find_module must be used to search for submodules.
    loader = getattr(mod, '__loader__', None)
    if loader:
        mod_path = "%s.%s" % (mod.__name__.rsplit('.',1)[-1], submod_name)
        x = loader.find_module(mod_path)
        if x is None:
            # zipimport.zipimporter.find_module is documented to take
            # dotted paths but in fact through Python 2.7 is observed
            # to require os.sep in place of dots...so try using os.sep
            # if the dotted path version failed to find the requested
            # submodule.
            x = loader.find_module(mod_path.replace('.', os.sep))
        return x is not None
=======
>>>>>>> 94f8e324c64a21bb127aba4ca2e481b380e750e2

def module_has_submodule(package, module_name):
    """See if 'module' is in 'package'."""
    name = ".".join([package.__name__, module_name])
    if name in sys.modules:
        return True
    for finder in sys.meta_path:
        if finder.find_module(name):
            return True
    for entry in package.__path__:  # No __path__, then not a package.
        try:
            # Try the cached finder.
            finder = sys.path_importer_cache[entry]
            if finder is None:
                # Implicit import machinery should be used.
                try:
                    file_, _, _ = imp.find_module(module_name, [entry])
                    if file_:
                        file_.close()
                    return True
                except ImportError:
                    continue
            # Else see if the finder knows of a loader.
            elif finder.find_module(name):
                return True
            else:
                continue
        except KeyError:
            # No cached finder, so try and make one.
            for hook in sys.path_hooks:
                try:
                    finder = hook(entry)
                    # XXX Could cache in sys.path_importer_cache
                    if finder.find_module(name):
                        return True
                    else:
                        # Once a finder is found, stop the search.
                        break
                except ImportError:
                    # Continue the search for a finder.
                    continue
            else:
                # No finder found.
                # Try the implicit import machinery if searching a directory.
                if os.path.isdir(entry):
                    try:
                        file_, _, _ = imp.find_module(module_name, [entry])
                        if file_:
                            file_.close()
                        return True
                    except ImportError:
                        pass
                # XXX Could insert None or NullImporter
    else:
        # Exhausted the search, so the module cannot be found.
        return False
