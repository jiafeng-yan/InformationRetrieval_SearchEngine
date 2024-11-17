import os
import lucene
from org.apache.lucene.store import FSDirectory, NIOFSDirectory
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search.spell import SpellChecker, PlainTextDictionary
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.util import Version
from java.nio.file import Paths
# from lucene.store import RAMDirectory  # 这样导入 RAMDirectory


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

def change_dict(str=''):
    from nltk.corpus import words

    try:
        # 获取英文单词列表
        word_list = words.words()

        for word in str.strip().split(';'):
            word_list.append(word)

        word_list.sort()

        # 将单词列表保存为文本文件
        with open("dictionary.txt", "w+") as f:
            for word in word_list:
                f.write(word + "\n")
    except Exception as e:
        return False

    return True

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


def spell_check(incorrect_word, num_suggestions=5, index_dir='tmp_dir', dictionary_path='dictionary.txt'):
    directory = NIOFSDirectory.open(Paths.get(index_dir))
    spellchecker = SpellChecker(directory)  # 创建拼写检查器

    analyzer = StandardAnalyzer()  # 使用标准分词器
    config = IndexWriterConfig(analyzer)
    # 使用词典文件来生成拼写索引
    dictionary = PlainTextDictionary(Paths.get(dictionary_path))
    spellchecker.indexDictionary(dictionary, config, True)  # 构建拼写建议的索引

    # 测试拼写纠正
    suggestions = spellchecker.suggestSimilar(incorrect_word, num_suggestions)

    return suggestions


if __name__ == '__main__':
    incorrect_word = 'telk'
    # incorrect_word = "lucnene"
    num_suggestions = 6
    index_dir = 'test_dir'
    dictionary_path = "dictionary.txt"
    
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    # 示例使用
    suggestions = spell_check(incorrect_word, num_suggestions, index_dir, dictionary_path)

    print("Suggestions for '{}':".format(incorrect_word))
    for suggestion in suggestions:
        print(suggestion)
