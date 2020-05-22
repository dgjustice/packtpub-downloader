"""
This file contain all url endpoint
"""

# this is base url where i do the requests
BASE_URL = "https://services.packtpub.com/"

# URL to request jwt token, params by post are user and pass, return jwt token
AUTH_ENDPOINT = "auth-v1/users/tokens"

# URL to get all your books, two params that i change are offset and limit, method GET
PRODUCTS_ENDPOINT = "entitlements-v1/users/me/products?sort=createdAt:DESC&offset={offset}&limit={limit}"  # noqa

# URL to get types , param is  book id, method GET
URL_BOOK_TYPES_ENDPOINT = "products-v1/products/{book_id}/types"

# URL to get url file to download, params are book id and format of
# the file (can be pdf, epub, etc..), method GET
URL_BOOK_ENDPOINT = "products-v1/products/{book_id}/files/{format}"

MEDIA_DIR = "media"

BOOK_FILE_TYPES = {"pdf", "mobi", "epub", "code"}

# need to fill Authoritazion with current token provide by api
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 "
    + "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Authorization": "",
}
