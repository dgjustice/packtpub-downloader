import typing as t

from pydantic import BaseModel


class FileTypeData(BaseModel):
    """Inner model for URL_BOOK_TYPES_ENDPOINT"""

    fileTypes: t.List[str]


class FileTypes(BaseModel):
    """Model for URL_BOOK_TYPES_ENDPOINT"""

    data: t.List[FileTypeData]


class BookURL(BaseModel):
    """Model for URL_BOOK_ENDPOINT"""

    data: str


class AuthTokenData(BaseModel):
    """Inner model for authentication"""

    refresh: str
    access: str


class AuthToken(BaseModel):
    """Model authentication"""

    data: AuthTokenData


class BookData(BaseModel):
    """Model inner list of PRODUCTS_ENDPOINT"""

    id: str
    userId: str
    productId: str
    productName: str
    releaseDate: str
    entitlementSource: str
    entitlementLink: str
    createdAt: str
    updatedAt: str


class BookRequest(BaseModel):
    """Model PRODUCTS_ENDPOINT"""

    data: t.List[BookData]
    count: int


class BookWithFileTypes(BaseModel):
    """Helper model for get_book_file_types"""

    book: BookData
    file_types: FileTypes


class BookWithURL(BaseModel):
    """Helper model for get_book_file_types"""

    book: BookData
    url: BookURL
    filename: str
