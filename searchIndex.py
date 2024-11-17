import os
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.document import Document, Field, TextField, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.store import FSDirectory, MMapDirectory, NIOFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.queryparser.flexible.standard import StandardQueryParser
from org.apache.lucene.analysis.en import PorterStemFilter, EnglishAnalyzer
from org.apache.lucene.analysis.core import LowerCaseFilter, StopFilter
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, Formatter, SimpleHTMLFormatter, Fragmenter, SimpleSpanFragmenter, InvalidTokenOffsetsException
from org.apache.lucene.search.uhighlight import UnifiedHighlighter, PassageFormatter
from java.nio.file import Paths
from string import Template
from lucene.collections import JavaList
from org.apache.lucene.analysis import CharArraySet
import time

# class CustomTemplate(Template):
#     delimiter = '#'

# format = '#title#date#keyword'
# template = CustomTemplate(format)


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
    
    
# 创建自定义 PassageFormatter
class CustomPassageFormatter(PassageFormatter):
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def format(self, passages, content):
        highlighted_fragments = []
        
        if not passages:
            # 如果没有高亮片段，返回原内容
            return content

        for passage in passages:
            # 获取片段的起止位置
            start = passage.getStartOffset()
            end = passage.getEndOffset()

            # 检查 start 和 end 的有效性
            if start < 0 or end > len(content):
                continue
            
            # 包裹高亮词
            highlighted_text = self.begin + content[start:end] + self.end
            highlighted_fragments.append(highlighted_text)
        
        # 将所有高亮片段连接成一个字符串
        return "".join(highlighted_fragments)

# class SearchIndex():
    # def __init__(self, index_dir='dir', stop_list=[]):

def search(query, top_k=80, abstractMaxLen=1000, highlightNum=10, index_dir='dir', stop_list=[]):

        # init analyzer
        # analyzer = StandardAnalyzer()
        # self.analyzer = CustomPorterStemmerAnalyzer()
        # self.analyzer = StandardAnalyzer()

        extended_stop_words = CharArraySet(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET, True)
        for word in stop_list:
            extended_stop_words.add(word)
        analyzer = StandardAnalyzer(extended_stop_words)

        ### 建索引时使用stopword会使查不到该词，搜索时使用stopword会使不能高亮
        # extended_stop_words = CharArraySet(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET, True)
        # for word in stop_list:
        #     extended_stop_words.add(word)
        # analyzer = StandardAnalyzer(extended_stop_words)

        # init query obj
        ## single field query
        # queryParser = QueryParser('fulltext', analyzer)     # 第一个参数: 默认查询域, 如果查询的关键字中带搜索的域名, 则从指定域中查询, 如果不带域名则从, 默认搜索域中查询
        ## multi fields query
        # fields = JavaList(['title', 'keyword', 'abstract', 'fulltext'])
        # boots = {
        #     'title': 1,
        #     'keyword': 0.8,
        #     'abstract': 0.5,
        #     'fulltext': 0.3,
        # }
        queryParser = StandardQueryParser(analyzer)
        # qpConfig = self.queryParser.getQueryConfigHandler()
        # StandardQueryConfigHandler config =  qpHelper.getQueryConfigHandler()
        # qpConfig.setAllowLeadingWildcard(True)
        queryParser.setAllowLeadingWildcard(True)
        # queryParser = MultiFieldQueryParser(fields, analyzer)
        # self.queryParser.setDefaultOperator(QueryParser.Operator.AND)    # 默认运算符

        # init directory obj
        # directory = FSDirectory.open(Paths.get(index_dir))
        directory = NIOFSDirectory.open(Paths.get(index_dir))

        # init in-stream obj
        indexReader = DirectoryReader.open(directory)

        # init search obj
        indexSearcher = IndexSearcher(indexReader)

        # customize query
        query = queryParser.parse(query, 'fulltext')

        # search
        start = time.time()
        topDocs = indexSearcher.search(query, top_k)   # 第二个参数: 是返回多少条数据用于展示, 分页使用
        end = time.time()


        # ### simple highlighter
        scorer = QueryScorer(query)
        fragmenter = SimpleSpanFragmenter(scorer, abstractMaxLen)
        # 高亮格式器
        # formatter = SimpleHTMLFormatter("<b><font color='yellow' size='bond'>","</font></b>")
        formatter = SimpleHTMLFormatter("<b><font -===- -=bold=- -=italic=- -==- -=colorfont=->","</font></b>")
        # 高亮器
        highlighter = Highlighter(formatter, scorer)
        highlighter.setTextFragmenter(fragmenter)

        # ### Unified Highlighter
        # highlighter = UnifiedHighlighter(self.indexSearcher, self.analyzer)
        # formatter = CustomPassageFormatter("<b><font color='yellow' size='bond'>","</font></b>")
        # highlighter.setFormatter(formatter)
        # # fragmenter = SimpleSpanFragmenter()
        # # highlighter.setFragmenter(fragmenter)
        # # highlighter.setFormatter(CustomPassageFormatter('--------', '----------'))
        # highlighter.setMaxNoHighlightPassages(abstractMaxNum)
        # # highlighter.setMaxFragmentSize(abstractMaxLen)

        scoreDocs = topDocs.scoreDocs
        docInfo = []
        # abstractMaxNum = 400
        
        for scoreDoc in scoreDocs:
            docID = scoreDoc.doc
            document = indexSearcher.doc(docID)
            info = {
                'title': document.get('title'),
                'author': document.get('author'),
                'abstract': document.get('abstract'),
                'address': document.get('address'),

                # 'docID': docID,
                # 'name': document.get('name'),

                #### have been highlighted
                # 'title': ''.join(list(simple_highlighter.getBestFragments(self.analyzer, 'title', document.get('title'), abstractMaxLen))),
                # 'author': simple_highlighter.getBestFragments(self.analyzer, 'author', document.get('author'), abstractMaxLen),
                # 'abstract': simple_highlighter.getBestFragments(self.analyzer, 'abstract', document.get('abstract'), abstractMaxLen),
                # 'address': simple_highlighter.getBestFragments(self.analyzer, 'address', document.get('address'), abstractMaxLen),

                'docID': docID,
                'name': document.get('name'),
                # 'generation': 
            }
            fulltext = document.get('fulltext')
            tokenStream = analyzer.tokenStream('fulltext', fulltext)
            generation = highlighter.getBestFragments(tokenStream, fulltext, highlightNum)
            info['generation'] = ''.join(list(generation))[:abstractMaxLen]
            print(len(generation), '--------------')
            
            # abstract = document.get('abstract')
            # tokenStream = self.analyzer.tokenStream('abstract', abstract)
            # generation = highlighter.getBestFragments(tokenStream, abstract, abstractMaxNum)
            # info['generation'] = list(generation)[0] if generation else ''
            
            docInfo.append(info)

            # print()
        # generation = highlighter.highlight('fulltext', query, topDocs)
        # generation = highlighter.highlight('fulltext', query, topDocs)
        indexReader.close()
        
        return {
            'totalHits': f'{topDocs.totalHits}'.split()[0],     ## 1386+
            'time': end - start,    # millisecond
            'docInfo': docInfo,
        }


