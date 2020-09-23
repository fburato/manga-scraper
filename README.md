# Manga extractor

The scripts in this repository can be used to download en-masse mangas hosted at [mangastream.xyz](http://mangastream.xyz).

[extractor.py](extractor.py) takes as input the root of a manga in the website and recursively downloads every chapter in it. The chapters
are divided in folders which are numbered using padded increasing numbers to be lexicographically ordered.

[download_chapter.py](download_chapter.py) takes as input the a chapter in the website and downloads the images in a certain
directory of choice. This script can be used after a mass download to get chapters that are still being published.

## Installation

In order to run the scripts, you will need to have python 3.8 installed in your system. You can install it either 
by downloading it directly from the [python website](https://www.python.org/downloads/) or by installing it through 
[chocolatey](https://chocolatey.org).

Once python is installed, open a terminal and install the package `virtualenv` with

```commandline
pip install virtualenv
```

Clone the repository containing the scripts from github in your computer and navigate to the directory in the terminal.

From the root of the repository, define a new virtual environment with

```commandline
virtualenv .env
```

And activate it. In Windows, run

```commandline
.\.env\Scripts\activate
```

In *nix systems, run

```shell script
source .env/bin/activate
```

Install all the dependencies with

```commandline
pip install -r requirements.txt
```

The scripts are now ready to be executed.

## Running

### extractor.py

To run the script, ensure that the installation steps have been completed and ensure that the virtual environment is 
activated in windows with

```commandline
.\.env\Scripts\activate
```

and in *nix systems, with

```shell script
source .env/bin/activate
```

Once the virtual environment is activated, choose the root of a manga from [mangastream.xyz](http://mangastream.xyz),
for example [http://mangastream.xyz/manga/full-metal-alchemist](http://mangastream.xyz/manga/full-metal-alchemist), and copy
the url.

Then simply run, from the command line with the virtual environment active:

```commandline
python extractor.py http://mangastream.xyz/manga/full-metal-alchemist
```

The script will create a directory called `full-metal-alchemist` and will also create as many directory as there are 
chapters in the manga. Once all chapters have been scraped, the script will start to download with 50 parallel threads
the images from all the chapters, numbering them in ascending order.

### download_chapter.py

To run the script, ensure that the installation steps have been completed and ensure that the virtual environment is 
activated in windows with

```commandline
.\.env\Scripts\activate
```

and in *nix systems, with

```shell script
source .env/bin/activate
```

Once the virtual environment is activated, choose a chapter of a manga from [mangastream.xyz](http://mangastream.xyz),
for example [http://mangastream.xyz/full-metal-alchemist-chapter-108](http://mangastream.xyz/full-metal-alchemist-chapter-108), and copy
the url.

Then simply run, from the command line with the virtual environment active:

```commandline
python download_chapter.py full-metal-alchemist http://mangastream.xyz/full-metal-alchemist-chapter-108
```

The second argument to the script is the root directory where the chapter will be downloaded, while the third argument
is the page that contains the chapter images.
