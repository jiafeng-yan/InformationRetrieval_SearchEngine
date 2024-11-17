import os
import lucene
from lucene.collections import JArray, JavaSet
from org.apache.lucene.analysis import CharArraySet
from org.apache.lucene.analysis.en import PorterStemFilter, EnglishAnalyzer
from org.apache.lucene.analysis.core import LowerCaseFilter, StopFilter
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.document import Document, Field, TextField, FieldType, StringField, StoredField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import FSDirectory, MMapDirectory, NIOFSDirectory
from java.nio.file import Paths

import collections

from lxml import etree


class CustomPorterStemmerAnalyzer(PythonAnalyzer):
    def __init__(self, stop_word_list=[]):
        extended_stop_words_set = CharArraySet(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET, True)
        for word in stop_word_list:
            extended_stop_words_set.add(word)
        self.stopWordList = extended_stop_words_set

    def createComponents(self, fieldName):
        source = StandardTokenizer()
        filter = LowerCaseFilter(source)
        filter = PorterStemFilter(filter)
        filter = StopFilter(filter, self.stopWordList)

        return self.TokenStreamComponents(source, filter)
   
    def initReader(self, fieldName, reader):
        return reader
     
    
def mkdir(index_dir):
   if os.path.exists(index_dir):
      import shutil
      shutil.rmtree(index_dir)
   os.makedirs(index_dir)

def update_lib(file_path, stop_words=[]):
   try:
      ## pdf to xml
      # 调用Grobid
      import requests
      # url = "http://localhost:8070/api/processFulltextDocument"
      url = "https://kermitt2-grobid.hf.space/api/processFulltextDocument"
      filename = file_path.split("/")[-1].split(".")[-2]
      params = dict(input=open(file_path, "rb"))
      response = requests.post(url, files=params, timeout=500)

      # 临时保存xml
      mkdir('./tmp')
      save_path = os.path.join('tmp', filename + ".xml")
      print(save_path)
      with open(save_path, "w", encoding="utf-8") as fh:
         fh.write(response.text)

      ## initIndex
      indexFile('dir', 'tmp', stop_words)
   except Exception as e:
      return False
   finally:
      pass
   return True


def update_stop(stop_words=''):
   try:
      stop_list = stop_words.strip().split(';')

      indexFile(stop_list=stop_list)
   except Exception as e:
      return False
   return True


def indexFile(index_dir='dir', xml_folder="../output_TEI_XMLs", stop_list=[], addition=True):

   if not addition:
      mkdir(index_dir)

   assert os.path.exists(xml_folder), f'xml dir: {xml_folder} is empty' 

   # init analyzer
   # analyzer = StandardAnalyzer()
   # analyzer = CustomPorterStemmerAnalyzer()

   extended_stop_words = CharArraySet(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET, True)
   for word in stop_list:
      extended_stop_words.add(word)
   analyzer = StandardAnalyzer(extended_stop_words)
   # analyzer = EnglishAnalyzer(extended_stop_words)

   # init directory obj
   # directory = FSDirectory.open(Paths.get(index_dir))
   directory = NIOFSDirectory.open(Paths.get(index_dir))

   # init IndexWriterConfig
   config = IndexWriterConfig(analyzer)
   ## optimization 控制写入一个新的Segment前内存中保存的document的数目，较大数目可以加快建索引速度
   # config.setMaxBufferedDocs(500)

   # IndexWriter outstream obj
   indexWriter = IndexWriter(directory, config)
   ## optimization N个段合并成一个段 数值越大建索引速度越快，搜索速度越慢
   # indexWriter.forceMerge(N_to_set)

   # gather information from tei_xml & insert document & write
   cnt = 1
   for filename in os.listdir(xml_folder):
      print(f'{cnt:03}  -=-  {filename}')
      cnt += 1
      file_path = os.path.join(xml_folder, filename)

      document = Document()

      ## lxml
      tree = etree.parse(file_path)
      root = tree.getroot()

   #  ns = '{' + f'{root.get('xmlns')}' + '}'
   #  print(ns)
      ns = '{http://www.tei-c.org/ns/1.0}'

      paths = {
         'title': "{0}teiHeader/{0}fileDesc/{0}titleStmt/{0}title".format(ns),
         'funder': "{0}teiHeader/{0}fileDesc/{0}titleStmt/{0}funder".format(ns),
         'author': "{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}persName".format(ns),
         'email': "{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}email".format(ns),
         'affiliation': "{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}affiliation/{0}orgName".format(ns),
         'address': "{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}affiliation/{0}address".format(ns),
         'date': "{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}monogr/{0}imprint/{0}date".format(ns),
         'keyword': "{0}teiHeader/{0}profileDesc/{0}textClass/{0}keywords".format(ns),
         'abstract': "{0}teiHeader/{0}profileDesc/{0}abstract".format(ns),
         'fulltext': '{0}text/{0}body'.format(ns),
      }
      for field, path in paths.items():
         tmp = ''
         for a in root.findall(path):
            tmp += ' '.join(a.xpath('string(.)').split()) + '\n'
         document.add(TextField(field, tmp, Field.Store.YES))

      # document.add(StoredField('name', '.'.join(filename.split('.')[0])))
      if filename.endswith('.grobid.tei.xml'):
         name = filename[:-15]
      else:
         name = filename[:-4]
      document.add(StoredField('name', name))

      indexWriter.addDocument(document)

   indexWriter.commit()
   indexWriter.close()




