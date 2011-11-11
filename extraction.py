#! /usr/bin/env python
#! utils/extraction.py

"""This module provides functionality for extracting various types of information from text
files.

Allows extraction of:
- Words
- Sentences
- Tagged sentences
"""

import nltk
import nltk.data
import nltk.tokenize
import nltk.tag.util
import re
from utils.decorators import memoized
from utils import files


############################## CONVENIENCE FUNCTIONS ###############################################
@memoized
def get_from_nltk(obj_name):
    "Returns a tokenizer or tagger from NLTK."
    if obj_name == 'TOKENIZER':
        return nltk.tokenize.WordPunctTokenizer()
    if obj_name == 'SENTENCE_TOKENIZER':
        return nltk.data.load('tokenizers/punkt/english.pickle')
    if obj_name == 'TAGGER':
        return nltk.data.load('taggers/maxent_treebank_pos_tagger/english.pickle')
    return None

def get_tokenizer():
    return get_from_nltk('TOKENIZER')

def get_sentence_tokenizer():
    return get_from_nltk('SENTENCE_TOKENIZER')

def get_tagger():
    return get_from_nltk('TAGGER')

def omit_blank(lines):
    "Filters out purely whitespace strings from a list of strings."
    return [line for line in lines if len(line.strip()) > 0]

def omit_blanks_if_asked(lines, ignore):
    return omit_blank(lines) if ignore else lines

def strip_if_asked(line, strip):
    return line.strip() if strip else line


############################## EXTRACTION FUNCTIONS ################################################
def lines(filename, strip=True):
    """Returns a list of lines in a text file.
    
    Newlines and whitespace are stripped off the ends of these lines by default.
    """
    with open(filename, 'r') as f:
        return [strip_if_asked(line, strip) for line in f]

def text(filename):
    "Returns the text from a file as a single string."
    with open(filename, 'r') as f:
        lines = f.readlines()
    return '\n'.join([line.strip() for line in lines])

def split_text(filename, pattern, flags=None):
    """Split text in file by occurrences of a regular expression pattern.

    Flags may be supplied in the style of re.split()/re.match(). Returns a list of strings.
    """
    ftext = text(filename)
    p = re.compile(pattern)
    return p.split(ftext) if flags is None else p.split(ftext, flags)

def text_lines(text, ignore_blank=True):
    """Returns a list of lines in a string.

    Blank lines are omitted by default.
    """
    return omit_blanks_if_asked(text.split('\n'), ignore_blank)



############################## TOKENIZATION/TAGGING FUNCTIONS ######################################
def words(text):
    """Returns a list of words contained in a string representing a piece of text.

    Tokenization is performed using a WordPunctTokenizer from NLTK.
    """
    tokenizer = get_tokenizer()
    return tokenizer.tokenize(text)

def sentences(text, realign_boundaries=True):
    """Returns a list of words contained in a string representing a piece of text.

    Tokenization is performed using a WordPunctTokenizer from NLTK.
    """
    tokenizer = get_sentence_tokenizer()
    return tokenizer.tokenize(text, realign_boundaries=realign_boundaries)


def xtagged_tuples(text, realign_boundaries=True):
    """Returns a generator for a list of tagged tuple lists representing the tagged sentences
    in this text.

    Each tuple list contains entries of the form (word, tag).
    """
    tagger = get_tagger()
    tokenizer = get_tokenizer()
    for sentence in sentences(text, realign_boundaries):
        yield tagger.tag(tokenizer.tokenize(sentence))

def xtagged_strings(text, realign_boundaries=True):
    """Returns a generator for a list of tagged sentences.

    Each tagged sentence contains words of the form 'word/tag' separated by single spaces.
    """
    tagger = get_tagger()
    tokenizer = get_tokenizer()
    for sentence in sentences(text, realign_boundaries):
        yield to_tagged_string(tagger.tag(tokenizer.tokenize(sentence)))

def tagged_tuples(text, realign_boundaries=True):
    """Returns a list of tagged tuple lists representing the tagged sentences in this text.

    Each tagged sentence consists of a list of tuples of the form (word, tag).
    """
    return list(xtagged_tuples(text, realign_boundaries))

def tagged_strings(text, realign_boundaries=True):
    """Returns a list of strings representing the tagged sentences in this text.

    Each tagged sentence contains words of the form 'word/tag' separated by single spaces.
    """
    return list(xtagged_strings(text, realign_boundaries))

def tag(sentence):
    tokenizer, tagger = get_tokenizer(), get_tagger()
    return tagger.tag(tokenizer.tokenize(sentence))

def tag_as_string(sentence):
    return to_tagged_string(tag(sentence))

def to_tagged_string(tagged_tuples):
    return ' '.join(nltk.tag.util.tuple2str(tup) for tup in tagged_tuples)

def words_with_tags(tagged_tuples, tag_list):
    """Returns a set consisting of all words in this tagged sentence that have any of the specified
    tags.
    """
    return set(word for (word, tag) in tagged_tuples if tag in tag_list)


def tag_freq(text, tag_list):
    """Returns an nltk.FreqDist representing the frequencies of every word that has one of these
    tags.

    Note that this method does not distinguish between different tags for the same word. Thus, if
    the word 'fleet' occurs 2 times as NN, and 3 times as JJ, the resulting FreqDist will assign a
    count of 5 to it. See tag_cond_freq() if you want to distinguish between the two.
    """
    fd = nltk.FreqDist()
    for tagged_sentence in xtagged_tuples(text):
        for word, tag in tagged_sentence:
            if tag in tag_list:
                fd.inc(word)
    return fd

def tag_cond_freq(text, tag_list):
    """Returns an nltk.FreqDist representing the frequencies of every word that has one of these
    tags.

    Note that this method distinguishes between different tags for the same word. Thus, if the word
    'fleet' occurs 2 times as NN, and 3 times as JJ, the resulting ConditionalFreqDist will not sum
    the two counts. Each will be stored under a separate condition, namely the associated tag.
    """
    cfd = nltk.ConditionalFreqDist()
    for tagged_sentence in xtagged_tuples(text):
        for word, tag in tagged_sentence:
            if tag in tag_list:
                cfd[tag].inc(word)
    return cfd
