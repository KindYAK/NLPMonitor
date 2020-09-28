# coding: utf-8

import sys
import fileinput
import os
import process
import argparse

assert sys.version_info >= (3,4)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOTS_ARPA_FILE = os.path.join(BASE_DIR, 'roots.arpa')
IGS_ARPA_FILE = os.path.join(BASE_DIR, 'igs.arpa')

class Bigrams:
    def __init__(self, arpa_file):
        self.unigram_probs = {}
        self.backoff_weights = {}
        self.bigram_probs = {}

        f = open(arpa_file)

        #read unigram probabilities and backoff weights
        while '1-grams:' not in f.readline():
            continue
        while True:
            line = f.readline()
            line = line.strip()
            if line != '':
                line = line.split()
                log_prob, word = line[0], line[1]
                self.unigram_probs[word] = float(log_prob)
                if len(line) == 3:
                    backoff_log_weight = float(line[2])
                    self.backoff_weights[word] = backoff_log_weight
            else:
                break

        #read bigram probabilities
        while '2-grams:' not in f.readline():
            continue
        while True:
            line = f.readline()
            line = line.strip()
            if line != '':
                log_prob, word1, word2 = line.split()
                if word1 not in self.bigram_probs.keys():
                    self.bigram_probs[word1] = {word2: float(log_prob)}
                else:
                    self.bigram_probs[word1][word2] = float(log_prob)
            else:
                break

        f.close()

    def get_prob(self, word1, word2):
        prob = float('-inf')

        if word1 in self.bigram_probs.keys() and word2 in self.bigram_probs[word1].keys():
            prob = self.bigram_probs[word1][word2]
        elif word2 in self.unigram_probs.keys():
            prob = self.backoff_weights[word1] if word1 in self.backoff_weights.keys() else 0
            prob += self.unigram_probs[word2]
        else:
            prob = -100

        return prob

class Tagger:
    def __init__(self, roots_arpa, igs_arpa):
        self.root_bigrams = Bigrams(roots_arpa)
        self.ig_bigrams = Bigrams(igs_arpa)
        self.word_sequence = []
        self.amb_sequence = []
        self.path = []
        self.log_prob = float('-inf')

    def baseline_model(self, tag1, tag2):
        root_prob = self.root_bigrams.get_prob(tag1.root, tag2.root)
        ig_prob = 0
        for k in range(len(tag2.ig)):
            ig_prob += self.ig_bigrams.get_prob(tag1.ig[-1] if tag1.ig else 'UNK', tag2.ig[k])
        return root_prob + ig_prob

    def tag(self, text):
        self.word_sequence, self.amb_sequence = process.process_input(text)

        #Viterbi tagging
        delta = []
        delta.append({})
        delta[0][self.amb_sequence[0][0]] = 0

        psi = []
        psi.append({})

        for i in range(1, len(self.amb_sequence)):
            delta.append({})
            psi.append({})
            for tag in self.amb_sequence[i]:
                max_delta = float('-inf')
                max_tag = self.amb_sequence[i-1][0]
                for prev_tag in self.amb_sequence[i-1]:
                    cur_delta = delta[i-1][prev_tag] + self.baseline_model(prev_tag, tag)
                    if cur_delta > max_delta:
                        max_delta = cur_delta
                        max_tag = prev_tag
                delta[i][tag] = max_delta
                psi[i][tag] = max_tag

        self.path = [None]*len(self.amb_sequence)
        self.path[-1] = self.amb_sequence[-1][0]
        self.path[0] = self.amb_sequence[0][0]

        for j in range(len(self.amb_sequence)-2,0,-1):
            self.path[j] = psi[j+1][self.path[j+1]]

        self.log_prob = delta[-1][self.amb_sequence[-1][0]]

    def root_debug(self):
        print('root probabilites:')
        for i in range(1, len(self.path)):
            print('\tP(', self.path[i].root, '|', self.path[i-1].root, ') =', self.root_bigrams.get_prob(self.path[i-1].root, self.path[i].root))
        print('')
        return 0

    def ig_debug(self):
        print('IG probabilities')
        for i in range(1, len(self.path)):
            for k in range(len(self.path[i].ig)):
                print('\tP(', self.path[i].ig[k], '|', self.path[i-1].ig[-1], ') =', self.ig_bigrams.get_prob(self.path[i-1].ig[-1], self.path[i].ig[k]))
        print('')
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Disambiguate output of apertium-kaz.')
    parser.add_argument('--conll', action='store_true', help='CoNLL output format')
    parser.add_argument('--roots', action='store_true', help='Just roots')
    args = parser.parse_args()

    baseline_tagger = Tagger(ROOTS_ARPA_FILE, IGS_ARPA_FILE)

    text = []
    for line in fileinput.input(files='-'):
        if line.startswith('\t\t'):
            #subreadings: this actually works for any level
            text[-1] += ' ' + line.strip()
        elif not line.startswith('\n'):
            text.append(line.rstrip())
        else:
            #sentence is over - let's tag it
            baseline_tagger.tag(text)
            #now printing out ...
            #(firstly, need to return to finegrained tags)
            for tag in baseline_tagger.path: 
                tag.fine()
            if args.conll:
                # ... in CoNLL-format
                words = baseline_tagger.word_sequence
                path = baseline_tagger.path
                counter = 0
                for i in range(1, len(words)):
                    conll_analysis = path[i].conll_analysis()
                    if len(conll_analysis)==1:
                        counter += 1
                        print(counter, end='\t')
                        print(words[i], end='\t')
                        print('%s\t%s\t%s\t%s' % conll_analysis[0])
                    else:
                        counter_start = counter+1
                        counter_end = counter+len(conll_analysis)
                        print('%d-%d' % (counter_start, counter_end), end='\t')
                        print(words[i], end='\t')
                        print('_\t_\t_\t_')
                        for subreading in conll_analysis:
                            counter += 1
                            print(counter, end='\t')
                            print('_', end='\t')
                            print('%s\t%s\t%s\t%s' % subreading)
            elif args.roots:
                # ... or just roots
                roots = []
                for tag in baseline_tagger.path[1:]:
                    roots.append(tag.root)
                print(' '.join(roots))
            else:
                # ... or in CG-format
                for i in range(1, len(baseline_tagger.word_sequence)):
                    print('"<%s>"' % baseline_tagger.word_sequence[i])
                    print('\t%s' % baseline_tagger.path[i])
                print('')
            text[:] = []