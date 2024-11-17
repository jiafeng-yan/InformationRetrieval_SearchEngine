import os
import requests

# open docker

## CRF-only image
# cmd : docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.8.1

## Deep Learning and CRF image
# cmd : docker run --rm --gpus all --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.1

def getXml(file_path, output_filepath):
    # url = "http://localhost:8070/api/processFulltextDocument"
    url = "https://kermitt2-grobid.hf.space/api/processFulltextDocument"
    filename = file_path.split("/")[-1].split(".")[-2]
    print(filename)
    params = dict(input=open(file_path, "rb"))
    response = requests.post(url, files=params, timeout=500)
    print(response)

    save_path = os.path.join(output_filepath, filename + ".xml")
    print(save_path)
    fh = open(save_path, "w", encoding="utf-8")
    fh.write(response.text)
    fh.close()


def run(files_paths, files):

    for file_path in files_paths:

        getXml(file_path, files)
        break


if __name__ == "__main__":
    # files = "./data/grobid_data"
    # files = "E:\\files\oriPDFs"
    # output_files = "E:\\files\output_TEI_XMLs"
    # files_path = [os.path.join(files, i) for i in os.listdir(files)]
    # run(files_path, files)

    file_path = './uploads/Seafusion.pdf'
    output_files = './tmp/'
    getXml(file_path, output_files)


# cmd : python3 -m grobid_client.grobid_client --input E:/files/virtualbox_share/oriPDFs --output E:/files/virtualbox_share/output_TEI_XMLs --config D:/Codefield/Python/RANDOM/CUFE_InformationRetrieval/test1/config.json processFulltextDocument
# cmd : python3 -m grobid_client.grobid_client --input E:/files/virtualbox_share/oriPDFs --output E:/files/virtualbox_share/output_TEI_XMLs --n 4 processFulltextDocument
# cmd : python3 -m grobid_client.grobid_client --input E:/files/virtualbox_share/oriPDFs --output E:/files/virtualbox_share/out_TEI_XMLs --config D:/Codefield/Python/RANDOM/CUFE_InformationRetrieval/test1/config.json --force --n 2 processFulltextDocument




# --force : 强制覆盖输出

"""
others:

usage: grobid_client [-h] [--input INPUT] [--output OUTPUT] [--config CONFIG]
                     [--n N] [--generateIDs] [--consolidate_header]
                     [--consolidate_citations] [--include_raw_citations]
                     [--include_raw_affiliations] [--force] [--teiCoordinates]
                     [--verbose]
                     service

Client for GROBID services

positional arguments:
  service               one of ['processFulltextDocument',
                        'processHeaderDocument', 'processReferences',
                        'processCitationList','processCitationPatentST36',
                        'processCitationPatentPDF']

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         path to the directory containing PDF files or .txt
                        (for processCitationList only, one reference per line)
                        to process
  --output OUTPUT       path to the directory where to put the results
                        (optional)
  --config CONFIG       path to the config file, default is ./config.json
  --n N                 concurrency for service usage
  --generateIDs         generate random xml:id to textual XML elements of the
                        result files
  --consolidate_header  call GROBID with consolidation of the metadata
                        extracted from the header
  --consolidate_citations
                        call GROBID with consolidation of the extracted
                        bibliographical references
  --include_raw_citations
                        call GROBID requesting the extraction of raw citations
  --include_raw_affiliations
                        call GROBID requestiong the extraciton of raw
                        affiliations
  --force               force re-processing pdf input files when tei output
                        files already exist
  --teiCoordinates      add the original PDF coordinates (bounding boxes) to
                        the extracted elements
  --segmentSentences    segment sentences in the text content of the document
                        with additional <s> elements
  --verbose             print information about processed files in the console
"""

"""
service subscription

/api/processHeaderDocument:
Extract the header of the input PDF document, normalize it and convert it into a TEI XML or BibTeX format.

/api/processFulltextDocument:
Convert the complete input document into TEI XML format (header, body and bibliographical section).

/api/processReferences:
Extract and convert all the bibliographical references present in the input document into TEI XML or BibTeX format.

"""