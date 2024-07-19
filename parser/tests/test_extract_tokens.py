import pytest

from ..extract_tokens import ExtractTokens, RawToken, TokenType


def test_extract_sigleline_comment():
    extractor = ExtractTokens('// test_comment')
    assert (
        extractor._extract_comment() == (
            RawToken('// test_comment', ('1:1', '1:15'), TokenType.COMMENT),
            14
        )
    )
    extractor = ExtractTokens('// test_comment\n')
    assert (
        extractor._extract_comment() == (
            RawToken('// test_comment\n', ('1:1', '1:16'), TokenType.COMMENT),
            15
        )
    )
    extractor = ExtractTokens('/\n')
    assert extractor._extract_comment() == (None, 0)


def test_extract_multiline_comment():
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('/* test_comment')
        extractor._extract_comment()
    assert syntax_error.value.msg == 'Multiline comment was never closed 1:1'
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('/* test_comment *')
        extractor._extract_comment()
    assert syntax_error.value.msg == 'Multiline comment was never closed 1:1'
    extractor = ExtractTokens('/* test_comment */dfdfsaf')
    assert (
        extractor._extract_comment() == (
            RawToken('/* test_comment */', ('1:1', '1:18'), TokenType.COMMENT),
            17
        )
    )
    extractor = ExtractTokens('/* test_comment \n test_comment_part_2*/')
    assert (
        extractor._extract_comment() == (
            RawToken(
                '/* test_comment \n test_comment_part_2*/',
                ('1:1', '2:22'),
                TokenType.COMMENT
                ),
            38
        )
    )


def test_extract_bin_number():
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0b')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Invelid binary number at 1:1'

    extractor = ExtractTokens('0b01')
    assert (
        extractor._extract_number() == (
            RawToken('0b01', ('1:1', '1:4'), TokenType.BIN_INT_CONST), 3
        )
    )
    extractor = ExtractTokens('0b01 ')
    assert (
        extractor._extract_number() == (
            RawToken('0b01', ('1:1', '1:4'), TokenType.BIN_INT_CONST), 3
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0b02')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Binary number at 1:1 is followed by invalid symbol'


def test_extract_oct_number():
    extractor = ExtractTokens('0')
    assert (
        extractor._extract_number() == (
            RawToken('0', ('1:1', '1:1'), TokenType.OCT_INT_CONST), 0
        )
    )
    extractor = ExtractTokens('0 ')
    assert (
        extractor._extract_number() == (
            RawToken('0', ('1:1', '1:1'), TokenType.OCT_INT_CONST), 0
        )
    )
    extractor = ExtractTokens('00')
    assert (
        extractor._extract_number() == (
            RawToken('00', ('1:1', '1:2'), TokenType.OCT_INT_CONST), 1
        )
    )
    extractor = ExtractTokens('01234567')
    assert (
        extractor._extract_number() == (
            RawToken('01234567', ('1:1', '1:8'), TokenType.OCT_INT_CONST), 7
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('08')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Invalid number defenition at 1:1'

    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0778')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Invalid number defenition at 1:1'


def test_extract_hex_number():
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0x')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Invelid hex number at 1:1'
    extractor = ExtractTokens('0x0')
    assert (
        extractor._extract_number() == (
            RawToken('0x0', ('1:1', '1:3'), TokenType.HEX_INT_CONST), 2
        )
    )
    extractor = ExtractTokens('0xABCDEF')
    assert (
        extractor._extract_number() == (
            RawToken('0xABCDEF', ('1:1', '1:8'), TokenType.HEX_INT_CONST), 7
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0x1H')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Hex number at 1:1 is followed by invalid symbol'


def test_extract_float_number():
    extractor = ExtractTokens('0.')
    assert (
        extractor._extract_number() == (
            RawToken('0.', ('1:1', '1:2'), TokenType.FLOAT_CONST), 1
        )
    )
    extractor = ExtractTokens('0.1')
    assert (
        extractor._extract_number() == (
            RawToken('0.1', ('1:1', '1:3'), TokenType.FLOAT_CONST), 2
        )
    )
    extractor = ExtractTokens('.1')
    assert (
        extractor._extract_number() == (
            RawToken('.1', ('1:1', '1:2'), TokenType.FLOAT_CONST), 1
        )
    )
    extractor = ExtractTokens('0123456789.0123456789')
    assert (
        extractor._extract_number() == (
            RawToken('0123456789.0123456789', ('1:1', '1:21'), TokenType.FLOAT_CONST), 20
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('0.a')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Float number at 1:1 is followed by invalid symbol'
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('1.a')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Float number at 1:1 is followed by invalid symbol'
    extractor = ExtractTokens('123456789.0123456789')
    assert (
        extractor._extract_number() == (
            RawToken('123456789.0123456789', ('1:1', '1:20'), TokenType.FLOAT_CONST), 19
        )
    )


def test_extract_dec_number():
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('12l')
        extractor._extract_number()
    assert syntax_error.value.msg == 'Invalid number defenition at 1:1'
    extractor = ExtractTokens('123456789')
    assert (
        extractor._extract_number() == (
            RawToken('123456789', ('1:1', '1:9'), TokenType.DEC_INT_CONST), 8
        )
    )


def test_extract_char():
    extractor = ExtractTokens("'h'")
    assert (
        extractor._extract_char() == (
            RawToken("'h'", ('1:1', '1:3'), TokenType.CHAR_CONST), 2
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens("'ha")
        extractor._extract_char()
    assert syntax_error.value.msg == 'Invalid char const defenetion at 1:1'


def test_extract_string():
    extractor = ExtractTokens('"ha"')
    assert (
        extractor._extract_string_const() == (
            RawToken('"ha"', ('1:1', '1:4'), TokenType.STRING_CONST), 3
        )
    )
    with pytest.raises(SyntaxError) as syntax_error:
        extractor = ExtractTokens('"ha')
        extractor._extract_string_const()
    assert syntax_error.value.msg == 'String at 1:1 wath never closed'


def test_extract_identifier():
    extractor = ExtractTokens('test')
    assert (
        extractor._extract_identifier() == (
            RawToken('test', ('1:1', '1:4'), TokenType.IDENTIFIER), 3
        )
    )
    extractor = ExtractTokens('_est')
    assert (
        extractor._extract_identifier() == (
            RawToken('_est', ('1:1', '1:4'), TokenType.IDENTIFIER), 3
        )
    )
    extractor = ExtractTokens('.est')
    assert (
        extractor._extract_identifier() == (
            None, 0
        )
    )
    extractor = ExtractTokens('t1_3_5')
    assert (
        extractor._extract_identifier() == (
            RawToken('t1_3_5', ('1:1', '1:6'), TokenType.IDENTIFIER), 5
        )
    )
