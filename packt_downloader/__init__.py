import glob
import logging
import os
import pdb  # noqa
import sys
import typing as t
from functools import partial, reduce

import gevent
from gevent import monkey
from gevent.pool import Pool
from pydantic import ValidationError

from packt_downloader import config, models
from returns.context import RequiresContext

from returns.curry import curry
from returns.converters import flatten
from returns.io import IO, IOResultE, impure_safe
from returns.maybe import maybe
from returns.functions import tap

logger = logging.getLogger(__name__)

# Gevent patch for requests
monkey.patch_all()

import requests  # noqa
import requests_cache  # noqa


# requests_cache.install_cache()  # Sorry, Packt-people!


class User:
    """User object

    There are much more FP-approved ways of doing this, but meh.
    """

    def __init__(self, email: str = "", password: str = "") -> None:
        self.email = email
        self.password = password
        self._token: str = ""
        self._session = requests.Session()
        self._session.hooks = {"response": self.refresh_token}  # type: ignore

    def get_token(self) -> None:
        """Request auth endpoint and return user token

        Return an IOResult and produces a side effect of setting the `STATE`
        """
        url = config.BASE_URL + config.AUTH_ENDPOINT
        # use json paramenter because for any reason they send user and pass in plain text :'(
        resp = self.session.post(
            url, json={"username": self.email, "password": self.password}
        )
        if resp.status_code == 200:
            logger.info("You are in!")
            token_data = models.AuthToken(**resp.json())
            token = "Bearer " + token_data.data.access
            config.HEADERS["Authorization"] = token
            self.session.headers.update(**config.HEADERS)
            return
        logger.error("Failed to obtain auth token")
        logger.error("status_code: %s, json: %s", resp.status_code, resp.json())
        raise Exception("Auth failure!")

    def refresh_token(self, resp, *args, **kwargs):
        """Hook for requests session"""

        if resp.status_code == 401:
            logger.info("Refreshing token")
            self.get_token()

    @property
    def token(self):
        return self._token

    @property
    def session(self):
        return self._session


def request_with_model(url: str, model: t.Any, session: t.Any) -> t.Any:
    """Wrap up requests.get with logging"""
    resp = session.get(url)
    if resp.status_code == 200:
        try:
            return model(**resp.json())
        except ValidationError as e:
            logger.error("%s", e.json())
            raise
    logger.error(
        "url: %s, status_code: %s, json: %s", url, resp.status_code, resp.json()
    )
    raise Exception("Request error")


def assets_request(
    offset: int = 0, limit: int = 10
) -> RequiresContext["User", IOResultE[models.BookRequest]]:
    """Call the Packt API and get a list of books

    Require context from an auth token
    Return a wrapped RequiresContext
    """

    @impure_safe
    def inner(user: "User") -> models.BookRequest:
        url = config.BASE_URL + config.PRODUCTS_ENDPOINT.format(
            offset=offset, limit=limit
        )
        return request_with_model(url, models.BookRequest, user.session)

    return RequiresContext(inner)