if __name__ == '__main__':

   # 初始化JVM
   lucene.initVM(vmargs=['-Djava.awt.headless=true'])   # vmargs=['-Djava.awt.headless=true']

   ## init args
   index_dir = 'dir'
   xml_dir = "../output_TEI_XMLs"
   # index_dir = 'test_dir'
   # xml_dir = "TEI_XML"

   ## index
   indexFile(index_dir, xml_folder=xml_dir, addition=False)

    






      # title = root.find("{0}teiHeader/{0}fileDesc/{0}titleStmt/{0}title".format(ns)).text
      # document.add(TextField("title", title, Field.Store.YES))

      # tmp = ''
      # for funder in root.findall("{0}teiHeader/{0}fileDesc/{0}titleStmt/{0}funder".format(ns)):
      #    tmp += ''.join(funder.xpath('string(.)').split()) + '\n'
      # document.add(TextField("funder", tmp, Field.Store.YES))
         
      # tmp = ''
      # for author in root.findall("{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}persName".format(ns)):
      #    tmp += ''.join(author.xpath('string(.)').split()) + '\n'
      # document.add(TextField("author", tmp, Field.Store.YES))

      # tmp = ''
      # for email in root.findall("{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}email".format(ns)):
      #    tmp += ''.join(email.text.split()) + '\n'
      # document.add(TextField("email", tmp, Field.Store.YES))

      # tmp = ''
      # for affiliation in root.findall("{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}affiliation/{0}orgName".format(ns)):
      #    tmp += ''.join(affiliation.xpath('string(.)').split()) + '\n'
      # document.add(TextField("affiliation", tmp, Field.Store.YES))

      # tmp = ''
      # for address in root.findall("{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}analytic/{0}author/{0}affiliation/{0}address".format(ns)):
      #    tmp += ''.join(address.xpath('string(.)').split()) + '\n'
      # document.add(TextField("address", tmp, Field.Store.YES))

      # date = root.find("{0}teiHeader/{0}fileDesc/{0}sourceDesc/{0}biblStruct/{0}monogr/{0}imprint/{0}date".format(ns)).text
      # if date is not None:
      #    document.add(TextField("date", date, Field.Store.YES))

      # keyword = root.find("{0}teiHeader/{0}profileDesc/{0}textClass/{0}keywords".format(ns)).xpath('string(.)')
      # # print('keyword', keyword)
      # document.add(TextField("keyword", keyword, Field.Store.YES))
         
      # abstract = root.find("{0}teiHeader/{0}profileDesc/{0}abstract".format(ns)).xpath('string(.)')
      # # print('Abstract', abstract)
      # document.add(TextField("abstract", abstract, Field.Store.YES))

      # fulltext = root.find('{0}text/{0}body'.format(ns)).xpath('string(.)')
      # # print(fulltext)
      # document.add(TextField("fulltext", fulltext, Field.Store.YES))

      # pass # ... other field val to add

"""
以下是TEI文件中`<title>`, `<author>`, `<date>`, `<affiliation>`, `<address>` 和 `<fulltext>` 这些域对应的路径：

1. **标题 (title)**:
   - 主要标题: `/TEI/teiHeader/fileDesc/titleStmt/title[@level="a" and @type="main"]`

2. **作者 (authors)**:
   - 作者列表: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author`

3. **日期 (date)**:
   - 日期: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/monogr/imprint/date[@type="published"]`

4. **机构 (affiliation)**:
   - 作者1所属机构: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[1]/affiliation`
   - 作者2所属机构: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[2]/affiliation`
   - 作者3所属机构: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[3]/affiliation`
   - 作者4所属机构: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[4]/affiliation`

5. **地址 (address)**:
   - 作者1地址: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[1]/affiliation/address`
   - 作者2地址: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[2]/affiliation/address`
   - 作者3地址: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[3]/affiliation/address`
   - 作者4地址: `/TEI/teiHeader/fileDesc/sourceDesc/biblStruct/analytic/author[4]/affiliation/address`

6. **全文 (fulltext)**:
   - 正文: `/TEI/text/body/div`

这些路径可以帮助你找到TEI文件中相应的信息。
"""

# // 1. gather data
# SkuDao skuDao = new SkuDaoImpl();
# List< Sku> skuList = skuDao.querySkuList();

# List<Document> docList = new ArrayList<Document>();
# // 2. init doc obj
# for(Sku sku: skuList) {
#     Document document = new Document();
#     // init field obj & into doc obj
#     document.add(new TextField("id", sku.getId(), Field.Store.YES));
#     document.add(new TextField("name", sku.getName(), Field.Store.YES));
#     document.add(new TextField("price", String.valueOf(sku.getPrice()), Field.Store.YES));
#     document.add(new TextField("image", sku.getImage(), Field.Store.YES));
#     document.add(new TextField("categoryName", sku.getCategoryName(), Field.Store.YES));
#     document.add(new TextField("brandName", sku.getBrandName(), Field.Store.YES));
#     // put doc obj into docList
#     docList.add(document);
# }
# // 3. init analyzer
# Analyzer analyzer = new StandardAnalyzer();
# // 4. init directory obj
# Directory dir = new FSDirectory.open(Paths.get("E:/Apache/dir"));
# // 5. init IndexWriterConfig obj (in which the analyzer to use is assigned)
# IndexWriterConfig config = new IndexWriterConfig(analyzer);
# // 6. init IndexWriter out-stream obj (assigning output location & used config initialization obj)
# IndexWriter indexWriter = new IndexWriter(dir, config);
# // 7. write doc to index database
# for(Document doc: docList) {
#     indexWriter.addDocument(doc);
# }
# // 8. release resource
# indexWriter.close();