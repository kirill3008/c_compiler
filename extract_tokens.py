import click
import logging

logger = logging.getLogger(__name__)


# STATES FOR PARSER
NONE = 0
IDENTIFIER = 1
OP = 2
SINGLE_LINE_COMMENT = 3
MULTILINE_COMMENT = 4
NUMBER = 5


def parse(content: str) -> list[str]:
    result = []
    state = NONE
    token = ''
    index = 0
    while index < len(content):
        symbol = content[index]
        if state == NONE:
            if symbol.isalpha() or symbol == '_':
                state = IDENTIFIER
                token = symbol
            elif symbol == '/':
                if content[index + 1] == '/':
                    state = SINGLE_LINE_COMMENT
                    while content[index] != '\n':
                        token += content[index]
                        index += 1
                    result.append((state, token))
                    state = NONE
                    token = ''
                if content[index + 1] == '*':
                    state = MULTILINE_COMMENT
                    while content[index:index+2] != '*/':
                        token += content[index]
                        index += 1
                    index += 1
                    token += '*/'
                    result.append((state, token))
                    state = NONE
                    token = ''
            elif symbol.isspace():
                pass
            elif symbol.isnumeric():
                state = NUMBER
                token = symbol
            else:
                state = OP
                token = symbol
                result.append((state, token))
                state = NONE
                token = ''
        elif state == IDENTIFIER:
            if symbol.isalnum() or symbol == '_':
                token += symbol
            else:
                result.append((state, token))
                state = NONE
                token = ''
                continue
        elif state == NUMBER:
            if symbol.isnumeric() or symbol == '.':
                token += symbol
            else:
                result.append((state, token))
                state = NONE
                token = ''
                continue
        else:
            logger.error('Shouldn\'t be here')
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
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')
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
        with open(file, 'r') as f:
            print(*(x[1] for x in parse(f.read())), sep='\n')



if __name__ == '__main__':
    main()
