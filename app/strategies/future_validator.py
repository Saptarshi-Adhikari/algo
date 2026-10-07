"""Future Data Reference Validator module."""
import ast
from typing import Set, List
from app.domain.schemas import StrategySpec, ConditionSpec

class FutureDataReferenceError(ValueError):
    """Raised when an executable StrategySpec contains future-data references (e.g., close(1) or open(2))."""
    pass

APPROVED_LOOKBACK_FUNCTIONS: Set[str] = {"close", "open", "high", "low", "volume"}

class FutureDataReferenceValidator:
    """Inspects StrategySpec expressions to ensure zero future-bar look-ahead leakage."""

    @classmethod
    def validate(cls, spec: StrategySpec) -> None:
        cls.validate_strategy(spec)

    @classmethod
    def validate_strategy(cls, spec: StrategySpec) -> None:
        all_rules: List[ConditionSpec] = spec.rules.entry_rules + spec.rules.exit_rules
        for cond in all_rules:
            cls.validate_expression(cond.left, location=f"Strategy '{spec.strategy_id}' rule left operand '{cond.left}'")
            cls.validate_expression(cond.right, location=f"Strategy '{spec.strategy_id}' rule right operand '{cond.right}'")

    @classmethod
    def validate_expression(cls, expr_str: str, location: str = "Expression") -> None:
        cleaned_expr = expr_str.strip()
        if not cleaned_expr:
            return

        try:
            parsed = ast.parse(cleaned_expr, mode="eval")
        except SyntaxError:
            # If not valid python AST expression (e.g. raw string literal), skip AST walk
            return

        visitor = _FutureDataASTVisitor(location=location)
        visitor.visit(parsed)

class _FutureDataASTVisitor(ast.NodeVisitor):
    def __init__(self, location: str):
        self.location = location

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            fn_name = node.func.id.lower()
            if fn_name in APPROVED_LOOKBACK_FUNCTIONS and len(node.args) == 1:
                arg = node.args[0]
                shift_val = None
                if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, ast.USub) and isinstance(arg.operand, (ast.Constant, ast.Num)):
                    shift_val = -int(getattr(arg.operand, 'value', getattr(arg.operand, 'n', 0)))
                elif isinstance(arg, (ast.Constant, ast.Num)):
                    shift_val = int(getattr(arg, 'value', getattr(arg, 'n', 0)))

                if shift_val is not None and shift_val > 0:
                    raise FutureDataReferenceError(
                        f"FUTURE DATA LEAKAGE DETECTED in {self.location}: '{fn_name}({shift_val})' accesses future bar (shift +{shift_val}). "
                        "Backtesting & Paper Trading require strictly historical data references (shift <= 0)."
                    )
        self.generic_visit(node)
