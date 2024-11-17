import os
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import FSDirectory, RAMDirectory
from java.nio.file import Paths

# 初始化JVM
lucene.initVM()

# 定义索引目录
index_dir = "E:\Apache\dir"
if not os.path.exists(index_dir):
    os.makedirs(index_dir)

# 创建索引存储目录和配置
directory = FSDirectory.open(Paths.get(index_dir))  # 使用 FSDirectory
analyzer = StandardAnalyzer()
config = IndexWriterConfig(analyzer)
index_writer = IndexWriter(directory, config)

# 读取 XML 文件并添加到索引
xml_folder = "path/to/xml/folder"  # 指定你的 XML 文件夹路径
for filename in os.listdir(xml_folder):
   pass


# Lucene允许通过包装 BoostQuery来影响查询的各个部分的得分贡献，也就是通过设置boost值。 org.apache.lucene.search.BoostQuery
# 上面提到过Boost，它影响着索引阶段和搜索阶段。在索引阶段设定文档的Document.setBoost和域的Field.setBoost值，这些值是在索引阶段就写入索引文件的，存储在标准化因子(.nrm)文件中，一旦设定，除非删除此文档，否则无法改变。如果不进行设定，则Document Boost和Field Boost默认为1。在6.4版本中已经不再支持了。

# 调整Similarity是改变评分算法，这在索引时使用IndexWriterConfig.setSimilarity(Similarity) 进行，在查询时使用IndexSearcher.setSimilarity(Similarity)进行。确保在查询时使用与索引时相同的相似性（以便规范被正确编码/解码）；Lucene不努力验证这一点。
# Similarity是非常重要的接口，它的实现非常多。ClassicSimilarity曾经是Lucene/Solr默认评分公式，但是从lucene-6.0开始已经改成BM25Similarity了。

# ClassicSimilarity 它是TFIDFSimilarity的实现类，它的计算公式：tf * idf * boost * lengthNorm lengthNorm，一个域中包含的Term总数越多，也即文档越长，此值越小，文档越短，此值越大，公式：(1.0 / Math.sqrt(numTerms))

# BM25Similarity BM25的idf和tf都做了一些变形，特别是tf公式（它叫tfNorm），还加入了两个经验参数k1和b（主要用来调整精准度），默认取K1=1.2，b=0.75。

"""
术语 (items)

Index-索引库	

Document的集合组成索引；
和一般的数据库不一样，Lucene不支持定义主键，在Lucene中不存在一个叫做Index的类，通过IndexWriter来写索引，通过IndexReader来读索引；
索引库在物理形式上一般是位于一个路径下的一系列文件；参考索引结构

Analyzer-分析器	
:
一段有意义的文字需要通过Analyzer分析器分割成一个个词语后才能按关键字搜索；
StandardAnalyzer是Lucene中最常用的分析器，不同的语言可以使用不同的搜索器；

Token-词	
:
Analyzer返回的结果是一串Token；
Token包含一个代表词本身含义的字符串和该词在文章中相应的起止偏移位置，Token还包含一个用来存储词类型的字符串；

段(segment)	
:
段是由多个文档构成,每一次索引都是由一组文件构成的,即一个段,如果是full build,那么新生成的段会和旧有的段合并,如果是增量索引，那么增量数据会有自己独立的段

Document-文档	
:
一个Document代表索引库中的一条记录，由很多的Field组成；Index和Search的最小单位（要搜索的信息封装成Document后通过IndexWriter写入索引库，调用Searcher接口按关键词搜索后，返回的也是一个封装后的Document列表）；

Field-文档列	
:
一个Document可以包含多个列，由很多的Term组成，包括Field Name和Field Value；
与一般数据库不同，一个文档的一个列可以有多个值

Term-词语	
:
是搜索语法的最小单位（复杂的搜索语法会分解成一个Term查询）；
Term由很多的字节组成，一般将Text类型的Field Value分词之后的每个最小单元叫做Term；

文档编号(id)
:
Lucene通过一个整型的文档编号指向每个文档，第一个被加入索引的文档编号为0，后续加入的文档编号依次递增。你可以理解为id就是documentId也叫docId。
注意文档编号是可能发生变化的，所以在Lucene外部存储这些值时需要格外小心。
"""

# org.apache.lucene.analysis
	

"""分词器定义、标准分词器的实现

org.apache.lucene.codes 编解码

org.apache.lucene.document 文档相关

org.apache.lucene.geo 地理空间相关

org.apache.lucene.index 索引相关

org.apache.lucene.search 搜索相关

org.apache.lucene.store 存储相关

org.apache.lucene.util 其他
"""

ramDirecotry = RAMDirectory
idxWriterCfg = IndexWriterConfig()
writer = IndexWriter(ramDirecotry, directory);

"""
build
0.directory
1.indexWriter
2.tokenize index store
3.做索引库 commit

read
0.directory
1.reader directoryReader.open(directory) 
2.seracher = indexSearcher(reader)
3.queryParser(filednam2query, analyser)
4.query = parser.parse(string2query)
5.results = searcher.search(query, top_k)

"""

public class Lucene_test {
    //存储选择内存
    private Directory directory = new RAMDirectory();
    @Test
    public void quickStart() throws IOException, ParseException {
        //Directory directory = FSDirectory.open(Paths.get("target"));
        IndexWriterConfig config = new IndexWriterConfig();
        //1.创建IndexWriter
        IndexWriter writer = new IndexWriter(directory, config);
        System.out.println(writer.getConfig());
        //支持分词索引，存储
        TextField name = new TextField("name", "Donald Trump", Field.Store.YES);
        Document doc = new Document();
        doc.add(name);
        //2.做索引库
        writer.addDocument(doc);
        //3.提交
        writer.commit();
        writer.close();
 
        IndexReader reader = DirectoryReader.open(directory);
        //打开索引
        IndexSearcher searcher = new IndexSearcher(reader);
        String filedName = "name";
        //MultiFieldQueryParser parser = new MultiFieldQueryParser(new String[] { "name"},new StandardAnalyzer());
        QueryParser parser = new QueryParser(filedName, new StandardAnalyzer());//new IKAnalyzer4Lucene7(true));
        Query query = parser.parse("Trump");//解析查询
        TopDocs results = searcher.search(query, 100);//检索并取回前100个文档号
        for (ScoreDoc hit : results.scoreDocs) {
            Document hitDoc = searcher.doc(hit.doc);//真正取文档
            System.out.println(hitDoc.get(filedName));
            System.out.println("doc:" + hitDoc);
        }
        reader.close();
        directory.close();
    }
}