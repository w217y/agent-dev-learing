import ast
import operator

from datetime import datetime

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def _eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _eval_expr(node.left),
            _eval_expr(node.right),
        )
    
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _eval_expr(node.operand)
        )
    
    raise ValueError(f"Unsupported expression")

def calculator(expression: str) -> float:
    tree = ast.parse(expression,mode="eval")
    return _eval_expr(tree.body)

def get_current_time() -> str:
    return datetime.now().isoformat(timespec="seconds")