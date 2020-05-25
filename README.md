# PacktPub Downloader

A coworker pointed me to this script, and I figured it would be a great opportunity to kick the tires on dry-python's `returns` library.
Many hours and rabbit holes later... I kinda have a solution, but it's not complete yet by any stretch.

## Usage

```bash
poetry install
python -m packt_downloader -e $PACKT_EMAIL -p $PACKT_PASSWORD
```

### Example: Download books in PDF format

```bash
python -m packt_downloader -e $PACKT_EMAIL -p $PACKT_PASSWORD -b pdf
```

## Commandline Options

WIP

- [X] `-e, --email = Your login emai`
- [X] `-p, --password = Your login passwor`
- [ ] `-d, --directory = Directory to download into. Default is "media/" in the current director`
- [X] `-b, --books = Assets to download. Options are: pdf,mobi,epub,code`
- [ ] `-s, --separate = Create a separate directory for each boo`
- [X] `-v, --verbose = Show more detailed informatio`
- [X] `-q, --quiet = Don't show information or progress bar`

### Book File Types

- pdf: PDF format
- mobi: MOBI format
- epub: EPUB format
- code: Accompanying source code, saved as .zip files

I'm working in Python 3.7

## Original fork comments from [lmbringas](https://github.com/lmbringas/packtpub-downloader)

Script to download all your PacktPub books inspired by [ozzieperez](https://github.com/ozzieperez/packtpub-library-downloader).

Since PacktPub restructured their website [packtpub-library-downloader](https://github.com/ozzieperez/packtpub-library-downloader) became obsolete because the downloader used webscraping.
So I figured out that now PacktPub uses a REST API.
Then I found which endpoint to use for downloading books and made a simple script.
Feel free to fork and PR to improve.
Packtpub's API isn't documented :'(
