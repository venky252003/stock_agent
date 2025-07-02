import ast
import types
from pathlib import Path


def load_function():
    source = Path('main.py').read_text()
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'markdown_to_pdf_bytes':
            mod = ast.Module(body=[node], type_ignores=[])
            ns = {}
            exec(compile(mod, '<main>', 'exec'), ns)
            return ns['markdown_to_pdf_bytes']
    raise RuntimeError('function not found')


def test_markdown_to_pdf_bytes():
    func = load_function()
    data = func('# Title')
    assert data.startswith(b'%PDF')
