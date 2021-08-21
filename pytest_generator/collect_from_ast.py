import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Union
from uuid import uuid4


def collect_members(root: Path) -> dict[str, dict[str, list]]:
    data = {}
    for source in root.glob("**/*.py"):
        print("Processing:", source.stem)
        key = ".".join(source.parts[source.parts.index(root.stem) :]).removesuffix(".py")

        tree = ast.parse(source.read_text())
        if not isinstance(tree, ast.Module):
            print("Expected a module.")

        analyzer = Analyzer(name=key)
        analyzer.visit(tree)

        data[key] = analyzer.stats
    return process_data(data)
    # return data


def process_data(data):
    for modulepath, details in data.items():
        for module_ in details.get("module"):
            for class_ in module_["classdef"]:
                class_["name"] = class_["name"][0]
                first_attr = class_["attribute"][0]
                class_["parent"] = first_attr.name[0] + "." + first_attr.attr[0]
                for fn in class_["functiondef"]:
                    pass
            for fn in module_["functiondef"]:
                pass


class Analyzer(ast.NodeVisitor):
    attt = 1

    def __init__(self, name: str):
        self.stats: dict[str, Any] = {}
        self.name: str = name

    def visit(self, node: ast.AST) -> Any:
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.subvisit)
        return visitor(node)

    def add_item(self, key, item):
        if isinstance(item, ast.AST):
            visited_item = self.visit(item)
        else:
            visited_item = item

        try:
            self.stats[key].append(visited_item)
        except KeyError:
            self.stats[key] = [visited_item]

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    self.add_item(field, item)
                continue
            self.add_item(field, value)

    def subvisit(self, node: ast.AST, set_on_stats: bool = True, **kwargs: str):
        """Visit a node's children by creating a new Analyzer instance

        Args:
            node (ast.AST): The root node
            set_on_stats (bool): Should the sub Analyzer's stats be appended to the
                parent's Analyzer?. Defaults to True.
        """

        def _subvisit():
            sub = Analyzer(name=f"{key}_{uuid4()}")
            sub.generic_visit(node)
            for k in kwargs:
                if k in sub.stats:
                    print(f"Did not expect {k} ({sub.stats[k]}) in the sub stats")
                sub.stats[k] = kwargs[k]
            return sub

        key = type(node).__name__.lower()
        subvisitor = _subvisit()
        if set_on_stats:
            try:
                self.stats[key].append(subvisitor.stats)
            except KeyError:
                self.stats[key] = [subvisitor.stats]
        return subvisitor.stats

    # def visit_ClassDef(self, node: ast.ClassDef):
    #     return self.subvisit(node, name=node.name)

    # def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
    #     return self._visit_function(node)

    # def visit_FunctionDef(self, node: ast.FunctionDef):
    #     return self._visit_function(node)

    # def _visit_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> dict[str, Any]:
    #     r = self.subvisit(node.returns, set_on_stats=False)
    #     if node.returns is None:
    #         return_ = None
    #     elif isinstance(node.returns, ast.Constant):
    #         return_ = node.returns.value
    #     elif isinstance(node.returns, ast.Subscript) and isinstance(node.returns.value, ast.Name):
    #         return_ = node.returns.value.id
    #     elif isinstance(node.returns, ast.Name):
    #         return_ = node.returns.id
    #     else:
    #         print("Unexpected node.returns", node.returns)
    #         return_ = node.returns

    #     # self.generic_visit(node)
    #     stats = self.subvisit(node, return_=return_)

    #     return {
    #         "name": node.name,
    #         "args": stats,  # TODO: pass args and only args :)
    #         "return_": return_,
    #     }

    # def visit_arguments(self, node: ast.arguments) -> Any:
    #     stats = self.subvisit(node)
    #     return stats

    # def visit_arg(self, node: ast.arg) -> Any:
    #     stats = self.subvisit(node)
    #     if node.annotation is None:
    #         annotation = None
    #     elif isinstance(node.annotation, ast.Name):
    #         annotation = node.annotation.id
    #     elif isinstance(node.annotation, ast.Attribute):
    #         if isinstance(node.annotation.value, ast.Name):
    #             annotation = f"{node.annotation.value.id}.{node.annotation.attr}"
    #         else:
    #             self.generic_visit(node.annotation)
    #     elif isinstance(node.annotation, ast.Subscript):
    #         self.generic_visit(node)
    #         if isinstance(node.annotation.value, ast.Name):
    #             node.annotation.slice
    #             annotation = f"{node.annotation.value.id}.{node.annotation.attr}"
    #     else:
    #         print("Unknown node annotation")
    #     if "annotation" in stats:
    #         print(f"Did not expect annotation ({stats['annotation']}) in the stats")
    #     stats["annotation"] = annotation
    #     self.stats["arg"].append(stats)

    # def visit_Subscript(self, node: ast.Subscript):
    #     # if isinstance(node.value, ast.Name):
    #     #     name = node.value.id
    #     # elif isinstance(node.value, ast.Attribute):
    #     #     name = node.value.attr
    #     # else:
    #     #     raise TypeError("Expected node to be of type ast.Name")
    #     stats = self.subvisit(node)
    #     self.stats["subscript"].append(stats)
    #     return stats

    # def visit_Attribute(self, node: ast.Attribute) -> Any:
    #     stats = self.subvisit(node)
    #     self.stats["attribute"].append(stats)
    #     return stats

    def visit_Name(self, node: ast.Name) -> Any:
        return node.id
