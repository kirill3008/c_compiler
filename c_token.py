import enum
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)


ValType = enum.Enum(
    'ValType',
    [
        'INT',
        'UNSIGNED_INT',
        'CHAR',
        'FLOAT',
        'STRING',
    ]
)


class Token():
    __slots__ = [
        'src_pos',
    ]

    def __init__(self, src_pos: tuple[int, int]):
        self.src_pos = src_pos

    def __eq__(self, other):
        if type(self) is type(other):
            return False
        # may break if new attrs added to other instance
        # should use slots as tokens might be imutable
        for attr in self.__slots__:
            if getattr(self, attr, None) != getattr(other, attr, None):
                return False
        return True

    def __str__(self):
        return (
            f"{type(self).__name__}(\n" + 
            ''.join(
                [
                    '    ' + key + ' = ' + '\n    '.join((
                        ('[\n' if isinstance(getattr(self, key)[0], Token) else '[')
                        +
                        (
                            '\n'.join(
                                map(
                                    lambda x: '    ' + x if isinstance(
                                        getattr(self, key)[0], Token
                                    ) else x,
                                    (',\n' if isinstance(getattr(self, key)[0], Token) else ',')
                                    .join(list(map(str, getattr(self, key)))).split('\n')))
                        )
                        + ('\n]' if isinstance(getattr(self, key)[0], Token) else ']')
                        if isinstance(getattr(self, key), list) and len(getattr(self, key)) > 0
                        else str(getattr(self, key))
                    ).split('\n')) + '\n' for key in self.__slots__]) +
            ')'
        )


class Constant(Token):
    __slots__ = [
        'type',
        'value',
    ]

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
    __slots__ = [
        'name',
        'type',
        'value',
    ]

    def __init__(
        self,
        src_pos: tuple[int, int],
        name: str,
        var_type: list[str],
        value: Optional[Token] = None,
    ):
        super().__init__(src_pos)
        self.name = name
        self.type = var_type
        self.value = value


class Function(Token):
    __slots__ = [
        'name',
        'args',
        'body',
        'return_type',
    ]

    def __init__(
        self,
        src_pos: tuple[int, int],
        return_type: list[str],
        name: str,
        args: list[Variable],
        body: list[Token],
    ):
        super().__init__(src_pos)
        self.return_type = return_type
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
    __slots__ = [
        'arity',
        'type',
        'args',
    ]

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
    __slots__ = [
        'condition',
        'body',
    ]

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
    __slots__ = [
        'condition',
        'body',
    ]

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
    __slots__ = [
        'init',
        'condition',
        'increment',
        'body',
    ]

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
