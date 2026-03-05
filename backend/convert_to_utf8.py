import codecs

with codecs.open("prompts_out.txt", "r", "utf-16le") as f_in:
    content = f_in.read()

with codecs.open("prompts_utf8.txt", "w", "utf-8") as f_out:
    f_out.write(content)
