import codecs
with codecs.open('test_log.txt', 'r', 'utf-16le') as f:
    text = f.read()
    print(text)
