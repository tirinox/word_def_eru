from util import *
from config import *
import academic_parse
from fake_useragent import UserAgent


def main():
    ua = UserAgent()
    session = create_new_session(ua)
    test = academic_parse.download_word_definition('ПАН', session)
    print(test)

if __name__ == '__main__':
    main()