import sys

# pools.py: Data Structure definitions for BIA/BIAPlus Models

__author__ = 'Andy Valenti'
__copyright__ = "Copyright 2016. Tufts University"

# Filtering word length artifacts
# Because words have different lengths, the overall activation will be different. In order to compensate,
# the letter to word connection weight is scaled by the word length, i.e. weight = c / |W|
c = 3.0         # connection weight
wd = 1.0        # weights for projections from words
lg = 1.0        # weights for projections from language nodes
w3 = c/3
w4 = c/4
w5 = c/5
si = -wd        # self-inhibitory weight for language
scsi = -lg      # self-inhibitory weight for ldt schema
rest = -0.1     # the resting activation level to which activations tend to settle in the absence of external input


# Defines an IAC Unit
# Input: list in the form [[[unit_name,pos] weight], [[unit_name,pos] weight] ... ]
#        unit_name is the name (a string) of the sending unit. Must be a valid key in a dict defining the pool of units
#        pos: indicates the position (or index) of the unit in a grouping of related units. Used in the lets pool to
#             indicate position of letter in a word; otherwise, pos = 0.
#        weight: the positive (excitatory) weight of negative (inhibitory) weight of the projection.
# Unit vales accessible via get and set methods:
#   Projection list exactly in the form as in Input. Caller can test for projections via isProjNone() method.
#   Activation, net input, and external input for THIS unit
class Unit:
    def __init__(self, projections=None, activation=None):
        if projections is None:
            self.projections = None
        else:
            self.projections = projections

        if activation is None:   # only for the default lexicon
            self.rest = rest
        else:                    # when auto loading, rest act is given
            self.rest = activation

        self.activation = self.rest
        self.ext_input = 0.0
        self.net_input = 0.0

    def isProjNone(self):
        if self.projections is None:
            return True

    def getNumProj(self):
        return len(self.projections)

    def getNetInput(self):
        return self.net_input

    def setNetInput(self, net_input):
        self.net_input = net_input
        return

    def getWeight(self,proj_index):
        if proj_index > len(self.projections):
            print("Error(getWeight): Out of Index")
            sys.exit(1)
        return self.projections[proj_index][1]

    def getProjList(self):
        return self.projections

    def setProjList(self,proj_list):
        self.projections = proj_list
        return

    def getProj(self,proj_index):
        if proj_index > len(self.projections):
            print("Error(getProj): Out of Index")
            sys.exit(1)
        return self.projections[proj_index][0]

    def getExtInput(self):
        return self.ext_input

    def setExtInput(self, ei):
        self.ext_input = ei
        return

    def getActivation(self):
        return self.activation

    def setWeight(self, proj_index, weight):
        if proj_index > len(self.projections):
            print("Error: Projections Out of Index")
            sys.exit(1)
        self.projections[proj_index][1] = weight
        return

    def setActivation(self, activation):
        self.activation = activation
        return

    def resetActivation(self):
        self.activation = self.rest
        return

    def getRest(self):
        return self.rest

    def setRest(self, new_rest):
        self.rest = new_rest
        return



'''
 Bilingual Lexicon
Spanish     English      1-Neighbors (not yet added)
azul (+)	blue    (+)
bien (+)	fine    (+)
rico (+)	rich    (+)
loco (+)	crazy   (+)
hijo (+)	son     (+)
hola (+)	hello   (+)
jugo (+)	juice   (+)
lado (+)	side    (+)  ride tide wide
            bide    (+)
            hide    (+)
taza (+)	cup (+)
cama (+)	bed (+)
gato (+)	cat  (+)
saco (+)	bag  (+)
vino (+)	wine (+)  dine line mine nine pine sine vine
piso (+)	floor (+)
'''

lang = {}
words = {}


#   The Inhibitory Control Proposal: Example for Language Switching in Reception
#   Based on Von Studnitz and Green(1997)
#   The presence of an external cue (color of bg on which letter string is presented) informs participants
#   of required language for decision
#   Two lexical decision schemas relate an output of of the lexical system (e.g. L1 tag present) to an LD response

schemas  = {'l1': [Unit([[['english',0],lg],[['cue1',0],lg],[['l2',0],scsi],[['l1',0],scsi]])],
            'l2': [Unit([[['spanish',0],lg],[['cue2',0],lg],[['l1',0],scsi],[['l2',0],scsi]])]}

#   Cue1 (Blue background) indicates L1 decision required
#   Cue2 (Yellow background) indicates L2 decision required
cues  = {'cue1': [Unit()],
         'cue2': [Unit()]}

