# PacktPub Downloader

Script to download all your PacktPub books inspired by https://github.com/ozzieperez/packtpub-library-downloader.

Since PacktPub restructured their website [packtpub-library-downloader](https://github.com/ozzieperez/packtpub-library-downloader) became obsolete because the downloader used webscraping.
So I figured out that now PacktPub uses a REST API.
Then I found which endpoint to use for downloading books and made a simple script.
Feel free to fork and PR to improve.
Packtpub's API isn't documented :'(

## Usage:

```bash
poetry install
python -m packt_downloader -e $PACKT_EMAIL -p $PACKT_PASSWORD
```

##### Example: Download books in PDF format

```bash
python -m packt_downloader -e $PACKT_EMAIL -p $PACKT_PASSWORD
```

	python main.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -b pdf,epub,mobi,code

## Commandline Options

WIP

- *[X] -e*, *--email* = Your login email
- *[X] -p*, *--password* = Your login password
- [ ] *-d*, *--directory* = Directory to download into. Default is "media/" in the current directory
- [X] *-b*, *--books* = Assets to download. Options are: *pdf,mobi,epub,code*
- [ ] *-s*, *--separate* = Create a separate directory for each book
- *[X] -v*, *--verbose* = Show more detailed information
- *[X] -q*, *--quiet* = Don't show information or progress bars

### **Book File Types**

- *pdf*: PDF format
- *mobi*: MOBI format
- *epub*: EPUB format
- *code*: Accompanying source code, saved as .zip files

I'm working in Python 3.7

