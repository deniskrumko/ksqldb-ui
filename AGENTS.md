## Build, Test, and Development Commands
After end of each big change run `make check` to validate that project is ok

## Coding Style & Naming Conventions
- Don't ever use `from __future__ import annotations`
- Add docstrings to new classes/function in single-line style without param descriptions. Always in English. If object has multi-line docstring - leave it as is
- Never use `assert` in code except tests (they are located in `src/tests`)
- Don't add `__all__` to `__init__.py` files and only add imports from child modules, no imports from sibling modules
- If module was moved, update `__init__.py` accordingly, remove old imports
- Inline comment must end WITHOUT dot char
