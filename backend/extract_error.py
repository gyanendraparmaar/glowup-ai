import codecs
import re

try:
    with codecs.open('test_log.txt', 'r', 'utf-16le') as f:
        content = f.read()
except:
    with open('test_log.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

# find Prompt generated block
idx = content.find("Preview:")
if idx != -1:
    end_idx = content.find("[STEP 3]", idx)
    if end_idx == -1: end_idx = idx + 2000
    prompt_text = content[idx:end_idx].strip()
    with open("extracted_prompt.txt", "w", encoding="utf-8") as out:
        out.write(prompt_text)
else:
    with open("extracted_prompt.txt", "w", encoding="utf-8") as out:
        out.write("Could not find prompt in test_log.txt")

# also grab any traceback
tb_idx = content.rfind("Traceback ")
if tb_idx != -1:
    with open("extracted_error.txt", "w", encoding="utf-8") as out:
        out.write(content[tb_idx:tb_idx+1000])
