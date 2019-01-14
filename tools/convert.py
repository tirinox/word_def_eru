# encoding=utf8
import sys
import codecs

def parse(raw_text):
    d = {}
    return d

def load_text(file_name):
    with codecs.open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

def main():

    print(sys.getdefaultencoding())

    file_name = 'data/raw/dict1.txt'
    text = load_text(file_name)
    print(text[0:1000])

if __name__ == "__main__":
    main()