import enum
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)


VarType = enum.Enum(
    'VarType',
    [
        'INT',
        'UNSIGNED_INT',
        'CHAR',
        'FLOAT',
        'POINTER',
    ]
)

ValType = enum.Enum(
    'ValType',
    [
        'INT',
        'UNSIGNED_INT',
        'CHAR',
        'FLOAT',
    ]
)


class Token():
    def __init__(self, src_pos: tuple[int, int]):
        self.src_pos = src_pos


class Constant(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        val_type: ValType,
        value: Union[int, float, str],
    ):
        super().__init__(src_pos)
        self.type = val_type
        self.value = value


class Variable(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        name: str,
        var_type: VarType,
        value: Optional[Constant] = None,
    ):
        super().__init__(src_pos)
        self.name = name
        self.type = var_type
        self.value = value


class Function(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        name: str,
        args: list[Variable],
        body: list[Token],
    ):
        super().__init__(src_pos)
        self.name = name
        self.args = args
        self.body = body


OpArity = enum.Enum('OpArity', ['Unary', 'Binary'])

OpType = enum.Enum(
    'OpType',
    [
        'MUL',
        'DIV',
        'ADD',
        'SUB',
        'UNARY_SUB',
        'REF',
        'DEREF',
        'ARRAY_ACC'
    ]
)


class Operator(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        arity: OpArity,
        op_type: OpType,
        args: Union[tuple[Token, Token], Token],
    ):
        super().__init__(src_pos)
        self.arity = arity
        self.type = op_type

        if self.arity == OpArity.Unary:
            assert isinstance(args, Token)
        if self.arity == OpArity.Binary:
            assert isinstance(args, tuple)
        self.args = args


class Condition(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        condition: Token,
        body: list[Token],
    ):
        super().__init__(src_pos)
        self.condition = condition
        self.body = body


class WhileLoop(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        condition: Token,
        body: list[Token],
    ):
        super().__init__(src_pos)
        self.condition = condition
        self.body = body


class ForLoop(Token):
    def __init__(
        self,
        src_pos: tuple[int, int],
        init: Token,
        condition: Token,
        increment: Token,
        body: list[Token],
    ):
        super().__init__(src_pos)
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body
