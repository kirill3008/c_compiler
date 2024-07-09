import click
import logging
import enum
from typing import Optional

from utils import to_str_column

logger = logging.getLogger(__name__)


# STATES FOR PARSER
TokenType = enum.Enum(
    'TokenType',
    [
        'IDENTIFIER',
        'OP',
        'COMMENT',
        'CONST'
    ]
)


def extract_comment(data: str, index: int) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    if data[index] == '/':
        if index + 1 < len(data) and data[index + 1] == '/':
            index_end = index
            while index_end < len(data) and data[index_end] != '\n':
                index_end += 1
            return (data[index: index_end + 1], (index, index_end)), index_end
            index = index_end
        if index + 1 < len(data) and data[index + 1] == '*':
            index_end = index + 2
            while index_end + 1 < len(data) and data[index_end:index_end + 2] != "*/":
                index_end += 1
            if index_end >= len(data):
                logger.error('Multiline comment was never closed %s', data[index:])
                return None, index
            return (data[index: index_end + 2], (index, index_end)), index_end
    return None, index


def extract_number(data: str, index: int) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    # float starting with .
    if data[index] == '.':
        if index + 1 < len(data) and data[index + 1].isdigit():
            index_end = index + 1
            while index_end < len(data) and data[index_end].isdigit():
                index_end += 1
            return (data[index: index_end], (index, index_end - 1)), index_end - 1

    # one of 0b*, 0x*, 0.*, 0*, 0
    if data[index] == '0':
        # eof means it's plain zero (also is imposible in normal code)
        if index + 1 >= len(data):
            return (data[index], (index, index)), index
        # binary number
        if data[index + 1] == 'b':
            index_end = index + 2
            while index_end < len(data) and data[index_end] in ('1', '0'):
                index_end += 1
            return (data[index: index_end], (index, index_end - 1)), index_end - 1
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
            return (data[index: index_end], (index, index_end - 1)), index_end - 1
        # octal number
        if data[index + 1] in ('0', '1', '2', '3', '4', '5', '6', '7'):
            index_end = index + 1
            while index_end < len(data) and data[index_end] in (
                '0', '1', '2', '3', '4', '5', '6', '7'
            ):
                index_end += 1
            # it may be stupid float stating with zero
            if index_end >= len(data) or data[index_end] != '.':
                return (data[index: index_end], (index, index_end - 1)), index_end - 1

        # try extract float with leading zero
        dot_pos = index + 1
        while data[dot_pos].isdigit():
            dot_pos += 1
        if data[dot_pos] == '.':
            # found do, it float!
            index_end = dot_pos + 1
            while index_end < len(data) and data[index_end].isdigit():
                index_end += 1
            return (data[index: index_end], (index, index_end - 1)), index_end - 1

        # nothing special after, it's plain zero
        return (data[index], (index, index)), index

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
            return (data[index: index_end], (index, index_end - 1)), index_end - 1
        return (data[index: index_end], (index, index_end - 1)), index_end - 1

    return None, index


def extract_char(data: str, index: int) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    if data[index] == '\'':
        if index + 2 >= len(data) or data[index + 2] != '\'':
            return None, index
        return (data[index: index + 3], (index, index + 2)), index + 2
    return None, index


def extract_identifier(data: str, index: int) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    if data[index].isalpha() or data[index] == '_':
        index_end = index
        while index_end < len(data) and data[index_end].isalnum() or data[index_end] == '_':
            index_end += 1
        return (data[index: index_end], (index, index_end - 1)), index_end - 1
    return None, index


def extract_string_const(
    data: str,
    index: int
) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    if data[index] == '"':
        index_end = index + 1
        while index_end < len(data) and data[index_end] != '"':
            index_end += 1
        if index_end >= len(data):
            logger.error('string %s wath never closed', data[index:])
            return None, index
        return (data[index: index_end + 1], (index, index_end)), index_end
    return None, index


def extract_op(data: str, index: int) -> tuple[Optional[tuple[str, tuple[int, int]]], int]:
    if data[index] in (
        '[', ']', '(', ')', '{', '}',
        '+', '-', '/', '%', '*',
        '*', '&', ',', ';'
    ):
        return (data[index], (index, index)), index
    return None, index


# split input text on tokens without classification.
# returns list of tokens with their position in data
def extract_tokens(data: str) -> Optional[list[tuple[str, tuple[int, int], TokenType]]]:
    result = []
    index = 0
    while index < len(data):
        flag = False
        token, index = extract_comment(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.COMMENT))

        token, index = extract_number(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.CONST))

        token, index = extract_char(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.CONST))

        token, index = extract_identifier(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.IDENTIFIER))

        token, index = extract_string_const(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.CONST))

        token, index = extract_op(data, index)
        if token:
            flag = True
            result.append((*token, TokenType.OP))

        if data[index].strip() and not flag:
            logger.error('Syntax error at %s', to_str_column(data, index))
            return None
        index += 1
    return result


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
            print(*(tokens if tokens else []), sep='\n')


if __name__ == '__main__':
    main()
