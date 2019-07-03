import re


def create_word_list_from_doc(doc_text):
    words = re.split(r'\W+', doc_text)
    return words