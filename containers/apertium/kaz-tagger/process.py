# coding: utf-8

import sys

assert sys.version_info >= (3,4)

ROOT_DELIM = '_'
IGS_DELIM = '.'

class Tag(object):
    def __init__(self, root, ig):
        self.root = root
        self.ig = ig
        self.fine_ig = None
        self.coarse()
        self.xpos()
        self.conll_analysis()
    def __repr__(self):
        tabs_num = 1
        analysis = '"' + self.root + '"'
        if self.ig:
            for ig in self.ig:
                if ig.startswith('"'):
                    tabs_num += 1
                    analysis += '\n' + '\t'*tabs_num + ig.replace('.',' ')
                else:
                    analysis += ' ' + ig.replace('.',' ')
        else:
            analysis += ' unk'
        return analysis
    def __eq__(self, other):
        return self.root == other.root and self.ig == other.ig
    def __ne__(self, other):
        return self.root != other.root or self.ig != other.ig
    def __hash__(self):
        return hash((self.root, ) + tuple(self.ig))

    def coarse(self):
        cases = ['nom', 'gen', 'acc', 'abl', 'dat', 'ins', 'loc']
        for i in range(len(self.ig)):
            if self.ig[i].startswith('prn.pers'):
                if not self.fine_ig:
                    self.fine_ig = list(self.ig)
                if self.ig[i][-3:] in cases:
                    self.ig[i] = 'prn.pers.'+self.ig[i][-3:]
                else:
                    self.ig[i] = 'prn.pers'

    def fine(self):
        if self.fine_ig:
            self.ig = list(self.fine_ig)

    def xpos(self):
        if self.ig:
            first_ig_tags = self.ig[0].split('.')
        else:
            first_ig_tags = ['unk']
        return first_ig_tags[0]

    def conll_analysis(self):
        analysis = []
        feats = ''
        for ig in self.ig:
            if ig.startswith('"'):
                parts = ig.split('.')
                sub_root = parts[0].strip('"')
                sub_xpos = parts[1]
                sub_feats = '|'.join(parts[2:])
                analysis.append((sub_root, '_', sub_xpos, sub_feats if sub_feats!='' else '_'))
            else:
                feats += '|' + ig.replace('.', '|')

        clean_feats = feats[len(self.xpos()) + 1:].lstrip('|')
        analysis.insert(0, (self.root, '_', self.xpos(), clean_feats if clean_feats!='' else '_'))
        return analysis

def process_input(text):
    word_sequence = ['.']
    amb_sequence = []
    current_ambiguities = [Tag('.', ['sent'])]

    for line in text:
        if line.startswith('"'):
            amb_sequence.append(current_ambiguities)
            current_ambiguities = []
            word = line.strip()[2:-2]
            word_sequence.append(word)
        elif line.strip() != '' and line.startswith('\t'):
            line = list(line.strip())
            i = 1
            while line[i] != '"':
                if line[i] == ' ':
                    line[i] = ROOT_DELIM
                i += 1
            line = ''.join(line)
            line = line.split()
            root = line[0][1:-1]
            igs = []
            if root.startswith('*'):
                root = root[1:]
                #igs = ['UNK']
            else:
                current_ig = ''
                for elem in line[1:]:
                    if elem.startswith(('subst', 'attr', 'advl', 'ger_', 'gpr_', 'gna_', 'prc_', 'ger')):
                        igs.append(current_ig)
                        current_ig = elem
                    elif elem.startswith('"'):
                        igs.append(current_ig)
                        current_ig = elem
                    else:
                        current_ig += elem if current_ig == '' else IGS_DELIM+elem
                igs.append(current_ig)
            current_ambiguities.append(Tag(root, igs))
    amb_sequence.append(current_ambiguities)
    return word_sequence, amb_sequence