if __name__ == '__main__':
    
    detail = True
    query = 'KESSLER'
    query = 'computer OR mock'
    # query = '*omputer'
    # query = ' Although we have only executed the mock trial event twice'
    query = 'comprises students'
    query = ''
    print('query: ', query)

    # index_dir = "test_dir"
    index_dir = 'dir'
    assert os.path.exists(index_dir), f"index dir: {index_dir} not exists"
    
    lucene.initVM() #vmargs=['-Djava.awt.headless=true'])
    # print(lucene.VERSION)

    result = search(query, 80, 1000, 20, 'test_dir')

    totalHits = result['totalHits']

    print(f'======== result count: {totalHits} hits ========')

    docInfo = result['docInfo']

    for info in docInfo:
        docID = info['docID']
        name = info['name']
        print(f'{docID:03}  -=-  {name}')
        if detail:
            print()
            for field, val in info.items():
                print(f' {field}: {val}')
            # for field in ['title', 'date', 'keyword', 'funder', 'author', 'email', 'affiliation', 'address', 'abstract', 'fulltext']:
            #     print(f'{field}: {document.get(f'{field}')}')
            # table = dict((field.name(), field.stringValue()) for field in document.getFields())
            # print(template.substitute(table))
            print()
            print('======================')






"""
//1. 创建分词器(对搜索的关键词进行分词使用)
//注意: 分词器要和创建索引的时候使用的分词器一模一样
Analyzer analyzer = new StandardAnalyzer();

//2. 创建查询对象,
//第一个参数: 默认查询域, 如果查询的关键字中带搜索的域名, 则从指定域中查询, 如果不带域名则从, 默认搜索域中查询
//第二个参数: 使用的分词器
QueryParser queryParser = new QueryParser("name", analyzer);

//3. 设置搜索关键词
//华 OR  为   手   机
Query query = queryParser.parse("华为手机");

//4. 创建Directory目录对象, 指定索引库的位置
Directory dir = FSDirectory.open(Paths.get("E:\\dir"));
//5. 创建输入流对象
IndexReader indexReader = DirectoryReader.open(dir);
//6. 创建搜索对象
IndexSearcher indexSearcher = new IndexSearcher(indexReader);
//7. 搜索, 并返回结果
//第二个参数: 是返回多少条数据用于展示, 分页使用
TopDocs topDocs = indexSearcher.search(query, 10);

//获取查询到的结果集的总数, 打印
System.out.println("=======count=======" + topDocs.totalHits);

//8. 获取结果集
ScoreDoc[] scoreDocs = topDocs.scoreDocs;

//9. 遍历结果集
if (scoreDocs != null) {
    for (ScoreDoc scoreDoc : scoreDocs) {
        //获取查询到的文档唯一标识, 文档id, 这个id是lucene在创建文档的时候自动分配的
        int  docID = scoreDoc.doc;
        //通过文档id, 读取文档
        Document doc = indexSearcher.doc(docID);
        System.out.println("==================================================");
        //通过域名, 从文档中获取域值
        System.out.println("===id==" + doc.get("id"));
        System.out.println("===name==" + doc.get("name"));
        System.out.println("===price==" + doc.get("price"));
        System.out.println("===image==" + doc.get("image"));
        System.out.println("===brandName==" + doc.get("brandName"));
        System.out.println("===categoryName==" + doc.get("categoryName"));

    }
}
//10. 关闭流
"""