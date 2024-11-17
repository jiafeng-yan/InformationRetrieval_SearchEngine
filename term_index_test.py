import lucene
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.index import DirectoryReader, PostingsEnum
from org.apache.lucene.util import BytesRef
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths

lucene.initVM()

# 打开已有的索引目录
index_dir = NIOFSDirectory(Paths.get("test_dir"))
reader = DirectoryReader.open(index_dir)

# 遍历索引中的每个叶节点
for leaf in reader.leaves():
    leaf_reader = leaf.reader()  # 获取 LeafReader 对象
    
    # 获取索引中的所有字段
    field_infos = leaf_reader.getFieldInfos()
    
    for field_info in field_infos:
        field_name = field_info.get('name')
        # field_name = 'test.grobid.tei'
        print(f"Field: {field_name}")
        
        # 获取该字段的术语（terms）
        terms = leaf_reader.terms(field_name)
        if terms is not None:
            terms_enum = terms.iterator()  # 获取 TermsEnum
            while terms_enum.next() is not None:
                term = terms_enum.term().utf8ToString()  # 获取术语字符串
                doc_freq = terms_enum.docFreq()  # 获取文档频率
                print(f"Term: {term}, DocFreq: {doc_freq}")
                
                # 获取倒排表 (postings) 以便查看术语在哪些文档中出现
                postings_enum = terms_enum.postings(None, PostingsEnum.ALL)
                while postings_enum.nextDoc() != PostingsEnum.NO_MORE_DOCS:
                    doc_id = postings_enum.docID()
                    freq = postings_enum.freq()
                    print(f"  DocID: {doc_id}, Freq: {freq}")