#   Language Node pool.
#   In the BIA Mode, the language nodes serve 4 functions:
#   (1) Language tags (labels) indicating the language to which the word belongs
#   (2) Activation accumulators which could account for between-language priming effects
#   (3) Functional mechanism which modulates relative language activation, i.e. language filter rather than a switch
#   (4) Serves as a collection point for context pre-activation from outside the word recognition system

lang['spanish'] = [Unit([[['azul',0],wd],[['bien',0],wd],[['cama',0],wd],[['gato',0],wd],[['hijo',0],wd],
                        [['hola',0],wd],[['jugo',0],wd],[['lado',0],wd],[['loco',0],wd],[['piso',0],wd],[['rico',0],wd],
                        [['saco',0],wd],[['taza',0],wd],[['vino',0],wd],[['l1',0],scsi]
                         ])]

lang['english'] = [Unit([[['bag',0],wd],[['bed',0],wd],[['bide',0],wd],[['blue',0],wd],[['cat',0],wd],[['chair',0],wd],
                        [['crazy',0],wd],[['cup',0],wd],[['dog',0],wd],[['fine',0],wd],[['floor',0],wd],[['hello',0],wd],
                        [['hide',0],wd],[['juice',0],wd],[['rich',0],wd],[['side',0],wd],[['son',0],wd],
                        [['table',0],wd], [['wine',0],wd],[['l2',0],scsi]
                         ])]
#   Pool Architecture.
#   Words are limited to 5 letters per word.  As a result, there are five groups of 26 input letters per word.
#   This is represented as a dictionary with 26 keys, 'a':'z' with each entry consisting of a nested list.
#   At the outermost level, there are 5 sublists, 1 per letter position. Each position defines
#   a  processing 'unit' and some may be empty (see below).
#   Each unit is initialized with a list containing zero or more 'projection' sublists, one for each connection
#   from a sending unit in a pool. Projections may be from any pool, including itself.
#   Each projection sublist contains another sublist with the sending unit key followed by the position in the
#   corresponding dictionary entry for the key. At present, this is only used for the lets dictionary (pool) and
#   projections from other pools have a 0 position.
#   The [key,position] pair is followed by the weight of the projection; this completes a sublist projection.
#   Word to letter excitation: Each word unit has excitatory connections to the units for all tof the ltters in the word.
#   For example, there is an excitatory connection from $TAKE$ to $T$ in the first position, to $A$ in the second, etc.

