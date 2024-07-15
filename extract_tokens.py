import click
import logging
import enum
from typing import Optional, Callable

from utils import to_str_column
from c_token import Token, Variable, Function
from const import type_names, brackets_dict

logger = logging.getLogger(__name__)


# STATES FOR PARSER
TokenType = enum.Enum(
    'TokenType',
    [
        'IDENTIFIER',
        'OP',
        'COMMENT',
        'FLOAT_CONST',
        'DEC_INT_CONST',
        'HEX_INT_CONST',
        'OCT_INT_CONST',
        'BIN_INT_CONST',
        'STRING_CONST',
        'CHAR_CONST',
    ]
)


class RawToken():
    __slots__ = [
        'data',
        'src_pos',
        'type'
    ]

    def __init__(self, data: str, src_pos: tuple[int, int], type: TokenType):
        self.data: str = data
        self.src_pos: tuple[int, int] = src_pos
        self.type = type
    
    def __repr__(self) -> str:
        return f'Token "{self.data}" ({self.type}) at {self.src_pos} '


def extract_comment(data: str, index: int) -> tuple[
    Optional[tuple[str, tuple[int, int]]],
    Optional[TokenType],
    int
]:
    if data[index] == '/':
        if index + 1 < len(data) and data[index + 1] == '/':
            index_end = index
            while index_end < len(data) and data[index_end] != '\n':
                index_end += 1
            return (data[index: index_end + 1], (index, index_end)), TokenType.COMMENT, index_end
            index = index_end
        if index + 1 < len(data) and data[index + 1] == '*':
            index_end = index + 2
            while index_end + 1 < len(data) and data[index_end:index_end + 2] != "*/":
                index_end += 1
            if index_end >= len(data):
                logger.error('Multiline comment was never closed %s', data[index:])
                return None, None, index
            return (data[index: index_end + 2], (index, index_end)), TokenType.COMMENT, index_end
    return None, None, index


def extract_number(data: str, index: int) -> tuple[
    Optional[tuple[str, tuple[int, int]]],
    Optional[TokenType],
    int
]:
    # float starting with .
    if data[index] == '.':
        if index + 1 < len(data) and data[index + 1].isdigit():
            index_end = index + 1
            while index_end < len(data) and data[index_end].isdigit():
                index_end += 1
            return (
                (data[index: index_end], (index, index_end - 1)),
                TokenType.FLOAT_CONST,
                index_end - 1
            )

    # one of 0b*, 0x*, 0.*, 0*, 0
    if data[index] == '0':
        # eof means it's plain zero (also is imposible in normal code)
        if index + 1 >= len(data):
            return (data[index], (index, index)), TokenType.OCT_INT_CONST, index
        # binary number
        if data[index + 1] == 'b':
            index_end = index + 2
            while index_end < len(data) and data[index_end] in ('1', '0'):
                index_end += 1
            return (
                (data[index: index_end], (index, index_end - 1)),
                TokenType.BIN_INT_CONST,
                index_end - 1
            )
        # hex number
        if data[index + 1] == 'x':
            index_end = index + 2
            while (
                index_end < len(data)
                and (
                    data[index_end].isdigit()
                    or data[index_end].lower() in ('a', 'b', 'c', 'd', 'e', 'f')
                )
            ):
                index_end += 1
            return (
                (data[index: index_end], (index, index_end - 1)),
                TokenType.HEX_INT_CONST,
                index_end - 1
            )
        # octal number
        if data[index + 1] in ('0', '1', '2', '3', '4', '5', '6', '7'):
            index_end = index + 1
            while index_end < len(data) and data[index_end] in (
                '0', '1', '2', '3', '4', '5', '6', '7'
            ):
                index_end += 1
            # it may be stupid float stating with zero
            if index_end >= len(data) or data[index_end] != '.':
                return (
                    (data[index: index_end], (index, index_end - 1)),
                    TokenType.OCT_INT_CONST,
                    index_end - 1
                )

        # try extract float with leading zero
        dot_pos = index + 1
        while data[dot_pos].isdigit():
            dot_pos += 1
        if data[dot_pos] == '.':
            # found dot, it's float!
            index_end = dot_pos + 1
            while index_end < len(data) and data[index_end].isdigit():
                index_end += 1
            return (
                (data[index: index_end], (index, index_end - 1)),
                TokenType.FLOAT_CONST,
                index_end - 1
            )

        # nothing special after, it's plain zero
        return (
            data[index], (index, index)), TokenType.OCT_INT_CONST, index

    # decimal constant
    if data[index].isdigit():
        index_end = index
        while index_end < len(data) and data[index_end].isdigit():
            index_end += 1
        if index_end < len(data) and data[index_end] == '.':
            # float
            index_end += 1
            while index_end < len(data) and data[index_end].isdigit():
                index_end += 1
            return (
                (data[index: index_end], (index, index_end - 1)),
                TokenType.FLOAT_CONST,
                index_end - 1
            )
        return (
            (data[index: index_end], (index, index_end - 1)),
            TokenType.DEC_INT_CONST,
            index_end - 1
        )

    return None, None, index


