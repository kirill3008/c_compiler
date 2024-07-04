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


if __name__ == '__main__':
    main()
