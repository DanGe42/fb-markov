from __future__ import (
    absolute_import,
    division,
    print_function,
)

from collections import defaultdict
import random


class _CountDict(defaultdict):

    def __init__(self):
        super(_CountDict, self).__init__(int)
        self.total = 0


_BEGIN = object()
_END = None


class CondFreqDist(defaultdict):

    def __init__(self):
        super(CondFreqDist, self).__init__(_CountDict)

    def train(self, source):
        prev_word = _BEGIN
        for word in source:
            word = word.lower()
            self[prev_word][word] += 1
            self[prev_word].total += 1
            prev_word = word

    def count(self, word1, word2):
        word1, word2 = word1.lower(), word2.lower()
        if (word1 not in self) or (word2 not in self[word1]):
            return 0

        return self[word1][word2]

    def freq(self, word1, word2):
        return self.count(word1, word2) / float(self[word1].total)

    def generate_word(self, begin=_BEGIN):
        freq = random.random()
        for next_word in self.iterkeys():
            freq -= self.freq(begin, next_word)
            if freq < 0:
                return next_word

        return _END

    def generate_sequence(self, length, begin=_BEGIN):
        output = [] if begin is _BEGIN else [begin]

        # Subtract 1 because we are given 1 word already
        for _ in xrange(length - 1):
            word = self.generate_word(begin)

            # If the leading context word causes us to generate nothing, then
            # terminate the string.
            if word is None:
                return output
            output.append(word)

        return output