def extract_char(data: str, index: int) -> tuple[
    Optional[tuple[str, tuple[int, int]]],
    Optional[TokenType],
    int
]:
    if data[index] == '\'':
        if index + 2 >= len(data) or data[index + 2] != '\'':
            return None, None, index
        return (data[index: index + 3], (index, index + 2)), TokenType.CHAR_CONST, index + 2
    return None, None, index


def extract_identifier(data: str, index: int) -> tuple[
    Optional[tuple[str, tuple[int, int]]], Optional[TokenType], int
]:
    if data[index].isalpha() or data[index] == '_':
        index_end = index
        while index_end < len(data) and data[index_end].isalnum() or data[index_end] == '_':
            index_end += 1
        return (
            (data[index: index_end], (index, index_end - 1)),
            TokenType.IDENTIFIER,
            index_end - 1
        )
    return None, None, index


def extract_string_const(
    data: str,
    index: int
) -> tuple[Optional[tuple[str, tuple[int, int]]], Optional[TokenType], int]:
    if data[index] == '"':
        index_end = index + 1
        while index_end < len(data) and data[index_end] != '"':
            index_end += 1
        if index_end >= len(data):
            logger.error('string %s wath never closed', data[index:])
            return None, None, index
        return (data[index: index_end + 1], (index, index_end)), TokenType.STRING_CONST, index_end
    return None, None, index


def extract_op(data: str, index: int) -> tuple[
    Optional[tuple[str, tuple[int, int]]],
    Optional[TokenType],
    int
]:
    if data[index] in (
        '[', ']', '(', ')', '{', '}',
        '+', '-', '/', '%', '*',
        '*', '&', ',', ';', '=',
        '<', '>', '!', '~'
    ):
        return (data[index], (index, index)), TokenType.OP, index
    return None, None, index


# split input text on tokens without classification.
# returns list of tokens with their position in data
def extract_tokens(data: str) -> Optional[list[RawToken]]:
    result: list[RawToken] = []
    index = 0

    extractors: list[Callable[
        [str, int],
        tuple[Optional[tuple[str, tuple[int, int]]], Optional[TokenType], int]
    ]] = [
        extract_comment,
        extract_number,
        extract_char,
        extract_identifier,
        extract_string_const,
        extract_op,
    ]

    while index < len(data):
        for extract_func in extractors:
            flag = False
            token, token_type, index = extract_func(data, index)
            if token and token_type:
                flag = True
                result.append(RawToken(*(*token, token_type)))
                break

        if data[index].strip() and not flag:
            logger.error('Syntax error at %s', to_str_column(data, index))
            return None
        index += 1
    return result


def _get_closing_bracket(tokens: list[RawToken], index: int):
    opening = tokens[index]
    closing_bracket = brackets_dict[tokens[index].data]
    opening_bracket = tokens[index].data
    balance = 1
    index += 1
    while index < len(tokens) and balance != 0:
        if tokens[index].data == closing_bracket:
            balance -= 1
        if tokens[index].data == opening_bracket:
            balance += 1
        index += 1
    if balance != 0:
        raise SyntaxError(f'Bracket at {opening} was never closed')
    return index