lets =     {'a': [Unit([[['azul',0],w4]]),Unit([[['cama',0],w4],[['gato',0],w4],[['lado',0],w4],[['table',0],w5],
                  [['bag',0],w3],[['cat',0],w3],[['saco',0],w4],[['taza',0],w4]]),
                  Unit([[['chair',0],w5],[['crazy',0],w5]]),Unit([[['cama',0],w4],[['hola',0],w4],
                  [['taza',0],w4]]),Unit()],
            'b': [Unit([[['bag',0],w3],[['bed',0],w3],[['bide',0],w4],[['blue',0],w4],[['bien',0],w4]]), Unit(),
                  Unit([[['table',0],w5]]),Unit(), Unit()],
            'c': [Unit([[['cama',0],w4],[['cat',0],w3],[['chair',0],w5],[['crazy',0],w5],[['cup',0],w3]]), Unit(),
                  Unit([[['loco',0],w4],[['rich',0],w4],[['rico',0],w4],[['saco',0],w4]]), Unit([[['juice',0],w5]]),
                  Unit()],
            'd': [Unit([[['dog',0],w3]]), Unit(),Unit([[['bed',0],w3],[['bide',0],w4],[['hide',0],w4],
                  [['lado',0],w4],[['side',0],w4]]),Unit(),Unit()],
            'e': [Unit(),Unit([[['bed',0],w3],[['hello',0],w5]]),Unit([[['bien',0],w4]]),
                  Unit([[['bide',0],w4],[['blue',0],w4],[['fine',0],w4],[['hide',0],w4],[['wine',0],w4],
                  [['side',0],w4]]),Unit([[['table',0],w5],[['juice',0],w5]])],
            'f': [Unit([[['fine',0],w4],[['floor',0],w5]]), Unit(), Unit(), Unit(), Unit()],
            'g': [Unit([[['gato',0],w4]]),Unit(),Unit([[['bag',0],w3],[['dog',0],w3],[['jugo',0],w4]]), Unit(),Unit()],
            'h': [Unit([[['hello',0],w5],[['hide',0],w4],[['hijo',0],w4],[['hola',0],w4]]),Unit([[['chair',0],w5]]),
                  Unit(),Unit([[['rich',0],w4]]),Unit()],
            'i': [Unit(),Unit([[['bide',0],w4],[['bien',0],w4],[['fine',0],w4],[['hide',0],w4],[['hijo',0],w4],
                  [['piso',0],w4],[['side',0],w4],[['rich',0],w4],[['rico',0],w4],[['vino',0],w4],[['wine',0],w4]]),
                  Unit([[['juice',0],w5]]), Unit([[['chair',0],w5]]), Unit()],
            'j': [Unit([[['jugo',0],w4],[['juice',0],w5]]), Unit(), Unit([[['hijo',0],w4]]), Unit(), Unit()],
            'k': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'l': [Unit([[['lado',0],w4],[['loco',0],w4]]),Unit([[['blue',0],w4],[['floor',0],w5]]),
                  Unit([[['hello',0],w5],[['hola',0],w4]]), Unit([[['table', 0],w5],[['hello',0],w5],[['azul',0],w4]]),
                  Unit()],
            'm': [Unit(), Unit(), Unit([[['cama',0],w4]]), Unit(), Unit()],
            'n': [Unit(), Unit(), Unit([[['fine',0],w4],[['son',0],w3],[['vino',0],w4],[['wine',0],w4]]),
                  Unit([[['bien',0],w4]]),Unit()],
            'o': [Unit(),Unit([[['dog',0],w3],[['hola',0],w4],[['loco',0],w4],[['son',0],w3]]),Unit([[['floor',0],w5]]),
                  Unit([[['floor',0],w5],[['gato',0],w4],[['hijo',0],w4],[['jugo',0],w4],[['lado',0],w4],[['loco',0],w4],
                       [['piso',0],w4],[['rico',0],w4],[['saco',0],w4],[['vino',0],w4]]),Unit([[['hello',0],w5]])],
            'p': [Unit([[['piso',0],w4]]), Unit(), Unit([[['cup',0],w3]]), Unit(),Unit()],
            'q': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'r': [Unit([[['rich',0],w4],[['rico',0],w4]]), Unit([[['crazy',0],w5]]),Unit(),Unit(),
                  Unit([[['chair',0],w5],[['floor',0],w5]])],
            's': [Unit([[['saco',0],w4],[['side',0],w4],[['son',0],w3]]), Unit(), Unit([[['piso',0],w4]]),
                  Unit(), Unit()],
            't': [Unit([[['table',0],w5],[['taza',0],w4]]), Unit(), Unit([[['cat',0],w3],[['gato',0],w4]]),
                  Unit(), Unit()],
            'u': [Unit(), Unit([[['cup',0],w3],[['jugo',0],w4]]),Unit([[['blue',0],w4],[['azul',0],w4]]),Unit(),Unit()],
            'v': [Unit([[['vino',0],w4]]), Unit(), Unit(), Unit(), Unit()],
            'w': [Unit([[['wine',0],w4]]), Unit(), Unit(), Unit(), Unit()],
            'x': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'y': [Unit(), Unit(), Unit(), Unit(), Unit([[['crazy',0],w5]])],
            'z': [Unit(), Unit([[['azul',0],w4]]), Unit([[['taza',0],w4]]), Unit([[['crazy',0],w5]]), Unit()]
            }
'''
            'B': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'L': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'A': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'N': [Unit(), Unit(), Unit(), Unit(), Unit()],
            'K': [Unit(), Unit(), Unit(), Unit(), Unit()]
'''

#
#  *******************************************WORDS******************************************************
#   Self-inhibitory connections for Words


azul_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

