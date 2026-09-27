"""Fail CI if a private case route loses authentication or ownership checks."""
import ast
from pathlib import Path

ROUTE_FILES = (Path("app/legacy_main.py"), Path("app/main.py"))
AUTH_DEPENDENCIES = {"current_user", "require_paid", "require_admin"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def _private_case_routes(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            target = decorator.func
            if not (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "app"
                and target.attr in HTTP_METHODS
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
                and isinstance(decorator.args[0].value, str)
                and decorator.args[0].value.startswith("/cases")
            ):
                continue
            yield decorator.args[0].value, node


def _dependency_names(node):
    defaults = list(node.args.defaults)
    defaults.extend(value for value in node.args.kw_defaults if value is not None)
    names = set()
    for default in defaults:
        if not (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id == "Depends"
            and default.args
        ):
            continue
        dependency = default.args[0]
        if isinstance(dependency, ast.Name):
            names.add(dependency.id)
    return names


def _calls_owned_case(node):
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == "owned_case"
        for child in ast.walk(node)
    )


def test_every_private_case_route_requires_authentication_and_ownership():
    discovered = []
    missing_auth = []
    missing_ownership = []

    for path in ROUTE_FILES:
        for route, node in _private_case_routes(path):
            label = f"{path}:{node.lineno} {route}"
            discovered.append(label)
            if not (_dependency_names(node) & AUTH_DEPENDENCIES):
                missing_auth.append(label)
            if "{case_id}" in route and not _calls_owned_case(node):
                missing_ownership.append(label)

    assert discovered, "No private case routes were discovered; update this guard if routing moved."
    assert not missing_auth, "Private case routes missing authentication:\n" + "\n".join(missing_auth)
    assert not missing_ownership, "Case-scoped routes missing owned_case enforcement:\n" + "\n".join(missing_ownership)
