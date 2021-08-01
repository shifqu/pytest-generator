import ast
from pathlib import Path
from typing import Any, Union


def collect_members(root: Path) -> dict[str, dict[str, list]]:
    data = {}
    for source in root.glob("**/*.py"):
        print("Processing:", source)
        tree = ast.parse(source.read_text())

        analyzer = Analyzer()
        analyzer.visit(tree)
        # analyzer.report()
        for x in source.parts[::-1]:
            if x == root.stem:
                break
        key = ".".join(source.parts[source.parts.index(root.stem) :]).removesuffix(".py")
        data[key] = analyzer.stats
    return data


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"class": [], "function": [], "async_function": []}
        self.available_modules = {}
        self.key = None

    def visit_ClassDef(self, node: ast.ClassDef):
        if self.key is None:
            class_ = {"name": node.name}
            tmp_visitor = Analyzer()
            tmp_visitor.generic_visit(node)
            new_stats = {k: v for k, v in tmp_visitor.stats.items() if v}
            self.stats["class"].append(dict(**new_stats, **class_))

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.stats["async_function"].append(self._visit_function(node))

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.stats["function"].append(self._visit_function(node))

    def _visit_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> dict[str, Any]:
        if node.returns is None:
            return_ = None
        elif isinstance(node.returns, ast.Constant):
            return_ = node.returns.value
        elif isinstance(node.returns, ast.Subscript) and isinstance(node.returns.value, ast.Name):
            return_ = node.returns.value.id
        elif isinstance(node.returns, ast.Name):
            return_ = node.returns.id
        else:
            raise NotImplementedError("Unexpected node.returns", node.returns)

        return {
            "name": node.name,
            "args": self._visit_arguments(node.args),
            "return_": return_,
        }

    def _visit_arguments(self, node: ast.arguments) -> Any:
        arguments: dict[str, Union[None, str, list]] = {}
        for field in node._fields:
            attr = getattr(node, field)
            if attr is None:
                arguments[field] = None
            elif isinstance(attr, list):
                try:
                    arguments[field] = [arg.arg for arg in attr]
                except AttributeError:
                    """We don't care about defaults for now"""
                    continue
            elif isinstance(attr, ast.arg):
                arguments[field] = attr.arg
        return arguments