def get_asset_list(
    resp_obj: models.BookRequest, offset: int = 0, limit: int = 10
) -> t.List[t.Any]:
    """Get a list of assets for the user.

    One call must be made upstream to retrieve the count.
    This cannot be done with limit=0.

    Take the count and build a list requests to retrieve all assets.
    """
    count = resp_obj.count
    logger.info("You have %s assets", count)
    reqs = []
    for i in range((count // limit) + 1):
        reqs.append(partial(assets_request, offset=offset, limit=limit))
        offset += limit
    return reqs


def run_reqs(
    req_list: t.List[t.Any]
) -> RequiresContext["User", IOResultE[t.List[RequiresContext[t.Any, t.Any]]]]:
    """Take a list of partial requests and return the results

    Require user context
    Return a list of IOResult objects
    """

    @impure_safe
    def inner(user: "User") -> t.List[RequiresContext]:
        pool = Pool(10)
        output = []
        with gevent.Timeout(3600):
            jobs = [pool.spawn(req(), user) for req in req_list]
            pool.join()
            for job in jobs:
                # Gotcha! If job failed, job.value defaults to `None`
                if job.successful():
                    output.append(job.value)
                else:
                    logger.error(
                        "Job failed, successful: %s, value: %s",
                        job.successful,
                        job.get(),
                    )
        return output

    return RequiresContext(inner)


def mapM(list_io: t.List[IOResultE[t.Any]]) -> IO[t.List]:
    """Trying to hack Haskell mapM"""

    @curry
    def concat(a, b):
        return a + b

    in_list = lambda v: [v]  # noqa
    return reduce(
        lambda a, b: a.apply(b.map(in_list).apply(IO(concat))),
        (io.value_or(None) for io in list_io),
        IO.from_value([]),
    )


def flatten_asset_list(
    book_lists: t.List[models.BookRequest]
) -> t.List[models.BookData]:
    """Flatten a list of lists"""
    output = []
    for book_list in book_lists:
        for book in book_list.data:
            output.append(book)
    return output


def get_asset_url(
    book: models.BookData, file_type="pdf", filename: str = ""
) -> RequiresContext["User", IOResultE[models.BookWithURL]]:
    """ Return url of the book to download (Packt uses ephemeral URLs)"""

    @impure_safe
    def inner(user: "User") -> models.BookWithURL:
        url = config.BASE_URL + config.URL_BOOK_ENDPOINT.format(
            book_id=book.productId, format=file_type
        )
        book_url = request_with_model(url, models.BookURL, user.session)
        return models.BookWithURL(book=book, url=book_url, filename=filename)

    return RequiresContext(inner)


def get_asset_file_types(
    book: models.BookData
) -> RequiresContext["User", IOResultE[models.BookWithFileTypes]]:
    """ Return a list with file types of a book

    NOTE: Not all documents have a summary under types, so this may return 404."""

    @impure_safe
    def inner(user: "User") -> models.BookWithFileTypes:
        url = config.BASE_URL + config.URL_BOOK_TYPES_ENDPOINT.format(
            book_id=book.productId
        )
        file_type = request_with_model(url, models.FileTypes, user.session)
        return models.BookWithFileTypes(book=book, file_types=file_type)

    return RequiresContext(inner)


@impure_safe
def move_current_files(root: str, book: str) -> None:
    """TODO: not used"""
    sub_dir = f"{root}/{book}"
    try:
        os.makedirs(sub_dir, exist_ok=True)
    except Exception:
        logger.exception("Failed to create director")
        raise
    for f in glob.iglob(sub_dir + ".*"):
        try:
            os.rename(f, f"{sub_dir}/{book}" + f[f.index(".") :])  # noqa
        except OSError:
            os.rename(f, f"{sub_dir}/{book}" + "_1" + f[f.index(".") :])  # noqa
        except ValueError:
            logger.exception("Failed to create director")
            raise


def download_asset(
    book_url: models.BookWithURL
) -> RequiresContext["User", IOResultE[None]]:
    """ Download your book and do a mess of bad IO"""

    @impure_safe
    def inner(user: "User") -> None:
        filename = book_url.filename
        logger.info("Starting to download %s", filename)
        if os.path.exists(filename) and os.path.exists(
            filename.replace(".code", ".zip")
        ):
            logger.debug(f"{filename} already exists, skipping.")
            return
        with open(filename, "wb") as fp:
            resp = user.session.get(book_url.url.data, stream=True)
            if resp.status_code != 200:
                logger.error(f"Failed to download {book_url.url.data}")
            total = resp.headers.get("content-length")
            if total is None:
                fp.write(resp.content)
            else:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        fp.write(chunk)
                        fp.flush()
                logger.info("Finished " + filename)
        if filename[-4:] == "code":
            os.replace(filename, filename[:-4] + "zip")

    return RequiresContext(inner)


@maybe
def get_asset_url_request(data):
    book, file_type = data
    """Take book and file_type, return a request for the book URL"""
    if (
        file_type not in config.BOOK_FILE_TYPES
    ):  # check if the file type entered is available by the current book
        logger.debug("%s not in types for %s", file_type, book.productName)
        return
    book_name = (
        book.productName.replace(" ", "_")
        .replace(".", "_")
        .replace(":", "_")
        .replace("/", "")
    )
    filename = f"{config.MEDIA_DIR}/{book_name}.{file_type}"

    # get url of the book to download
    return partial(get_asset_url, book, file_type, filename)


def run_it(args) -> None:
    """Do all the things"""

    logging.basicConfig()
    logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.CRITICAL)
    user = User(email=args.email, password=args.password)
    requested_types = args.books or {"pdf"}

    try:
        user.get_token()
    except Exception:
        sys.exit(1)
    if not os.path.exists(config.MEDIA_DIR):
        try:
            os.makedirs(config.MEDIA_DIR)
        except Exception:
            logger.exception("Cannot create media directory")
            sys.exit(1)

    logger.info("Retrieving your book list...")
    (
        flatten(
            assets_request(offset=0, limit=1)(user)
            .map(get_asset_list)
            .bind(run_reqs)(user)
            .map(mapM)
        )
        .map(flatten_asset_list)
        .map(tap(lambda v: logger.debug("len flatten_ass %s", len(v))))
        .map(lambda books: map(lambda book: partial(get_asset_file_types, book), books))
        .bind(run_reqs)(user)
        .map(mapM)
        .map(lambda v: list(filter(lambda i: i, list(flatten(v)))))
        .map(tap(lambda v: logger.debug("Got file types")))  # type: ignore
        .map(
            lambda book_w_ftl: [
                (book_ft.book, ft)
                for book_ft in book_w_ftl
                for ft in book_ft.file_types.data[0].fileTypes
                if ft in requested_types
            ]
        )
        .map(
            tap(lambda v: logger.debug("Translated list len %s", len(v)))
        )  # type: ignore
        .map(
            lambda book_ftl: map(
                lambda ftl: get_asset_url_request(ftl).value_or(None), book_ftl
            )
        )
        .map(lambda v: filter(lambda i: i, v))
        .bind(run_reqs)(user)
        .map(
            tap(lambda v: logger.info("%s files available for download", len(v)))
        )  # type: ignore
        .map(mapM)
        .map(
            lambda book_urls: map(
                lambda book_url: partial(download_asset, book_url), flatten(book_urls)
            )
        )
        .bind(run_reqs)(user)
        .map(mapM)
    )
