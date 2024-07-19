import click
import logging

from . import ExtractTokens


logger = logging.getLogger(__name__)


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
            raw_tokens = ExtractTokens(f.read()).extract()
            print(*raw_tokens, sep='\n')


if __name__ == '__main__':
    main()
