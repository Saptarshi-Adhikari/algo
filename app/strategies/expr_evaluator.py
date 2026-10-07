"""Safe AST Expression Evaluator for Strategy Evaluator."""
import ast
import pandas as pd
from typing import Callable, Any, Dict, Set

APPROVED_FUNCTIONS: Set[str] = {"close", "open", "high", "low", "volume"}

class SafeExpressionEvaluator(ast.NodeVisitor):
    """Safely parses and evaluates mathematical expression ASTs over pandas Series."""

    def __init__(self, df: pd.DataFrame, resolver_cb: Callable[[str, pd.DataFrame], pd.Series]):
        self.df = df
        self.resolver_cb = resolver_cb

    def evaluate(self, expr_str: str) -> pd.Series:
        cleaned_expr = expr_str.strip()
        if not cleaned_expr:
            raise ValueError("Empty expression string.")

        try:
            parsed = ast.parse(cleaned_expr, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax '{expr_str}': {e}")

        return self.visit(parsed.body)

    def visit_Constant(self, node: ast.Constant) -> pd.Series:
        if isinstance(node.value, (int, float)):
            return pd.Series(float(node.value), index=self.df.index)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    def visit_Num(self, node: ast.Num) -> pd.Series:  # Python 3.7 fallback
        return pd.Series(float(node.n), index=self.df.index)

    def visit_Name(self, node: ast.Name) -> pd.Series:
        name_id = node.id
        return self.resolver_cb(name_id, self.df)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> pd.Series:
        operand_ser = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand_ser
        elif isinstance(node.op, ast.USub):
            return -operand_ser
        raise ValueError(f"Unsupported unary operator: {type(node.op)}")

    def visit_BinOp(self, node: ast.BinOp) -> pd.Series:
        left_ser = self.visit(node.left)
        right_ser = self.visit(node.right)

        if isinstance(node.op, ast.Add):
            return left_ser + right_ser
        elif isinstance(node.op, ast.Sub):
            return left_ser - right_ser
        elif isinstance(node.op, ast.Mult):
            return left_ser * right_ser
        elif isinstance(node.op, ast.Div):
            res = left_ser / right_ser
            res = res.replace([float('inf'), float('-inf')], 0.0).fillna(0.0)
            return res
        raise ValueError(f"Unsupported binary operator: {type(node.op)}")

    def visit_Call(self, node: ast.Call) -> pd.Series:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Arbitrary function calls are not allowed.")

        fn_name = node.func.id.lower()
        if fn_name not in APPROVED_FUNCTIONS and fn_name not in ["rsi", "atr", "sma", "ema"]:
            raise ValueError(f"Unapproved function call '{fn_name}'.")

        # Evaluate arguments
        if not node.args:
            target_ser = self.resolver_cb(fn_name, self.df)
            return target_ser

        if len(node.args) == 1:
            arg_node = node.args[0]
            # Handle shift value (e.g. close(-1) or close(1))
            if isinstance(arg_node, ast.UnaryOp) and isinstance(arg_node.op, ast.USub) and isinstance(arg_node.operand, (ast.Constant, ast.Num)):
                shift_val = -int(getattr(arg_node.operand, 'value', getattr(arg_node.operand, 'n', 0)))
            elif isinstance(arg_node, (ast.Constant, ast.Num)):
                shift_val = int(getattr(arg_node, 'value', getattr(arg_node, 'n', 0)))
            else:
                # Nested argument resolution e.g. volume(sma_20)
                sub_name = ast.unparse(arg_node) if hasattr(ast, "unparse") else fn_name
                return self.resolver_cb(f"{fn_name}({sub_name})", self.df)

            base_ser = self.resolver_cb(fn_name, self.df)
            # Standard pandas shift semantics:
            # close(-1) -> previous bar (bar - 1) -> pd.Series.shift(1)
            # close(1) -> next bar (bar + 1) -> pd.Series.shift(-1)
            actual_shift = -shift_val
            return base_ser.shift(actual_shift)

        raise ValueError(f"Function '{fn_name}' expects at most 1 argument.")

    def generic_visit(self, node: ast.AST):
        raise ValueError(f"Forbidden AST node type '{type(node).__name__}' in expression.")
