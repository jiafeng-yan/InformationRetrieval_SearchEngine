import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.search.spell import SpellChecker, PlainTextDictionary
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from java.nio.file import Paths
import json
from spellcheck import spell_check


def spell_check_last_word(query_text, num_suggestions=5, index_dir='dir', dictionary_path='dictionary.txt'):
    # 获取最后一个单词
    tokens = tokenize_text(query_text)
    last_word = tokens[-1] if tokens else ""

    if not last_word:
        return []

    # # 创建一个字典
    # directory = NIOFSDirectory.open(Paths.get(index_dir))
    # spellchecker = SpellChecker(directory)  # 创建拼写检查器
    
    # analyzer = StandardAnalyzer()  # 使用标准分析器
    # config = IndexWriterConfig(analyzer)
    
    # # 使用词典文件来生成拼写索引
    # dictionary = PlainTextDictionary(Paths.get(dictionary_path))
    # spellchecker.indexDictionary(dictionary, config, True)  # 构建拼写建议的索引
    
    # 获取拼写建议
    suggestions = spell_check(last_word, num_suggestions)
    
    return list(suggestions)

def tokenize_text(text, analyzer=None):
    """
    使用 Lucene 分词器对文本进行分词，并返回分词后的单词列表。
    """
    analyzer = analyzer or StandardAnalyzer()  # 默认使用标准分析器
    tokenStream = analyzer.tokenStream("field", text)
    termAttr = tokenStream.getAttribute(CharTermAttribute.class_)
    tokenStream.reset()

    tokens = []
    while tokenStream.incrementToken():
        tokens.append(termAttr.toString())

    tokenStream.end()
    tokenStream.close()
    
    return tokens