# recursive function parsing tokens on the same visibility level
def build_ast(
    tokens: list[RawToken],
    index: int = 0,
    top_level: bool = False,
    state: str = 'NONE',
) -> tuple[list[Token], int]:
    result: list[Token] = []

    # only process content of brackets if part starts with some kind of bracket
    closing_bracket_index = None
    if tokens[index].type == TokenType.OP and tokens[index].data in brackets_dict:
        closing_bracket_index = _get_closing_bracket(tokens, index)
        tokens = tokens[index + 1: closing_bracket_index - 1]
        if len(tokens) == 0:
            return [], closing_bracket_index - 1
        index = 0

    while index < len(tokens):
        # got some kind of defenition (function or variable)
        if tokens[index].type == TokenType.IDENTIFIER and tokens[index].data in type_names:
            type_identifier = [tokens[index]]
            def_begin = index
            index += 1
            while tokens[index].type == TokenType.OP and tokens[index].data == '*':
                type_identifier.append(tokens[index])
                index += 1
            # check that there is identifier after type specifier
            assert tokens[index].type == TokenType.IDENTIFIER
            object_name = tokens[index]
            index += 1
            # function defenition
            if top_level and tokens[index].type == TokenType.OP and tokens[index].data == '(':
                args, index = build_ast(tokens, index, state='FUNCTION_ARGS')
                assert all(isinstance(token, Variable) for token in args)
                index += 1
                if tokens[index].type == TokenType.OP and tokens[index].data == '{':
                    function_body, index = build_ast(tokens, index)
                result.append(Function(
                    src_pos=(tokens[def_begin].src_pos[0], tokens[index].src_pos[1]),
                    return_type=[f.data for f in type_identifier],
                    name=object_name.data,
                    args=args,
                    body=function_body,
                ))
            if (
                not top_level
                and index < len(tokens)
                and tokens[index].type == TokenType.OP
                and tokens[index].data == '('
            ):
                raise SyntaxError('Function defenition not on top level')
            
            if state == 'FUNCTION_ARGS':
                result.append(Variable(
                    src_pos=(tokens[def_begin].src_pos[0], object_name.src_pos[1]),
                    name=object_name.data,
                    var_type=[f.data for f in type_identifier],
                ))
                while index < len(tokens):
                    assert (
                        tokens[index].type == TokenType.OP
                        and tokens[index].data == ','
                    )
                    index += 1
                    assert (
                        tokens[index].type == TokenType.IDENTIFIER
                        and tokens[index].data in type_names
                    )
                    type_identifier = [tokens[index]]
                    def_begin = index
                    index += 1
                    while tokens[index].type == TokenType.OP and tokens[index].data == '*':
                        type_identifier.append(tokens[index])
                        index += 1
                    # check that there is identifier after type specifier
                    assert tokens[index].type == TokenType.IDENTIFIER
                    object_name = tokens[index]
                    result.append(Variable(
                        src_pos=(tokens[def_begin].src_pos[0], object_name.src_pos[1]),
                        name=object_name.data,
                        var_type=[f.data for f in type_identifier],
                    ))
                    index += 1
            # some arg definition in body
            else:
                pass
        index += 1

    if closing_bracket_index is not None:
        return result, closing_bracket_index - 1
    return result, index


@click.command()
@click.argument('input_files', type=click.Path(), nargs=-1)
@click.option(
    '-v',
    '--verbose',
    count=True,
    help='Verbosity level -vv: debug, -v: info, default: error',
)
def main(input_files, verbose):
    if verbose <= 0:
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s %(levelname)s %(message)s'
        )
    elif verbose < 2:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(funcName)s - %(message)s',
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)d - %(message)s',
        )

    for file in input_files:
        with open(file) as f:
            tokens = extract_tokens(f.read())
            if not tokens:
                continue
            tokens, _ = build_ast(
                list(filter(lambda x: x.type != TokenType.COMMENT, tokens)),
                top_level=True
            )
            print(*(tokens if tokens else []), sep='\n')


if __name__ == '__main__':
    main()
