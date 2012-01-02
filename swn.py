#! /usr/bin/env python
#! swn.py

from nltk.corpus import wordnet

class SentiWordNet(object):
    """
    Provides an interface to SentiWordNet, along with various bits of functionality.

    This class builds a map of SWN entries and exposes methods for getting at that information in a
    variety of different ways.

    Usage:
    swn_obj = SentiWordNet('../../research/resources/SentiWordNet/swn3.txt')
    print swn_obj.get_possible_synsets('able')
    print swn_obj.get_possible_synsets('easy', 'a')
    print swn_obj.most_frequent_synset('likely', 'r')
    """

    def __init__(self, swn_path):
        "Initialize an interface object from the given copy of SentiWordNet."
        # A map of unique keys (POS + offset) to SWNEntry objects.
        self._synset_dict = dict()
        with open(swn_path, 'r') as swn_file:
            for index, line in enumerate(swn_file):
                if not line.startswith('#'):
                    # Construct an SWNEntry object and add it to the synset
                    # dictionary.
                    try:
                        entry = SentiWordNet._parse_line(line)
                        self._synset_dict[entry.unique_key] = entry
                    except:
                        print "Error parsing SWN input file on line %d: %s" % (index+1, line)
                        raise

    @staticmethod
    def _parse_line(line):
        """
        Parses a single line of the SentiWordNet corpus and returns an SWNEntry object corresponding
        to it.
        """
        # Tokenize the line.
        synset_pos, synset_offset, pos_score, neg_score, synset_terms, gloss = line.split('\t')

        # We'll ignore the synset terms and gloss, because the NLTK synset
        # object stored in SWNEntry can get those from WordNet.

        return SWNEntry(synset_pos, int(synset_offset), float(pos_score), float(neg_score))


    def get_possible_synsets(self, word, pos=None):
        """
        Returns a list of SWNEntry objects corresponding to the possible synsets for the given word
        and part of speech.

        The part of speech is optional, but can be specified as either 'a' (adjective), 'n' (noun)
        or 'r' (adverb).
        """
        candidates = wordnet.synsets(word)
        return [self._synset_dict[SWNEntry.make_unique_key(synset.pos, synset.offset)] for synset in
                candidates]

    def most_frequent_synset(self, word, pos=None):
        "Returns the most frequent synset that corresponds to the given word and part of speech."
        possible_synsets = self.get_possible_synsets(word, pos)
        return possible_synsets[0] if len(possible_synsets) > 0 else None
        

class SWNEntry(object):
    """
    An entry in SentiWordNet, corresponding to a single synset and its attributes.

    These attributes include part-of-speech, synset ID, SWN scores, the lemmas of the synset, and
    its glosses.
    """
    def __init__(self, pos, synset_id, pos_score, neg_score):
        self._synset = wordnet._synset_from_pos_and_offset(pos, synset_id)
        self._pos_score = pos_score
        self._neg_score = neg_score
        self._obj_score = 1.0 - pos_score - neg_score
        self.unique_key = self._synset.pos + str(self._synset.offset)

    def get_offset(self):
        return self._synset.offset

    def get_pos(self):
        return self._synset.pos

    def get_scores(self):
        return self._pos_score, self._neg_score, self._obj_score

    @staticmethod
    def make_unique_key(pos, offset):
        return pos + str(offset)

    def __repr__(self):
        lemma_names = self._synset.lemma_names
        scores = [str(score) for score in self.get_scores()]
        return '<%s, %d, %s, %s>' % (self._synset.pos, self._synset.offset, ' '.join(lemma_names), ' '.join(scores))


if __name__ == '__main__':
    swn_obj = SentiWordNet('../../research/resources/SentiWordNet/swn3.txt')
    print swn_obj.most_frequent_synset('likely', 'r')
