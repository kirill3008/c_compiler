import enum
from typing import Callable, Optional

from .position_handler import FileAwarePosition


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

    def __init__(self, data: str, src_pos: tuple[str, str], type: TokenType):
        self.data: str = data
        self.src_pos: tuple[str, str] = src_pos
        self.type = type

    def __repr__(self) -> str:
        return f'Token "{self.data}" ({self.type}) at {self.src_pos}'

    def __eq__(self, other):
        if not isinstance(other, RawToken):
            return False
        return (
            self.data == other.data
            and self.src_pos == other.src_pos
            and self.type == other.type
        )


class ExtractTokens():
    def __init__(self, content: str):
        self.content = content
        self.position_handler = FileAwarePosition(content)
        self.position: int = 0

    def extract(self) -> list[RawToken]:
        result: list[RawToken] = []

        extractors: list[Callable[[], tuple[Optional[RawToken], int]]] = [
            self._extract_comment,
            self._extract_number,
            self._extract_char,
            self._extract_string_const,
            self._extract_identifier,
            self._extract_op,
        ]
        while self.position < len(self.content):
            for extract_func in extractors:
                flag = False
                token, self.position = extract_func()
                if token:
                    flag = True
                    result.append(token)
                    break

            if self.content[self.position].strip() and not flag:
                raise self.position_handler.error(
                    'Syntax error at {} (can\'t determen token)',
                    self.position
                )
            self.position += 1
        return result

    def _extract_comment(self) -> tuple[Optional[RawToken], int]:
        if self.content[self.position] == '/':
            if self.position + 1 < len(self.content) and self.content[self.position + 1] == '/':
                position_end = self.position
                while position_end < len(self.content) and self.content[position_end] != '\n':
                    position_end += 1
                # comment up to the end of file
                if position_end == len(self.content):
                    position_end -= 1
                return RawToken(
                    self.content[self.position: position_end + 1],
                    self.position_handler.convert((self.position, position_end)),
                    TokenType.COMMENT
                ), position_end
            if self.position + 1 < len(self.content) and self.content[self.position + 1] == '*':
                position_end = self.position + 2
                while (
                    position_end + 1 < len(self.content)
                    and self.content[position_end:position_end + 2] != "*/"
                ):
                    position_end += 1
                if position_end + 1 >= len(self.content):
                    raise self.position_handler.error(
                        'Multiline comment was never closed {}',
                        self.position
                    )
                return RawToken(
                    self.content[self.position: position_end + 2],
                    self.position_handler.convert((self.position, position_end + 1)),
                    TokenType.COMMENT
                ), position_end + 1
        return None, self.position

    def _extract_number(self) -> tuple[Optional[RawToken], int]:
        # float starting with .
        if self.content[self.position] == '.':
            if self.position + 1 < len(self.content) and self.content[self.position + 1].isdigit():
                position_end = self.position + 1
                while position_end < len(self.content) and self.content[position_end].isdigit():
                    position_end += 1
                return RawToken(
                        self.content[self.position: position_end],
                        self.position_handler.convert((self.position, position_end - 1)),
                        TokenType.FLOAT_CONST
                    ), position_end - 1

        # one of 0b*, 0x*, 0.*, 0*, 0
        if self.content[self.position] == '0':
            # eof means it's plain zero (also is imposible in normal code)
            if self.position + 1 >= len(self.content):
                return RawToken(
                    self.content[self.position],
                    self.position_handler.convert((self.position, self.position)),
                    TokenType.OCT_INT_CONST
                ), self.position
            # binary number
            if self.content[self.position + 1] == 'b':
                position_end = self.position + 2
                if (
                    position_end >= len(self.content)
                    or self.content[position_end] not in ('1', '0')
                ):
                    raise self.position_handler.error('Invelid binary number at {}', self.position)
                while position_end < len(self.content) and self.content[position_end] in ('1', '0'):
                    position_end += 1
                if (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isalnum()
                        or self.content[position_end] in ('_', '.')
                    )
                ):
                    raise self.position_handler.error(
                        'Binary number at {} is followed by invalid symbol',
                        self.position
                    )

                return RawToken(
                    self.content[self.position: position_end],
                    self.position_handler.convert((self.position, position_end - 1)),
                    TokenType.BIN_INT_CONST
                    ), position_end - 1
            # hex number
            if self.content[self.position + 1] == 'x':
                position_end = self.position + 2
                if (
                    position_end >= len(self.content)
                    or not (
                        self.content[position_end].isdigit()
                        or self.content[position_end].lower() in ('a', 'b', 'c', 'd', 'e', 'f')
                    )
                ):
                    raise self.position_handler.error('Invelid hex number at {}', self.position)
                while (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isdigit()
                        or self.content[position_end].lower() in ('a', 'b', 'c', 'd', 'e', 'f')
                    )
                ):
                    position_end += 1
                if (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isalpha()
                        or self.content[position_end] in ('_', '.')
                    )
                ):
                    raise self.position_handler.error(
                        'Hex number at {} is followed by invalid symbol',
                        self.position
                    )
                return RawToken(
                    self.content[self.position: position_end],
                    self.position_handler.convert((self.position, position_end - 1)),
                    TokenType.HEX_INT_CONST
                ), position_end - 1
            # octal number
            if self.content[self.position + 1] in ('0', '1', '2', '3', '4', '5', '6', '7'):
                position_end = self.position + 1
                while position_end < len(self.content) and self.content[position_end] in (
                    '0', '1', '2', '3', '4', '5', '6', '7'
                ):
                    position_end += 1
                if (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isalpha()
                        or self.content[position_end] in ('_')
                    )
                ):
                    raise self.position_handler.error(
                        'Octal number at {} is followed by invalid symbol',
                        self.position
                    )
                # it may be stupid float stating with zero
                if position_end >= len(self.content) or (
                    self.content[position_end] != '.'
                    and not self.content[position_end].isdigit()
                ):
                    return RawToken(
                        self.content[self.position: position_end],
                        self.position_handler.convert((self.position, position_end - 1)),
                        TokenType.OCT_INT_CONST
                        ), position_end - 1

            # try extract float with leading zero
            dot_pos = self.position + 1
            while dot_pos < len(self.content) and self.content[dot_pos].isdigit():
                dot_pos += 1
            if dot_pos < len(self.content) and self.content[dot_pos] == '.':
                # found dot, it's float!
                position_end = dot_pos + 1
                while position_end < len(self.content) and self.content[position_end].isnumeric():
                    position_end += 1
                if (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isalpha()
                        or self.content[position_end] in ('_', '.')
                    )
                ):
                    raise self.position_handler.error(
                        'Float number at {} is followed by invalid symbol',
                        self.position
                    )
                return RawToken(
                    self.content[self.position: position_end],
                    self.position_handler.convert((self.position, position_end - 1)),
                    TokenType.FLOAT_CONST
                ), position_end - 1
            elif dot_pos >= len(self.content) or self.content[dot_pos].isalnum():
                raise self.position_handler.error('Invalid number defenition at {}', self.position)

            # nothing special after, it's plain zero
            return RawToken(
                self.content[self.position],
                self.position_handler.convert((self.position, self.position)),
                TokenType.OCT_INT_CONST
            ), self.position

        # decimal constant
        if self.content[self.position].isdigit():
            position_end = self.position
            while position_end < len(self.content) and self.content[position_end].isdigit():
                position_end += 1
            if position_end < len(self.content) and self.content[position_end] == '.':
                # float
                position_end += 1
                while position_end < len(self.content) and self.content[position_end].isdigit():
                    position_end += 1
                if (
                    position_end < len(self.content)
                    and (
                        self.content[position_end].isalpha()
                        or self.content[position_end] in ('_', '.')
                    )
                ):
                    raise self.position_handler.error(
                        'Float number at {} is followed by invalid symbol',
                        self.position
                    )
                return RawToken(
                    self.content[self.position: position_end],
                    self.position_handler.convert((self.position, position_end - 1)),
                    TokenType.FLOAT_CONST
                ), position_end - 1
            if (
                position_end < len(self.content)
                and (
                    self.content[position_end].isalpha()
                    or self.content[position_end] in ('_', '.')
                )
            ):
                raise self.position_handler.error('Invalid number defenition at {}', self.position)

            return RawToken(
                self.content[self.position: position_end],
                self.position_handler.convert((self.position, position_end - 1)),
                TokenType.DEC_INT_CONST
            ), position_end - 1
        return None, self.position

    def _extract_char(self) -> tuple[Optional[RawToken], int]:
        if self.content[self.position] == '\'':
            if self.position + 2 >= len(self.content) or self.content[self.position + 2] != '\'':
                raise self.position_handler.error(
                    'Invalid char const defenetion at {}',
                    self.position
                )
            return RawToken(
                self.content[self.position: self.position + 3],
                self.position_handler.convert((self.position, self.position + 2)),
                TokenType.CHAR_CONST
            ), self.position + 2
        return None, self.position

    def _extract_string_const(self) -> tuple[Optional[RawToken], int]:
        if self.content[self.position] == '"':
            position_end = self.position + 1
            while position_end < len(self.content) and self.content[position_end] != '"':
                position_end += 1
            if position_end >= len(self.content):
                raise self.position_handler.error('String at {} wath never closed', self.position)
            return RawToken(
                self.content[self.position: position_end + 1],
                self.position_handler.convert((self.position, position_end)),
                TokenType.STRING_CONST
            ), position_end
        return None, self.position

    def _extract_identifier(self) -> tuple[Optional[RawToken], int]:
        if self.content[self.position].isalpha() or self.content[self.position] == '_':
            position_end = self.position
            while (
                position_end < len(self.content)
                and (
                    self.content[position_end].isalnum()
                    or self.content[position_end] == '_'
                )
            ):
                position_end += 1
            return RawToken(
                self.content[self.position: position_end],
                self.position_handler.convert((self.position, position_end - 1)),
                TokenType.IDENTIFIER
            ), position_end - 1
        return None, self.position

    def _extract_op(self) -> tuple[Optional[RawToken], int]:
        if self.content[self.position] in (
            '[', ']', '(', ')', '{', '}',
            '+', '-', '/', '%', '*',
            '*', '&', ',', ';', '=',
            '<', '>', '!', '~'
        ):
            return RawToken(
                self.content[self.position],
                self.position_handler.convert((self.position, self.position)),
                TokenType.OP
            ), self.position
        return None, self.position
