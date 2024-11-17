from lucene.include.org.apache.lucene.analysis.standard import StandardAnalyzer
from lucene.include.org.apache.lucene.document import Document, TextField, Field
from lucene.include.org.apache.lucene.index import IndexWriter, IndexWriterConfig
from lucene.include.org.apache.lucene.store import FSDirectory
from lucene.include.java.nio.file import Paths
import lucene
import os


class Indexer:
    def __init__(self, doClear=True, computeLengthNorm=False):
        lucene.getVMEnv().attachCurrentThread()
        self.dir = FSDirectory.open(Paths.get(INDEX_PATH))  # 索引存储位置
        self.analyzer = StandardAnalyzer()                  # 分词器类型
        self.config = IndexWriterConfig(self.analyzer)      # 索引器配置
        self.writer = IndexWriter(self.dir, self.config)    # 建立索引器

    def newIndex(self):
        for i in range(len(os.listdir(DOC_PATH))):  # 遍历数据集中的所有文档
            dir = os.path.join(DOC_PATH, os.listdir(DOC_PATH)[i])
            for j in range(len(os.listdir(dir))):
                fname = os.listdir(dir)[j]
                title = fname[0:-4]             # 提取文档标题
                text = ""
                with open(os.path.join(dir, fname), "r") as f:  # 提取文档内容
                    for line in f:
                        if line[0] != "<" and line[-1] != ">":
                            text += line[0:-1]
                    text += "\n"
                doc = Document()                # 创建文档对象
                titleField = TextField("title", title, Field.Store.YES)
                # 为 title 字段创建信息字段对象，选择完全存储
                textField = TextField("text", text, Field.Store.NO)
                # 为 text 字段创建信息字段对象，选择不存储（为了减少索引文件的大小，不存储的内容将来无法从索引中直接获取）
                doc.add(titleField)             # 将信息字段对象添加到文档对象中
                doc.add(textField)              # 将信息字段对象添加到文档对象中
                self.writer.addDocument(doc)    # 将文档对象添加到索引器中
        self.writer.close()                     # 关闭索引器
