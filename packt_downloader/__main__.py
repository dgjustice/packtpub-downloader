from argparse import ArgumentParser, Action
import sys
import typing as t

from packt_downloader import run_it, config


def check_requested_ftypes(file_types: t.Set[str]) -> None:
    """Check for valid file types"""
    diff = file_types - config.BOOK_FILE_TYPES
    if diff:
        print(f"{diff} are not supported file types")
        sys.exit(1)


class FileTypeAction(Action):
    """Class to allow custom validationd of  file types"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(FileTypeAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        ftl = set(values.split(","))
        check_requested_ftypes(ftl)
        setattr(namespace, self.dest, ftl)


def main():
    """Parse args and pass off to the __init__ module."""

    parser = ArgumentParser(prog="packt_downloader")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", action="store_true", dest="verbose")
    group.add_argument("-q", action="store_true", dest="quiet")
    parser.add_argument("-e", "--email", type=str, required=True, help="account e-mail")
    parser.add_argument(
        "-p",
        "--pass",
        type=str,
        required=True,
        help="account password",
        dest="password",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        required=False,
        help="dowload destination directory",
    )
    parser.add_argument(
        "-b", "--books", type=str, required=False, action=FileTypeAction
    )
    parser.add_argument("-s", "--separate", type=bool, required=False, default=True)
    run_it(parser.parse_args())


if __name__ == "__main__":
    main()  # type: ignore
