# Information Retrieval Search Engine

This project is a Information Retrieval Search Engine that allows you to index and search scholarly papers. It consists of three main components:
- extracting metadata and text from PDFs using GroBid
- building an inverted index using Lucene, also several other humanized functions
- implementing a simple web search interface using Flask

## Requirements
```
Python 3.9
Flask
pyLucene (Python wrapper for Lucene)
```
## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/jiafeng-yan/InformationRetrieval_SearchEngine.git
```

2. Install the required Python packages:

```bash
pip install Flask pyLucene
```

3. Download and install [Grobid](https://grobid.readthedocs.io/) for PDF processing.

## Run 
```cmd
python app.py
cd ./frontend/
npm start
```

## Features

- User-friendly front-end design
- Normal query / Boolean query / multi-field query / wildcard query
- paging (Max 5 pages with 15 items each page)
- dynamic digest generation / highlight \& customized highlight settings
- spelling correction \& customized checking dictionary 
- stop words \& customized stop words dictionary
- Allow to upload your own pdf files

## Details
More details please see: ```CUFE__School_of_Information__Information_Retrieval_task1_Lucene_.pdf```

## Contributors

- [jiafneg-yan](https://github.com/jiafeng-yan)

## License

This project is licensed under the [MIT License](LICENSE).
