from typing import Iterator, List, Set, Tuple

from nltk.tokenize import sent_tokenize as nltk_sent_tokenize
from nltk.corpus import stopwords
from nltk import word_tokenize as nltk_word_tokenize
from nltk.util import trigrams  # skipgrams(_, n, k); n - deg, k - skip dist

import re


# This can be varied
language = 'russian'.lower()
removeStops = True  # `= set()` for not removing stopwords
puncts = set('.,!?')


# language dispatch
sent_tokenize = lambda text: nltk_sent_tokenize(text, language)
word_tokenize = lambda text: nltk_word_tokenize(text, language)
stopwords = set(stopwords.words(language)) if removeStops else set()
if language == 'russian':
    from nltk.stem.snowball import RussianStemmer as Stemmer
else:
    from nltk.stem.snowball import EnglishStemmer as Stemmer


# Remove unnecessary tokens
def remove_sth(seq: Iterator[str], sth: Set[str]) -> Iterator[str]:
    """ Generic function for removal """
    return filter(lambda x: x not in sth, seq)


def remove_puncts(seq: Iterator[str]) -> Iterator[str]:
    return remove_sth(seq, puncts)


def remove_stops(seq: Iterator[str]) -> Iterator[str]:
    return remove_sth(seq, stopwords)


# Translators
def wordsToStemmed(sent: Iterator[str], stemmer) -> List[str]:
    return [stemmer.stem(word) for word in sent]


def fileToSents(filename: str) -> List[str]:
    with open(filename) as file:
        try:
            text = file.read()
        except:
            file.close()
            file = open(filename, encoding='utf-8')
            text = file.read()
        text = re.sub("\s+", ' ', text)  # "hi     man" ~> "hi man"
        return sent_tokenize(text)


def sentsToWords(sents: List[str]) -> List[List[str]]:
    # FIXME: remove_stops . remove_puncts ~> remove_sth(_, stops | puncts)
    # FIXME: list . map
    stemmer = Stemmer()
    return [
        wordsToStemmed(
            remove_stops(
                remove_puncts(
                    word_tokenize(sent))),
            stemmer) for sent in sents]


def wordsToTrigrams(words: List[List[str]]) -> List[List[Tuple[str, str, str]]]:
    # FIXME: list . map
    return [list(trigrams(sent)) for sent in words]


if __name__ == "__main__":
    pass