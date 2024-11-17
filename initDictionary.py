import nltk
from nltk.corpus import words

# 下载 NLTK 词汇
nltk.download('words')

# 获取英文单词列表
word_list = words.words()

# 将单词列表保存为文本文件
with open("dictionary.txt", "w") as f:
    for word in word_list:
        f.write(word + "\n")

# 错词替换和 拼写纠正 使用了lucene中的SpellChecker 输入英语字典 这里我们使用了nltk中的默认英语字典导入到本地
# 并且另外实现了在前端中可以让用户输入自定义单词来新建词汇
# 例如：在 [窗口] 中，输入lucene，那么我们输入 luncene 就可以进行纠正