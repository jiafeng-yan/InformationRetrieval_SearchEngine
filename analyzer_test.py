import sys, os, lucene

from org.apache.lucene.analysis import Analyzer, TokenStream, LowerCaseFilter, StopFilter
# from org.apache.lucene.analysis.TokenStream import TokenStreamComponents
from org.apache.lucene.analysis.en import PorterStemFilter, EnglishAnalyzer #, CapitalizationFiler
# from org.apache.lucene.analysis.custom import CustomAnalyzer
from org.apache.lucene.analysis.standard import StandardTokenizer #, StandardAnalyzer #, StandardFilter
from org.apache.pylucene.analysis import PythonAnalyzer
from java.nio.file import Paths

class PorterStemmerAnalyzer(PythonAnalyzer):

    def createComponents(self, fieldName):
        source = StandardTokenizer()
        filter = LowerCaseFilter(source)
        filter = PorterStemFilter(filter)
        filter = StopFilter(filter, EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

        return self.TokenStreamComponents(source, filter)
    
    def initReader(self, fieldName, reader):
        return reader


class CustomAnalyzer(Analyzer):
    def __init__(self, stop_words):
        super(CustomAnalyzer, self).__init__()
        self.stop_words = stop_words

    def createComponents(self, field_name):
        # 使用标准的 StandardTokenizer
        tokenizer = StandardTokenizer()
        
        # 添加 LowerCaseFilter 将所有文本转换为小写
        tokenStream = LowerCaseFilter(tokenizer)
        
        # 添加 StopFilter 处理停用词
        tokenStream = StopFilter(tokenStream, self.stop_words)
        
        # 返回 TokenStreamComponents，包含自定义的分词器和过滤器
        return Analyzer.TokenStreamComponents(tokenizer, tokenStream)

if __name__ == '__main__':
    # 初始化JVM
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    # 定义自定义的停用词列表
    stop_words_list = ['the', 'is', 'and', 'a', 'to']
    stop_words_set = set(stop_words_list)

    # 使用自定义的分析器
    # analyzer = CustomAnalyzer(stop_words_set)
    
    # init analyzer
    # analyzer = StandardAnalyzer()
    # analyzer = CustomAnalyzer.builder(Paths.get('analyzer_config'))    \
    #     .withTokenizer('standard')       \
    #     .addTokenFilter("lowercase")     \
    #     .addTokenFilter("stop")          \
    #     .addTokenFilter("porterstem").build()
    #     # .addTokenFilter("capitalization").build()

    ## GPT generated
    # analyzer = CustomAnalyzer.builder() \
    #     .withTokenizer(StandardTokenizer()) \
    #     .addTokenFilter(LowerCaseFilter()) \
    #     .addTokenFilter(StopFilter(stop_words_set)) \
    #     .build()

    ## version 2
    # src = StandardTokenizer()
    # # result = StandardFilter(src)
    # result = LowerCaseFilter(src)
    # result = StopFilter(True, result, stop_words_set) #StandardAnalyzer.STOP_WORDS_SET)
    # # result = PorterStemFilter(result)
    # # result = CapitalizationFiler(result)
    # analyzer = TokenStream.TokenStreamComponents(src, result)

    ## offcial
    analyzer = PorterStemmerAnalyzer()

    # 示例：分析文本
    text = "This is a simple example to demonstrate custom analyzer in PyLucene."
    token_stream = analyzer.tokenStream("field", text)
    
    # 开始处理 TokenStream
    token_stream.reset()
    while token_stream.incrementToken():
        print(token_stream.reflectAsString(True))  # 输出每个 token
    token_stream.end()
    token_stream.close()
