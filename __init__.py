import inspect
import os
import pkgutil

class MangaSource:
    source_name = ''
    source_id = ''
    
    def updates(self, count=5):
        raise NotImplementedError

    def top(self, count=5):
        raise NotImplementedError

    def manga(self, iden):
        raise NotImplementedError

    def chapter(self, iden):
        raise NotImplementedError


class SourceCollection(object):
    def __init__(self, source_package):
        self.source_package = source_package
        self.reload_sources()

    def reload_sources(self):
        self.sources = {}
        self.seen_paths = []
        self.walk_package(self.source_package)

    def source(self, source, params):
        if source in self.sources.keys():
            return self.sources[source]
        else:
            #Return some error because source doesnt exist
            return MangaSource

    def walk_package(self, package):
        imported_package = __import__(package, fromlist=['lol'])

        for _, sourcename, ispkg in pkgutil.iter_modules(
                imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                source_module = __import__(sourcename, fromlist=['lol'])
                clsmembers = inspect.getmembers(source_module, inspect.isclass)
                for (_, c) in clsmembers:

                    if issubclass(c, MangaSource) & (c is not MangaSource):
                        self.sources[c.source_id] = c()

        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])

        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                child_pkgs = [
                    p for p in os.listdir(pkg_path)
                    if os.path.isdir(os.path.join(pkg_path, p))
                ]

                for child_pkg in child_pkgs:
                    self.walk_package(package + '.' + child_pkg)