bide_si = [[['bag',0],si],[['bed',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

bien_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

bag_si =  [[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['hide',0],si],[['juice',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

bed_si =   [[['bag',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

blue_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['cat',0],si],[['chair',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

cama_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

cat_si =  [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['chair',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

chair_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['crazy',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

crazy_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

cup_si =  [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

dog_si =  [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

fine_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['floor',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

floor_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['hello',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

gato_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si], [['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

hello_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['juice',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

hide_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

hijo_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

hola_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

jugo_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

juice_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],[['hide',0],si],
           [['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

lado_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

loco_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

piso_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['loco',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

rich_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

rico_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

saco_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],
           [['taza',0],si],[['vino',0],si]]

side_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

son_si =  [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

table_si =[[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]

taza_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],
           [['saco',0],si],[['vino',0],si]]

vino_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],[['wine',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],
           [['hola',0],si],[['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],
           [['saco',0],si],[['taza',0],si]]

wine_si = [[['bag',0],si],[['bed',0],si],[['bide',0],si],[['blue',0],si],[['cat',0],si],[['chair',0],si],
           [['crazy',0],si],[['cup',0],si],[['dog',0],si],[['fine',0],si],[['floor',0],si],[['hello',0],si],
           [['hide',0],si],[['juice',0],si],[['rich',0],si],[['side',0],si],[['son',0],si],[['table',0],si],
           [['azul',0],si],[['bien',0],si],[['cama',0],si],[['gato',0],si],[['hijo',0],si],[['hola',0],si],
           [['jugo',0],si],[['lado',0],si],[['loco',0],si],[['piso',0],si],[['rico',0],si],[['saco',0],si],
           [['taza',0],si],[['vino',0],si]]


#   ************************************WORDS POOL (as a dictionary)***************************************
#   Projections are from the letter pool.
#   Letter to word excitation: Each letter unit has excitatory connections to each of the units standing for a word that
#   contains the letter in the corresponding position. Weights are positive. For readability, these connections
#   are the first sublist in each word's unit.
#
#   Letter to word inhibition: Each letter unit has inhibitory connections to each of the units standing for a word that
#   does not contain the letter in the corresponding position. Weights are negative.

words['non-word'] = [Unit(activation=rest)]

words['azul'] = [Unit([[['a',0],w4],[['z',1],w4],[['u',2],w4],[['l',3],w4],
                      [['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + azul_si)]

words['bien'] = [Unit([[['b',0],w4],[['i',1],w4],[['e',2],w4],[['n',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + bien_si)]

words['bag'] = [Unit([[['b',0],w3],[['a',1],w3],[['g',2],w3],
                     [['a',0],-w3],[['a',2],-w3],
                     [['b',1],-w3],[['b',2],-w3],
                     [['c',0],-w3],[['c',1],-w3],[['c',2],-w3],
                     [['d',0],-w3],[['d',1],-w3],[['d',2],-w3],
                     [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                     [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                     [['g',0],-w3],[['g',1],-w3],
                     [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                     [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                     [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                     [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                     [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                     [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                     [['o',0],-w3],[['o',1],-w3],[['o',2],-w3],
                     [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                     [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                     [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                     [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                     [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                     [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                     [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                     [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                     [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                     [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                     [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                      ] + bag_si)]

words['bed'] = [Unit([[['b',0],w3],[['e',1],w3],[['d',2],w3],
                     [['a',0],-w3],[['a',1],-w3],[['a',2],-w3],
                     [['b',1],-w3],[['b',2],-w3],
                     [['c',0],-w3],[['c',1],-w3],[['c',2],-w3],
                     [['d',0],-w3],[['d',1],-w3],
                     [['e',0],-w3],[['e',2],-w3],
                     [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                     [['g',0],-w3],[['g',1],-w3],[['g',2],-w3],
                     [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                     [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                     [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                     [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                     [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                     [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                     [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                     [['o',0],-w3],[['o',1],-w3],[['o',2],-w3],
                     [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                     [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                     [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                     [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                     [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                     [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                     [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                     [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                     [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                     [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                     [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                      ] + bed_si)]

words['bide'] = [Unit([[['b',0],w4],[['i',1],w4],[['d',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + bide_si)]

words['blue'] = [Unit([[['b',0],w4],[['l',1],w4],[['u',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + blue_si)]

words['cama'] = [Unit([[['c',0],w4],[['a',1],w4],[['m',2],w4],[['a',3],w4],
                      [['a',0],-w4],[['a',2],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + cama_si)]

words['cat'] = [Unit([[['c',0],w3],[['a',1],w3],[['t',2],w3],
                     [['a',0],-w3],[['a',2],-w3],
                     [['b',0],-w3],[['b',1],-w3],[['b',2],-w3],
                     [['c',1],-w3],[['c',2],-w3],
                     [['d',0],-w3],[['d',1],-w3],[['d',2],-w3],
                     [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                     [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                     [['g',0],-w3],[['g',1],-w3],[['g',2],-w3],
                     [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                     [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                     [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                     [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                     [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                     [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                     [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                     [['o',0],-w3],[['o',1],-w3],[['o',2],-w3],
                     [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                     [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                     [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                     [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                     [['t',0],-w3],[['t',1],-w3],
                     [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                     [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                     [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                     [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                     [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                     [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                      ] + cat_si)]

words['chair'] = [Unit([[['c',0],w5],[['h',1],w5],[['a',2],w5],[['i',3],w5],[['r',4],w5],
                       [['a',0],-w5],[['a',1],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],[['e',4],-w5],
                       [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',0],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',4],-w5],
                       [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',1],-w5],[['l',2],-w5],[['l',3],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],[['o',4],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                        ] + chair_si)]

words['crazy'] = [Unit([[['c',0],w5],[['r',1],w5],[['a',2],w5],[['z',3],w5],[['y',4],w5],
                       [['a',0],-w5],[['a',1],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],[['e',4],-w5],
                       [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',0],-w5],[['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',3],-w5],[['i',4],-w5],
                       [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',1],-w5],[['l',2],-w5],[['l',3],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],[['o',4],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',2],-w5],[['r',3],-w5],[['r',4],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',4],-w5]
                        ] + crazy_si)]

words['cup'] = [Unit([[['c',0],w3],[['u',1],w3],[['p',2],w3],
                     [['a',0],-w3],[['a',1],-w3],[['a',2],-w3],
                     [['b',0],-w3],[['b',1],-w3],[['b',2],-w3],
                     [['c',1],-w3],[['c',2],-w3],
                     [['d',0],-w3],[['d',1],-w3],[['d',2],-w3],
                     [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                     [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                     [['g',0],-w3],[['g',1],-w3],[['g',2],-w3],
                     [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                     [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                     [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                     [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                     [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                     [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                     [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                     [['o',0],-w3],[['o',1],-w3],[['o',2],-w3],
                     [['p',0],-w3],[['p',1],-w3],
                     [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                     [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                     [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                     [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                     [['u',0],-w3],[['u',2],-w3],
                     [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                     [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                     [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                     [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                     [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                      ] + cup_si)]
words['dog'] =   [Unit([[['d',0],w3],[['o',1],w3],[['g',2],w3],
                       [['a',0],-w3],[['a',1],-w3],[['a',2],-w3],
                       [['b',0],-w3],[['b',1],-w3],[['b',2],-w3],
                       [['c',0],-w3],[['c',1],-w3],[['c',2],-w3],
                       [['d',1],-w3],[['d',2],-w3],
                       [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                       [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                       [['g',0],-w3],[['g',1],-w3],
                       [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                       [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                       [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                       [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                       [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                       [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                       [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                       [['o',0],-w3],[['o',2],-w3],
                       [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                       [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                       [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                       [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                       [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                       [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                       [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                       [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                       [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                       [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                       [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                        ] + dog_si)]

words['fine'] = [Unit([[['f',0],w4],[['i',1],w4],[['n',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + fine_si)]

words['floor'] = [Unit([[['f',0],w5],[['l',1],w5],[['o',2],w5],[['o',3],w5],[['r',4],w5],
                       [['a',0],-w5],[['a',1],-w5],[['a',2],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',0],-w5],[['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],[['e',4],-w5],
                       [['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',0],-w5],[['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',3],-w5],[['i',4],-w5],
                       [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',2],-w5],[['l',3],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',4],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                        ] + floor_si)]

words['gato'] = [Unit([[['g',0],w4],[['a',1],w4],[['t',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + gato_si)]

words['hello'] = [Unit([[['h',0],w5],[['e',1],w5],[['l',2],w5],[['l',3],w5],[['o',4],w5],
                       [['a',0],-w5],[['a',1],-w5],[['a',2],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',0],-w5],[['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',2],-w5],[['e',3],-w5],[['e',4],-w5],
                       [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',3],-w5],[['i',4],-w5],
                       [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',1],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],[['r',4],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                        ] + hello_si)]

words['hide'] = [Unit([[['h',0],w4],[['i',1],w4],[['d',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + hide_si)]

words['hijo'] = [Unit([[['h',0],w4],[['i',1],w4],[['j',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + hijo_si)]

words['hola'] = [Unit([[['h',0],w4],[['o',1],w4],[['l',2],w4],[['a',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + hola_si)]

words['jugo'] = [Unit([[['j',0],w4],[['u',1],w4],[['g',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',3],-w4],
                      [['h',1],-w4],[['h',2],-w4],[['h',3],-w4],[['h',4],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + jugo_si)]

words['juice'] = [Unit([[['j',0],w5],[['u',1],w5],[['i',2],w5],[['c',3],w5],[['e',4],w5],
                       [['a',0],-w5],[['a',1],-w5],[['a',2],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',0],-w5],[['c',1],-w5],[['c',2],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],
                       [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',0],-w5],[['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',3],-w5],[['i',4],-w5],
                       [['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',1],-w5],[['l',2],-w5],[['l',3],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],[['o',4],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],[['r',4],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                        ] + juice_si)]

words['lado'] = [Unit([[['l',0],w4],[['a',1],w4],[['d',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + lado_si)]

words['loco'] = [Unit([[['l',0],w4],[['o',1],w4],[['c',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + loco_si)]

words['piso'] = [Unit([[['p',0],w4],[['i',1],w4],[['s',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',2],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + piso_si)]

words['rich'] = [Unit([[['r',0],w4],[['i',1],w4],[['c',2],w4],[['h',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + rich_si)]


words['rico'] = [Unit([[['r',0],w4],[['i',1],w4],[['c',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',2],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + rico_si)]

words['saco'] = [Unit([[['s',0],w4],[['a',1],w4],[['c',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + saco_si)]

words['side'] = [Unit([[['s',0],w4],[['i',1],w4],[['d',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + side_si)]

words['son']    = [Unit([[['s',0],w3],[['o',1],w3],[['n',2],w3],
                        [['a',0],-w3],[['a',1],-w3],[['a',2],-w3],
                        [['b',0],-w3],[['b',1],-w3],[['b',2],-w3],
                        [['c',0],-w3],[['c',1],-w3],[['c',2],-w3],
                        [['d',0],-w3],[['d',1],-w3],[['d',2],-w3],
                        [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                        [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                        [['g',0],-w3],[['g',1],-w3],[['g',2],-w3],
                        [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                        [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                        [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                        [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                        [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                        [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                        [['n',0],-w3],[['n',1],-w3],
                        [['o',0],-w3],[['o',2],-w3],
                        [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                        [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                        [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                        [['s',1],-w3],[['s',2],-w3],
                        [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                        [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                        [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                        [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                        [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                        [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                        [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                         ] + son_si)]

words['table'] = [Unit([[['t',0],w5],[['a',1],w5],[['b',2],w5],[['l',3],w5],[['e',4],w5],
                       [['a',0],-w5],[['a',2],-w5],[['a',3],-w5],[['a',4],-w5],
                       [['b',0],-w5],[['b',1],-w5],[['b',3],-w5],[['b',4],-w5],
                       [['c',0],-w5],[['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                       [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                       [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],
                       [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                       [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                       [['h',0],-w5],[['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                       [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',3],-w5],[['i',4],-w5],
                       [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                       [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                       [['l',0],-w5],[['l',1],-w5],[['l',2],-w5],[['l',4],-w5],
                       [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                       [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                       [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],[['o',4],-w5],
                       [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                       [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                       [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],[['r',4],-w5],
                       [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                       [['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                       [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                       [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                       [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                       [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                       [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                       [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                        ] + table_si)]

words['taza'] = [Unit([[['t',0],w4],[['a',1],w4],[['z',2],w4],[['a',3],w4],
                      [['a',0],-w4],[['a',2],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',3],-w4]
                       ] + taza_si)]

words['vino'] = [Unit([[['v',0],w4],[['i',1],w4],[['n',2],w4],[['o',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + vino_si)]

words['wine'] = [Unit([[['w',0],w4],[['i',1],w4],[['n',2],w4],[['e',3],w4],
                      [['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ] + wine_si)]

#words['BLANK'] = [Unit()]  # used for blank cycle processing

# *************************** TEMPLATE TO ALLOW AUTO-PROCESSING OF NEW WORD READ-IN FROM A FILE ********************
#   Steps to add a new word to Word pool
#   1. copy word3,word4, or word5 template and make new_word projections list
#   2. copy word_si_template, replacing 'new_word" with corresponding string literal of new word
#   3. in new_word proj list, replace the inhib weight with the excit weight in each letter unit corresponding to the
#      letter pos in the new_word
#   4a Scan through all the words in the pool and build a self-inhibitory list and append to new_word proj list
#   4b While scanning words in pool (step 4a), append copied word_si_template to its unit
#   5. add new dictionary entry to word pool: key = new word string, value = new_word proj list
#
#   Steps to add a new word to Lets pool
#   1. copy wordn_lets_template, replacing 'new_word' with string literal of word to be added
#   1. For each let in new word, find corresponding let and let position unit in lets pool
#      and append wordn_lets_template
#
#   Steps to add new word to Lang pool
#   1. copy word_lang_template, replacing 'new_word' with string literal of new word
#   1. append copied word_lang_template to proj list in appropriate lang pool


lets_word_template = {}

lets_word_template[3] = [[['a',0],-w3],[['a',1],-w3],[['a',2],-w3],
                      [['b',0],-w3],[['b',1],-w3],[['b',2],-w3],
                      [['c',0],-w3],[['c',1],-w3],[['c',2],-w3],
                      [['d',0],-w3],[['d',1],-w3],[['d',2],-w3],
                      [['e',0],-w3],[['e',1],-w3],[['e',2],-w3],
                      [['f',0],-w3],[['f',1],-w3],[['f',2],-w3],
                      [['g',0],-w3],[['g',1],-w3],[['g',2],-w3],
                      [['h',0],-w3],[['h',1],-w3],[['h',2],-w3],
                      [['i',0],-w3],[['i',1],-w3],[['i',2],-w3],
                      [['j',0],-w3],[['j',1],-w3],[['j',2],-w3],
                      [['k',0],-w3],[['k',1],-w3],[['k',2],-w3],
                      [['l',0],-w3],[['l',1],-w3],[['l',2],-w3],
                      [['m',0],-w3],[['m',1],-w3],[['m',2],-w3],
                      [['n',0],-w3],[['n',1],-w3],[['n',2],-w3],
                      [['o',0],-w3],[['o',1],-w3],[['o',2],-w3],
                      [['p',0],-w3],[['p',1],-w3],[['p',2],-w3],
                      [['q',0],-w3],[['q',1],-w3],[['q',2],-w3],
                      [['r',0],-w3],[['r',1],-w3],[['r',2],-w3],
                      [['s',0],-w3],[['s',1],-w3],[['s',2],-w3],
                      [['t',0],-w3],[['t',1],-w3],[['t',2],-w3],
                      [['u',0],-w3],[['u',1],-w3],[['u',2],-w3],
                      [['v',0],-w3],[['v',1],-w3],[['v',2],-w3],
                      [['w',0],-w3],[['w',1],-w3],[['w',2],-w3],
                      [['x',0],-w3],[['x',1],-w3],[['x',2],-w3],
                      [['y',0],-w3],[['y',1],-w3],[['y',2],-w3],
                      [['z',0],-w3],[['z',1],-w3],[['z',2],-w3]
                       ]


lets_word_template[4] = [[['a',0],-w4],[['a',1],-w4],[['a',2],-w4],[['a',3],-w4],
                      [['b',0],-w4],[['b',1],-w4],[['b',2],-w4],[['b',3],-w4],
                      [['c',0],-w4],[['c',1],-w4],[['c',2],-w4],[['c',3],-w4],
                      [['d',0],-w4],[['d',1],-w4],[['d',2],-w4],[['d',3],-w4],
                      [['e',0],-w4],[['e',1],-w4],[['e',2],-w4],[['e',3],-w4],
                      [['f',0],-w4],[['f',1],-w4],[['f',2],-w4],[['f',3],-w4],
                      [['g',0],-w4],[['g',1],-w4],[['g',2],-w4],[['g',3],-w4],
                      [['h',0],-w4],[['h',1],-w4],[['h',2],-w4],[['h',3],-w4],
                      [['i',0],-w4],[['i',1],-w4],[['i',2],-w4],[['i',3],-w4],
                      [['j',0],-w4],[['j',1],-w4],[['j',2],-w4],[['j',3],-w4],
                      [['k',0],-w4],[['k',1],-w4],[['k',2],-w4],[['k',3],-w4],
                      [['l',0],-w4],[['l',1],-w4],[['l',2],-w4],[['l',3],-w4],
                      [['m',0],-w4],[['m',1],-w4],[['m',2],-w4],[['m',3],-w4],
                      [['n',0],-w4],[['n',1],-w4],[['n',2],-w4],[['n',3],-w4],
                      [['o',0],-w4],[['o',1],-w4],[['o',2],-w4],[['o',3],-w4],
                      [['p',0],-w4],[['p',1],-w4],[['p',2],-w4],[['p',3],-w4],
                      [['q',0],-w4],[['q',1],-w4],[['q',2],-w4],[['q',3],-w4],
                      [['r',0],-w4],[['r',1],-w4],[['r',2],-w4],[['r',3],-w4],
                      [['s',0],-w4],[['s',1],-w4],[['s',2],-w4],[['s',3],-w4],
                      [['t',0],-w4],[['t',1],-w4],[['t',2],-w4],[['t',3],-w4],
                      [['u',0],-w4],[['u',1],-w4],[['u',2],-w4],[['u',3],-w4],
                      [['v',0],-w4],[['v',1],-w4],[['v',2],-w4],[['v',3],-w4],
                      [['w',0],-w4],[['w',1],-w4],[['w',2],-w4],[['w',3],-w4],
                      [['x',0],-w4],[['x',1],-w4],[['x',2],-w4],[['x',3],-w4],
                      [['y',0],-w4],[['y',1],-w4],[['y',2],-w4],[['y',3],-w4],
                      [['z',0],-w4],[['z',1],-w4],[['z',2],-w4],[['z',3],-w4]
                       ]

lets_word_template[5] = [[['a',0],-w5],[['a',1],-w5],[['a',2],-w5],[['a',3],-w5],[['a',4],-w5],
                      [['b',0],-w5],[['b',1],-w5],[['b',2],-w5],[['b',3],-w5],[['b',4],-w5],
                      [['c',0],-w5],[['c',1],-w5],[['c',2],-w5],[['c',3],-w5],[['c',4],-w5],
                      [['d',0],-w5],[['d',1],-w5],[['d',2],-w5],[['d',3],-w5],[['d',4],-w5],
                      [['e',0],-w5],[['e',1],-w5],[['e',2],-w5],[['e',3],-w5],[['e',4],-w5],
                      [['f',0],-w5],[['f',1],-w5],[['f',2],-w5],[['f',3],-w5],[['f',4],-w5],
                      [['g',0],-w5],[['g',1],-w5],[['g',2],-w5],[['g',3],-w5],[['g',4],-w5],
                      [['h',0],-w5],[['h',1],-w5],[['h',2],-w5],[['h',3],-w5],[['h',4],-w5],
                      [['i',0],-w5],[['i',1],-w5],[['i',2],-w5],[['i',3],-w5],[['i',4],-w5],
                      [['j',0],-w5],[['j',1],-w5],[['j',2],-w5],[['j',3],-w5],[['j',4],-w5],
                      [['k',0],-w5],[['k',1],-w5],[['k',2],-w5],[['k',3],-w5],[['k',4],-w5],
                      [['l',0],-w5],[['l',1],-w5],[['l',2],-w5],[['l',3],-w5],[['l',4],-w5],
                      [['m',0],-w5],[['m',1],-w5],[['m',2],-w5],[['m',3],-w5],[['m',4],-w5],
                      [['n',0],-w5],[['n',1],-w5],[['n',2],-w5],[['n',3],-w5],[['n',4],-w5],
                      [['o',0],-w5],[['o',1],-w5],[['o',2],-w5],[['o',3],-w5],[['o',4],-w5],
                      [['p',0],-w5],[['p',1],-w5],[['p',2],-w5],[['p',3],-w5],[['p',4],-w5],
                      [['q',0],-w5],[['q',1],-w5],[['q',2],-w5],[['q',3],-w5],[['q',4],-w5],
                      [['r',0],-w5],[['r',1],-w5],[['r',2],-w5],[['r',3],-w5],[['r',4],-w5],
                      [['s',0],-w5],[['s',1],-w5],[['s',2],-w5],[['s',3],-w5],[['s',4],-w5],
                      [['t',0],-w5],[['t',1],-w5],[['t',2],-w5],[['t',3],-w5],[['t',4],-w5],
                      [['u',0],-w5],[['u',1],-w5],[['u',2],-w5],[['u',3],-w5],[['u',4],-w5],
                      [['v',0],-w5],[['v',1],-w5],[['v',2],-w5],[['v',3],-w5],[['v',4],-w5],
                      [['w',0],-w5],[['w',1],-w5],[['w',2],-w5],[['w',3],-w5],[['w',4],-w5],
                      [['x',0],-w5],[['x',1],-w5],[['x',2],-w5],[['x',3],-w5],[['x',4],-w5],
                      [['y',0],-w5],[['y',1],-w5],[['y',2],-w5],[['y',3],-w5],[['y',4],-w5],
                      [['z',0],-w5],[['z',1],-w5],[['z',2],-w5],[['z',3],-w5],[['z',4],-w5]
                       ]


# word proj to lets template
word_lets_template = {3: [['new_word',0],w3], 4: [['new_word',0],w4], 5: [['new_word',0],w5]}


word_si_template = [['new_word',0],si]  # append this to end of every word in pool
word_lang_template = [['new_word',0],wd]


