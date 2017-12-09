#!/usr/bin/python
import csv
import math
import operator
import fileinput, os, sys, re, copy
import matplotlib.pyplot as plt
from IA_pools import words, lets, lang, schemas, cues, Unit
from IA_pools import lets_word_template, word_lets_template, word_si_template, word_lang_template
from itertools import cycle

#   biaIC.py: Implementation of the Bilingual Interactive Activation (BIA) model of word recognition incorporating
#   Inhibitory Control
#  (Green, 1998)
#  (Dijkstra & van Heuven, 2002)

__author__ = 'Andy Valenti'
__copyright__ = "Copyright 2016. Tufts University"


#   Global variables
#   variables for scripting

e = 0.0002      # epsilon value. During script processing we stop cycling when activations change by this amount.
ncycles = 0    # number of cycles. It is used to hold value from script.
item_script = ''       # used by runCycle to cycle until item settles within e
list_script = []       # used to process a list of items to display; build from the script
script_mode = False
blankCycle = False      # used to recognize when word is a blank

# model variables
verbose = False
input_word = ''
console_message = ''
mode = 'Ready'
cycleno = 0         # current cycle; it is reset by reset()
display_cols = 3.0  # The number of columns in a subplot of the word activations. Needs to be adjusted as words are added
trial = 1           # counts the number of times the model has been reset/initialized. It is never reset by the model.
act_dataset = []    # accumulates word activations
act_langset = []    # accumulates language node activations
act_schemaset = []  # accumulates schema node activations
exit_flag = False
log = []
logging = False
pool_list = [lets,words,lang,schemas,cues]
a2z = 'abcdefghijklmnopqrstuvwxyz'
max_subplots = 30   # The most subplots that can be reasonably displayed simultaneously

#   Parameter definitions (from Explorations in Parallel Distributed Processing: A Handbook of Models,
#   Programs, and Exercises. James McClelland. July 28th, 2015)

max = 1.0       # maximum activation parameter
min = -0.2      # minimum activation parameter
rest = -0.1     # the resting activation level to which activations tend to settle in the absence of external input
decay = 0.1    # the decay rate parameter, which determines the strength of the tendency to return to resting level
estr = 0.4      # this parameter stands for the strength of external input (inputs from outside the network). It scales
                # the influence of external signals relative to internally generated inputs to units
alpha = 0.1     # this parameter scales the strength of the excitatory input to units from other units in the network
gamma = 0.1     # this parameter scales the strength of the inhibitory input to units from other units in the network
ncycles_default = 10   # default number of cycles
params = {'max': max, 'min': min, 'rest': rest, 'decay': decay, 'estr': estr, 'alpha': alpha, 'gamma': gamma,
          'ncycles': ncycles_default}

#  Function Definitions


#   builds a list of keys for a pool, used for charting axis
def build_keys(pool):
    keys = []
    for key in pool:
        keys.append(key)
    list.sort(keys)
    return keys


#
#   Creates the x values for a dataset of size dataset_size, where each record in the set corresponds
#   to r update cycles of the mode
def genx_axis(r, dataset_size):
    return [x * r for x in range(1, dataset_size)]


# Reset completely restarts the model.
# Need to add code to reset each unit to default activation, rest, net-input, and ext_input values
# NOTES: Does NOT reset the params
def reset():
    global trial, act_dataset, act_langset, act_schemaset, verbose, cycleno, console_message, mode,\
        input_word, params, log, blankCycle, script_mode

    def reset_pool(pool):
        for key, unit_list in pool.iteritems():
            for unit in unit_list:
                unit.resetActivation()
                unit.setExtInput(0.0)
                unit.setNetInput(0.0)
        return
    # reset each unit to default activation, rest, net-input, and ext_input values
    reset_pool(lets)
    reset_pool(words)
    reset_pool(lang)
    reset_pool(cues)
    reset_pool(schemas)
    trial += 1
    cycleno = 0
    verbose = False
    act_dataset = []
    act_langset = []
    act_schemaset = []
    console_message = ''
    mode = 'Ready'
    input_word = ''
    blankCycle = False
    script_mode = False
    log = []
    return


#  Cycle(act_dataset) cycles through the pools, collecting the net input of each unit and then updating the unit
#  activation
#  Input: act_dataset is a list which contains a record of a pool's activation for each update across cycles.
#  It is hard-coded to the words pool.
#  Control variables: ncycles controls the number of iterations of the net input & update cycle
#                     verbose controls printing of each update cycle to the standard output (console)
#  Returns: act_dataset, act_langset appended with the last ncycles activation records for each unit in the pool
def cycle_pool():
    global verbose, cycleno, act_dataset, act_langset, act_schemaset
    act_trial = []
    act_trial_lang = []
    for reps in range(int(params['ncycles'])):  # ensure ncycles is type int bc doSetParams converts it to float
        cycleno += 1
        # gather netInput from pools
        netInput(cues)
        netInput(lets)
        netInput(words)
        netInput(lang)
        netInput(schemas)
        # update the pools
        update(cues)
        update(lets)
        update(words)
        update(lang)
        update(schemas)


        # ARI_EDIT
        curr_activations = readActivations(words)
        # print(curr_activations)

        ##### calculate the information gain based on activations

        # params: input word, activations of lexicon, recenter bool
        

        ##### update the nonword unit
        words['non-word'][0].setActivation(3.0)
        print(words['non-word'][0].getActivation())


        act_dataset.append(readActivations(words))
        act_langset.append(readActivations(lang))
        act_schemaset.append(readActivations(schemas))
        act_trial.append(readActivations(words))
        act_trial_lang.append(readActivations(lang))
        if verbose is True:
            print 'Word Activations:'
            print('Cycleno: ' + repr(reps + 1) + ' ' + repr(act_trial[reps]))
            print 'Language Node Activations:'
            print('Cycleno: ' + repr(reps + 1) + ' ' + repr(act_trial_lang[reps]))
    return act_dataset, act_langset


def extract_col(col_num, dataset):
    col = []
    for cycle_row in dataset:
        col.append(cycle_row[col_num][1])
    return col


#   NEW readActivation using generic pool structure
#   Reads all units in pool and if the pool is legal (a dict obj), returns:
#   act_list: [[unit_name0, activation],..,[unit_name,activation]]
#   Input: a pool such as words, lets, lang and an activation data set.
#           It is up to the caller to initialize an empty dataset.
def readActivations(pool):
    def getKey(item):
        return item[0]
    act_list = []
    for key, unit_list in pool.iteritems():
        posnum = 0
        for unit in unit_list:
            activation = unit.getActivation()
            act_list.append([key + repr(posnum),activation])
            posnum += 1
    act_list = sorted(act_list, key=getKey)

    return act_list


#   function netInput(rcvr_pool) parses the projections in rcvr_pool and looks up activation of each sending unit
#   The standard netInput routine computes the net input for
#   each pool. The net input consists of three things: the external input, scaled by
#   estr; the excitatory input from other units, scaled by alpha; and the inhibitory
#   input from other units, scaled by gamma. For each pool, the netInput routine first
#   accumulates the excitatory and inhibitory inputs from other units, then scales
#   the inputs and adds them to the scaled external input to obtain the net input.
def netInput(rcvr_pool):
    global pool_list, params
    # generic pool function
    for key, unit_list in rcvr_pool.iteritems():
        for unit in unit_list:
            in_pool = False
            excitation = 0
            inhibition = 0
            if not unit.isProjNone():
                for sender in unit.getProjList():
                    #print repr(unit.getProjList())
                    from_keypos = sender[0]
                    from_key = from_keypos[0]
                    from_pos = from_keypos[1]
                    weight = sender[1]
                # check to see if key is in any sending pool, i.e. lets, words, lang
                    for pool in pool_list:

                        #print 'From Key:' + repr(from_key)
                        if from_key in pool:
                            activation = pool[from_key][from_pos].getActivation()
                            in_pool = True
                            break
                        else:
                            in_pool = False
                    if in_pool is False:
                        print("NetInput: Unrecoverable Error. No pool found.")
                        sys.exit(1)

                    if activation > 0:     # process only positive activations
                        if weight > 0:
                            excitation += weight * activation
                        elif weight < 0:
                            inhibition += weight * activation
            excitation *= params['alpha']
            inhibition *= params['gamma']
            unit.setNetInput(excitation + inhibition + unit.getExtInput()*params['estr'])
    return


# Standard update. The update routine increments the activation of each unit,
# based on the net input and the existing activation value.
def update(pool):
    global params
    # generic pool update
    for key, unit_list in pool.iteritems():
        for unit in unit_list:
            activation = unit.getActivation()
            resting_level = unit.getRest()
            if activation > 0:
                unit.setActivation(activation + (params['max'] - activation) * unit.getNetInput()
                                   - params['decay'] * (activation - resting_level))
            else:
                unit.setActivation(activation + (activation - params['min']) * unit.getNetInput()
                                   - params['decay'] * (activation - resting_level))
    return


#   ***********************************Model's User Interface *******************************************

#   function definitions
#
#   Handle user entering a character not found in "case" dictionary
def errhandler():
    global console_message, mode
    mode = 'Error'
    console_message = "Unrecognized action. Try again"
    return


#   Print Letter Pool
def printLets():
    global a2z
    print 'Letter Pool'
    for key in a2z:
        value = lets[key]
        for i in range(5):
            print(key + '[' + repr(i) + ']: ' + repr(value[i].getProjList()))
    return


# print all the lang pools, nicely formatted
def printLang():
    print 'Language Pool'
    for key, value in lang.iteritems():
        proj_list = value[0].getProjList()
        num_cols = 5
        num_words = len(proj_list)
        print_rows = int(math.floor(num_words / num_cols))
        rem_cols = num_words % num_cols
        print '\n' + key.upper() + ' projs: ' + repr(num_words)

        # print rows with no. cols
        for i in range(0,print_rows):
            j = i * num_cols
            print ('{0:s},{1:s},{2:s},{3:s},{4:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2],
                                                              proj_list[j+3],proj_list[j+4]))

        # here we print the remaining words which fill a partial row
        j = (i + 1) * num_cols
        if rem_cols == 1:
            print ('{0:s}'.format(proj_list[j]))
        elif rem_cols == 2:
            print ('{0:s},{1:s}'.format(proj_list[j],proj_list[j+1]))
        elif rem_cols == 3:
            print ('{0:s},{1:s},{2:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2]))
        elif rem_cols == 4:
            print ('{0:s},{1:s},{2:s},{3:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2],proj_list[j+3]))
    return


#   print all the word pools, nicely formatted
def printWords_Full():
    print 'Word Pool'
    for key, value in words.iteritems():
        proj_list = value[0].getProjList()
        word_len = len(key)
        num_words = len(proj_list)
        print_rows = int(math.floor(num_words / word_len))
        rem_cols = num_words % word_len
        print '\n' + key.upper() + ' projs: ' + repr(num_words)

        # print rows with no. cols. = word length
        for i in range(0,print_rows):
            j = i * word_len
            if word_len == 3:
                print ('{0:s},{1:s},{2:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2]))
            elif word_len == 4:
                print ('{0:s},{1:s},{2:s},{3:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2],proj_list[j+3]))
            elif word_len == 5:
                print ('{0:s},{1:s},{2:s},{3:s},{4:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2],
                                                              proj_list[j+3],proj_list[j+4]))
            else: break

        # here we print the remaining words which fill a partial row
        j = (i + 1) * word_len
        if rem_cols == 1:
            print ('{0:s}'.format(proj_list[j]))
        elif rem_cols == 2:
            print ('{0:s},{1:s}'.format(proj_list[j],proj_list[j+1]))
        elif rem_cols == 3:
            print ('{0:s},{1:s},{2:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2]))
        elif rem_cols == 4:
            print ('{0:s},{1:s},{2:s},{3:s}'.format(proj_list[j],proj_list[j+1],proj_list[j+2],proj_list[j+3]))
    return

def printWords():
    cols = 6    # max columns
    separator = 6 # space between words
    global mode
    mode = 'Print Lexicon'
    buildConsoleMsg()
    print 'Lexicon:'
    lexicon = build_keys(words)
    all_rows = divmod(len(lexicon), cols)
    full_rows = all_rows[0]
    partial_rows = all_rows[1]
    row_idx = 0
    for row_idx in range(full_rows):
        for col_idx in range(cols):
            print repr(lexicon[col_idx + row_idx * cols]) + (separator - len(lexicon[col_idx + row_idx * cols])) * ' ',
        print '\n'
    if partial_rows != 0:
        for col_idx in range(partial_rows):
            print repr(lexicon[col_idx + row_idx * cols]) + (separator - len(lexicon[col_idx + row_idx * cols])) * ' ',
        print '\n'


#   Process a new input word from console
def doNewWord():
    global input_word, trial, console_message, mode, script_mode, item_script, blankCycle
    # clear the ext_input from the last word
    mode = 'New word'
    blankCycle = False
    for pos in range(len(input_word)):
        lets[input_word[pos]][pos].setExtInput(0)
    if not script_mode:
        input_word = raw_input('Enter a three to five character word: ')
    else:
        input_word = item_script
    input_word = input_word.lower()

    '''
    if input_word not in words:
        mode = 'Error'
        console_message = '{:s} not in vocabulary'.format(input_word.upper())
        input_word = ''
        return
    '''
    if len(input_word) > 5:
        input_word = input_word[:5]
        console_message = 'Word truncated to ' + input_word
    else:
        console_message = 'You entered: {0:s}'.format(input_word.upper())
    buildConsoleMsg()
#   set the extInput according to the input_word
    for pos in range(len(input_word)):
        lets[input_word[pos]][pos].setExtInput(1)

    return


#   Get and return activation of input word, l1 schema, l2 schema
def getActivations():
    global input_word
    if input_word not in words:
        word_act = rest
    else:
        unit = words[input_word][0]
        word_act = unit.getActivation()
    l1_act = lang['english'][0]
    l2_act = lang['spanish'][0]
    l1schema_act = schemas['l1'][0]
    l2schema_act = schemas['l2'][0]
    return (word_act, l1_act.getActivation(), l2_act.getActivation(), l1schema_act.getActivation(),
            l2schema_act.getActivation())


def buildConsoleMsg():
    global console_message
    word_act, l1_act, l2_act, l1schem_act, l2schem_act = getActivations()
    console_message = 'Input word: {0:s}     Activ: {1:4f}\n          English:  {2:4f} Spanish:   {3:4f}\n          '\
                      'L1 Schema: {4:4f} L2 Schema: {5:4f}'\
        .format(input_word.upper(),word_act,l1_act,l2_act,l1schem_act,l2schem_act)
    return


#   Perform an update cycle, so long as a word has been inputted
def doContinue():
    global mode, input_word, console_message, mode
    if input_word == '':
        mode = 'Error'
        console_message = 'Unable to cycle until word is entered.'
        return
    mode = 'Cycle'
    cycle_pool()
    buildConsoleMsg()
    return


#   Clear the ExtInput to the letters and the cues and cycle the network
def doBlankCycle():
    global input_word, trial, console_message, mode, blankCycle
    # clear the ext_input from the last word
    mode = 'Blank cycle'
    blankCycle = True
    for pos in range(len(input_word)):
        lets[input_word[pos]][pos].setExtInput(0)
    # input_word = 'BLANK'
    cues['cue2'][0].setExtInput(0)
    cues['cue1'][0].setExtInput(0)
    cycle_pool()
    buildConsoleMsg()
    return


#   Set the cue ext input to 1 in order to activate
def doSetCue1():
    global mode, console_message
    mode = 'Set L1 Cue'
    buildConsoleMsg()
    cues['cue1'][0].setExtInput(1)
    cues['cue2'][0].setExtInput(0)
    return


#   Set the cue ext input to 1 in order to activate
def doSetCue2():
    global mode, console_message
    mode = 'Set L2 Cue'
    buildConsoleMsg()
    cues['cue2'][0].setExtInput(1)
    cues['cue1'][0].setExtInput(0)
    return


#   [D1] display a single plot with activations, 10 words at-a-time
def doDisplay():
    global cycleno, console_message, mode, input_word, act_dataset

    def build_key_list(activation_set):
        key_list = []
        for word_tuple in activation_set:
            key_list.append(word_tuple[0][:-1])
        return key_list

    def build_next_act_list(act_list, i_pos, j_pos):
        next_act_list = []
        sliceObj = slice(i_pos, j_pos)
        for time_step in act_list:
            next_act_list.append(time_step[sliceObj])
        return next_act_list

    action_set = {'p', 'n', 'q'}
    lines = ['--', '-.', ':', '-']
    linecycler = cycle(lines)
    step = 10 # this is number of activations we will display

    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    # key_list_test = build_keys(words)

    buildConsoleMsg()
    plt.xlabel('Cycles')
    plt.ylabel('Activation')
    # fig, ax = plt.subplots()
    # Since we want to be able to handle large lexicon, let the user cycle through 10 at a time
    iterations = divmod(len(act_dataset[0]), step)  # (quotient, remainder)
    pos = 0
    i_pos = 0

    while True:
        next_act_dataset = build_next_act_list(act_dataset, i_pos, i_pos + step)
        key_list = build_key_list(next_act_dataset[0])
        mode = '1-plot, {0:d}-words'.format(len(key_list))
        x_vals = genx_axis(1,len(next_act_dataset)+1)
        for col in range(len(next_act_dataset[1])):
            plt.plot(x_vals, extract_col(col, next_act_dataset), next(linecycler))
        word_act, l1, l2, l1schema, l2schema = getActivations()
        plt.title('Input word: {0:s} Activ: {1:4f}'.format(input_word.upper(), word_act))
        plt.legend(key_list, loc='best', ncol=3)
        plt.show()

        action_input = raw_input("Enter [N]ext, [P]rev, [Q]uit: ").lower()
        if action_input not in action_set:
            mode = 'Error'
            console_message = '{:s} not valid action'.format(action_input.upper())
            plt.close()
            return
        elif action_input == 'n':
            if pos < iterations[0]:
                pos += 1
                i_pos += step
            plt.gcf().clear()
        elif action_input == 'p':
            i_pos -= step
            pos -= 1
            if i_pos < 0:
                i_pos = 0
                pos = 0
            plt.gcf().clear()
        elif action_input == 'q':
            plt.close()
            return


#   display a single plot with activations of all language nodes
def doDisplayLang():
    global cycleno, console_message, mode, input_word, act_langset
    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    key_list = build_keys(lang)
    mode = '1-plot, {0:d}-languages'.format(len(key_list))
    console_message = 'You entered: {0:s}'.format(input_word)
    plt.xlabel('Cycles')
    plt.ylabel('Activation')
    x_vals = genx_axis(1,len(act_langset)+1)
    for col in range(len(act_langset[1])):
        plt.plot(x_vals, extract_col(col,act_langset))
    plt.title('Input word: %s' %input_word.upper())

    plt.legend(key_list, loc='best', ncol=3)
    plt.show()
    return


#   Display activation of one or more words or langs entered at input prompt
#   Note: Must have run at least 1 cycle
def doDisplayItems():
    global cycleno, console_message, mode, act_dataset, act_langset, act_schemaset, input_word, script_mode, list_script
    lines = ['--', '-.', ':', '-']
    linecycler = cycle(lines)
    # must have processed at least one update cycle
    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    #
    plt.close()
    mode = '1-plot, n-items'
    buildConsoleMsg()
    word_key_list = build_keys(words)
    lang_key_list = build_keys(lang)
    schema_key_list = build_keys(schemas)
    key_list = []
    if not script_mode:
        select_item = raw_input('Enter 1 or more items separated by a comma:').split(',')
    else:
        select_item = list_script
    plt.xlabel('Cycles')
    plt.ylabel('Activation')
    x_vals = genx_axis(1,len(act_dataset)+1)

    for item in select_item:
        item = item.lower()
        if item in words:
            item_index = word_key_list.index(item)
            plt.plot(x_vals, extract_col(item_index,act_dataset),next(linecycler))
            key_list.append(item)
        elif item in lang:
            item_index = lang_key_list.index(item)
            plt.plot(x_vals, extract_col(item_index,act_langset),next(linecycler))
            key_list.append(item)
        elif item in schemas:
            item_index = schema_key_list.index(item)
            plt.plot(x_vals, extract_col(item_index,act_schemaset),next(linecycler))
            key_list.append(item)
        else:
            mode = 'Error'
            console_message = item  + ' Item not found in pool.'
            return
    word_act, l1, l2, l1schema, l2schema = getActivations()
    plt.title('Input word: {0:s} Activ: {1:4f}'.format(input_word.upper(),word_act))
    plt.legend(key_list, loc='best')
    plt.show()
    return


#   display Top 10 Activations
def doDisplayTop10():
    rows = 10
    left_margin = 10
    max_word_len = 5 + 1
    global act_dataset, input_word, display_cols, mode, console_message
    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    mode = 'Top 10 Activs'
    buildConsoleMsg()
    activations_t = act_dataset[-1]     # get latest activations
    activations_t.sort(key=operator.itemgetter(1), reverse=True)

    print ''
    print (5 * ' '),
    print('*** Top 10 Activations ***\n')
    print ((left_margin) * ' '),
    print('word  activation')
    print ((left_margin) * ' '),
    print('----------------')
    for i in range(rows):
        word = activations_t[i][0][:-1]
        word_str = word + (max_word_len - len(word)) * ' '
        print (left_margin * ' '),
        print('%s%+.4f' % (word_str, activations_t[i][1]))

    return

#   display a subplot for each word. Function calculates number of rows based on display_cols, a global parameter
def doDisplaySubPlots():
    global act_dataset, input_word, display_cols, mode, console_message, max_subplots
    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    mode = 'Subplot words'
    buildConsoleMsg()
    num_words = len(act_dataset[1])
    if num_words > max_subplots:
        mode = 'Error'
        console_message = 'Too many subplots to display'
        return
    display_rows = int(math.ceil(num_words / display_cols))
    word_ctr = 0
    key_list = build_keys(words)
    x_vals = genx_axis(1,len(act_dataset)+1)
    f, axarr = plt.subplots(display_rows,int(display_cols),sharex='col', sharey='row')
    for i in range(display_rows):
        for j in range(int(display_cols)):
            if word_ctr <= (num_words - 1):
                axarr[i][j].plot(x_vals, extract_col(word_ctr,act_dataset))
                axarr[i][j].set_title('%s' %key_list[word_ctr], va='center', size='small',weight='demi', style='italic')
                word_ctr += 1
    word_act, l1, l2, l1schema, l2schema = getActivations()
    plt.suptitle('Input word: {0:s} Activ: {1:4f}'.format(input_word.upper(),word_act), size='large',weight='bold')
    plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
    plt.setp([a.get_yticklabels() for a in axarr[:, 0]], size='x-small')
    plt.show()
    return


#  NEW VERSION display a subplot for each word. Show 10 subplots per chart. Allows Scrolling.
#  Function calculates number of rows based on display_cols, a global parameter
def doDisplaySubPlots_NEW():
    global act_dataset, input_word, display_cols, mode, console_message, max_subplots

    def build_key_list(activation_set):
        key_list = []
        for word_tuple in activation_set:
            key_list.append(word_tuple[0][:-1])
        return key_list

    def build_next_act_list(act_list, i_pos, j_pos):
        next_act_list = []
        sliceObj = slice(i_pos, j_pos)
        for time_step in act_list:
            next_act_list.append(time_step[sliceObj])
        return next_act_list

    action_set = {'p', 'n', 'q'}
    step = 12 # this is number of activations we will display

    if cycleno == 0:
        mode = 'Error'
        console_message = 'No data available until a cycle is run.'
        return
    # key_list_test = build_keys(words)
    mode = 'Subplot words'
    buildConsoleMsg()

    # Since we want to be able to handle large lexicon, let the user cycle through 10 at a time
    iterations = divmod(len(act_dataset[0]), step)  # (quotient, remainder)
    pos = 0
    i_pos = 0

    while True:
        next_act_dataset = build_next_act_list(act_dataset, i_pos, i_pos + step)
        key_list = build_key_list(next_act_dataset[0])
        num_words = len(key_list)
        display_rows = int(math.ceil(num_words / display_cols))
        word_ctr = 0
        x_vals = genx_axis(1, len(next_act_dataset) + 1)
        f, axarr = plt.subplots(display_rows, int(display_cols), sharex='col', sharey='row')
        for i in range(display_rows):
            for j in range(int(display_cols)):
                if word_ctr <= (num_words - 1):
                    axarr[i][j].plot(x_vals, extract_col(word_ctr, next_act_dataset))
                    axarr[i][j].set_title('%s' % key_list[word_ctr], va='center', size='small', weight='demi',
                                          style='italic')
                    word_ctr += 1

        word_act, l1, l2, l1schema, l2schema = getActivations()
        plt.suptitle('Input word: {0:s} Activ: {1:4f}'.format(input_word.upper(), word_act), size='large',
                     weight='bold')
        plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
        plt.setp([a.get_yticklabels() for a in axarr[:, 0]], size='x-small')
        plt.show()

        action_input = raw_input("Enter [N]ext, [P]rev, [Q]uit: ").lower()
        if action_input not in action_set:
            mode = 'Error'
            console_message = '{:s} not valid action'.format(action_input.upper())
            return
        elif action_input == 'n':
            if pos < iterations[0]:
                pos += 1
                i_pos += step
            # plt.gcf().clear()
            plt.close()
        elif action_input == 'p':
            i_pos -= step
            pos -= 1
            if i_pos < 0:
                i_pos = 0
                pos = 0
            # plt.gcf().clear()
            plt.close()
        elif action_input == 'q':
            return

#   Provides a user interface for altering the IAC parameters.
#   Note: Must reset the model as well
def doSetParams():
    global params, mode, console_message

    def mapvars(kwargs):
        global params, mode, console_message
        if kwargs != ['']:

            for key in kwargs:
                key_val = key.split('=')
                if key_val[0] in params:
                    params[key_val[0]] = float(key_val[1])
                else:
                    mode = 'Error'
                    console_message = 'Invalid parameter keyword'
                    return
        return

    mode = 'Parameter reset'
    p = raw_input('Enter params separated by a comma:').split(',')
    mapvars(p)
    console_message = 'Params: ' + repr(params)
    return


#   Turns verbose flag on/off
def doLogging():
    global verbose, mode, console_message, input_word
    console_message = 'You entered: {0:s}'.format(input_word)
    mode = 'Verbose'
    if verbose is True:
        verbose = False
    else: verbose = True
    return


def doExit():
    print 'Adios!'
    sys.exit(0)


#   Read new word stimuli from file and update lets, words, and lang pools
#   Steps to add a new word to Word pool
#   1. copy word3,word4, or word5 template and make lets_word projections dictionary (+)
#   2. copy word_si_template, replacing 'new_word" with corresponding string literal of new word (+)
#   3. in lets_word_proj dict, replace the inhib weight with the excit weight in each letter unit corresponding to the
#      letter pos in the new_word (+)
#   4a Scan through all the words in the pool and build a self-inhibitory list and append to lets_word proj dict
#   4b While scanning words in pool (step 4a), append copied word_si_template to its unit
#   5. add new dictionary entry to word pool: key = new word string, value = new_word proj list
#
#   Steps to add a new word to Lets pool
#   1. copy word_lets_template, replacing 'new_word' with string literal of word to be added (+)
#   1. For each let in new word, find corresponding let and let position unit in lets pool
#      and append wordn_lets_template (+)
#
#   Steps to add new word to Lang pool
#   1. copy word_lang_template, replacing 'new_word' with string literal of new word
#   1. append copied word_lang_template to proj list in appropriate lang pool

#   Stimuli in CSV file format, i.e., word,language,resting_activation\n

def doAutoLoad():
    global mode, console_message, a2z, rest

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def load_stimuli(file_str):
        i = 0
        csv_pattern = re.compile(',')
        script = []
        with open(file_str) as f:
            for i, line in enumerate(f):
                line = line.strip()
                split = csv_pattern.split(line)
                # split[-1] = split[-1][:-1]
                script.append(split)
        print('*** Read (%d) words ***' % (i + 1))
        return script
    #
    # Create the letter dictionary. This is used to locate the offset (letter X position-in-word) of the letter unit

    let_dict = {v: k for k, v in enumerate(a2z)}

    stimuli_file = raw_input('             Please enter the stimuli filename: ')
    if not os.path.isfile(stimuli_file):
        mode = 'Error: Auto-load'
        console_message = 'Stimuli file does not exist: ' + repr(stimuli_file)
        return
    stimuli = load_stimuli(stimuli_file)
    print '*** Building Pools. This may take a moment. ***'
    mode = 'Auto-loading Stimuli'
    #
    # process each stimulus

    # ARI_EDIT
    nonword_resting_activation = 0.0

    for new_stim in stimuli:
        resting_activation = params['rest'] # we can alter the default resting level for auto-loaded words this way
        nonword_resting_activation = resting_activation

        # stimulus properly formatted?
        if len(new_stim) < 2:
            mode = 'Error: Auto-load'
            console_message = 'Stimuli improperly formatted'
            break
        new_word = new_stim[0].lower()
        language = new_stim[1].lower()
        # do we have a resting activation?
        if len(new_stim) == 3:
            if  not is_number(new_stim[2]):
                mode = 'Warning: Auto-load'
                # console_message = 'Resting value is not a float ' + repr(new_stim)
                console_message = 'One or more resting values defaulted'
                resting_activation = params['rest']
            else:
                resting_activation = float(new_stim[2])
        # language recognized?
        if language not in lang:
            mode = 'Error: Auto-load'
            console_message = 'Unknown language attribute ' + repr(language)

            break
        # word length 3, 4, or 5?
        if len(new_word) not in word_lets_template:
            mode = 'Error: Auto-load'
            console_message = 'Stimulus 3 <= word <= 5 lets'
            break

        # passed preliminary error checking
        # make a deep copy of the word_lets and word_si templates, updating placeholder with our new word
        word_lets_proj = copy.deepcopy(word_lets_template[len(new_word)])
        word_lets_proj[0][0] = new_word  # word projections for corresponding letters in the lets pool
        word_lang_proj = copy.deepcopy(word_lang_template)
        word_lang_proj[0][0] = new_word  # word projection for corresponding language
        new_word_si = copy.deepcopy(word_si_template)
        new_word_si[0][0] = new_word      # new_word si projection appended to proj list of all other word units
        #
        # deep copy word3,word4, or word5 template and make new_word projections list: lets_word_proj
        # lets_word_proj are all the projections from corresponding letter positions to the new word
        word_len = len(new_word)
        lets_word_proj = copy.deepcopy(lets_word_template[word_len])

        # in lets_word_proj dict, replace the inhib weight with the excit weight in each letter unit corresponding
        # to the letter pos in the new_word
        for pos, let in enumerate(new_word):
            list_index = (let_dict[let] * word_len) + pos
            lets_word_proj[list_index][1] *= -1

        # Scan through all the words in the pool and build word_si_list and EXTEND lets_word proj dict
        # While scanning words in pool (step 4a), append copied word_si_template to its unit
        word_si_list = []
        for word in words:
            # print word
            word_si = copy.deepcopy(word_si_template)  # a word self-inhibitory projection
            word_si[0][0] = word
            word_si_list.append(word_si)    # build the si list of all words except new_word
            if not words[word][0].isProjNone():
                unit_proj_list = words[word][0].getProjList()
                unit_proj_list.append(new_word_si)
             # print new_word_si
             # print unit_proj_list
                words[word][0].setProjList(unit_proj_list)
            else: print "isProjNone: word pool. " + word

        # add new_word to the word pool: key: new word string value; lets_word_proj dict
        # NOTE: We EXTEND the lets_word_proj list to create the properly formatted projection list
        lets_word_proj.extend(word_si_list)
        words[new_word] = [Unit(lets_word_proj, resting_activation)]


    # print(new_word + ': ' + repr(words[new_word][0].getProjList()))

    # For each let in new word, find corresponding let and let position unit in lets pool and append wordn_lets_template
        for pos in range(len(new_word)):
            if not lets[new_word[pos]][pos].isProjNone():
                unit_proj_list = lets[new_word[pos]][pos].getProjList()
                unit_proj_list.append(word_lets_proj)
                lets[new_word[pos]][pos].setProjList(unit_proj_list)
            else:
                lets[new_word[pos]][pos].setProjList([word_lets_proj])

    # Append the new word to the corresponding language pool
        if not lang[language][0].isProjNone():
            lang_proj_list = lang[language][0].getProjList()
            lang_proj_list.append(word_lang_proj)
            lang[language][0].setProjList(lang_proj_list)
        else:
            lang[language][0].setProjList([word_lang_proj])


    # ARI_EDIT
    words['non-word'] = [Unit(activation=nonword_resting_activation)] # set the activation, no projections to letters


    #   DEBUGGING CODE
    # printLets()
    # printWords()
    return

#  *************** script versions of above model operations ************************

#   This processes a simple script of records to automate the testing process.
#   Note: error processing is VERY limited. Best to assume script items are correct.
#   Each record is in CSV format and invokes a model function as follows:
#   ['r']                resets the model
#   ['n',word]           present a new 3 to 5 letter word to the lets pool
#   ['c1' | 'c2']        turns on cue1 or cue2 and turns off complementary cue
#   ['rc',ncycles]       run cycle: cycles model for ncycles
#   ['rs',item]          run settle: cycles model until item activation reaches equilibrium.
#                        Cycleno contains corresponding value.
#   ['b',ncycles]        cycles model with 'blank' word for ncycles; turning off c1 and c2 while it does so.
#   ['d',item1,item2,...itemn}  displays plot of listed items
#   ['t',comment]        adds a trace rec to a log table with: cycleno, word (act), l1, l2, l1schema, l2schema, comment
#   ['pt']               prints all trace records in the log file to std output i.e. console
#   ['wt']               creates log.csv file containing all trace records in CSV format


def scriptProcessor():
    global script_mode, list_script, mode, item_script, cycleno, ncycles, log
    #   Clear the ExtInput to the letters and the cues and cycle the network
    #   Script command: ['B',ncycles]

    def runBlankCycle():
        global ncycles, mode, blankCycle
        mode = 'runBlankCycles'
        blankCycle = True
        for pos in range(len(input_word)):
            lets[input_word[pos]][pos].setExtInput(0)
        cues['cue2'][0].setExtInput(0)
        cues['cue1'][0].setExtInput(0)
        for i in range(ncycles):
            cycle_pool()
        buildConsoleMsg()
        ncycles = 0     # reset ncycle between script statements
        return


#   runCycle will cycle the model until ncycles
    def runCycle():
        global item_script, ncycles, e, mode
        #
        #   process ['rc', ncycles]
        if ncycles != 0:

            mode = 'runCycle ncycles'
            for i in range(ncycles):
                cycle_pool()
            buildConsoleMsg()
            ncycles = 0
            return


#   runSettle will cycle the model until the node given in item settles
    def runSettle():
        global item_script, ncycles, e, mode
        #   process ['rs', item]
        if item_script != '':
            mode = 'runCycle until convergence'
            if item_script in words:
                unit = words[item_script][0]
                last_act = unit.getActivation()
            elif item_script in lang:
                unit = lang[item_script][0]
                last_act = unit.getActivation()
            elif item_script in schemas:
                unit = schemas[item_script][0]
                last_act = unit.getActivation()
            else:
                mode = 'Error in Run Cycle Script'
                buildConsoleMsg()
                return

            # Check for convergence to epsilon
            cycleno_settle = 0
            while True:
                cycle_pool()
                curr_act = unit.getActivation()
                # give it a few cycles to become activated but don't let it run away!
                cycle_range = (5 < cycleno_settle < 10000)
                if (abs((last_act - curr_act)) <= e) and cycle_range:
                    break
                else:
                    last_act = curr_act
                    cycleno_settle += 1
        buildConsoleMsg()
        return


#   read and load the script
    def load_script(file_str):
        print('Loading script')
        csv_pattern = re.compile(',')
        script = []
        with open(file_str) as f:
            for line in f:
                split = csv_pattern.split(line)
                split[-1] = split[-1][:-1]
                script.append(split)
        return script

    #   Logs events to log list
    def runTrace():
        global log, item_script, blankCycle

        rec = list(getActivations())        # this unpacks the tuple and converts to a list
        rec = [round(act,4) for act in rec] # round to a reasonable precision
        if not blankCycle:
            rec.insert(0,input_word)           # append item_script to front of list
        else:
            rec.insert(0,'BLANK')           # append item_script to front of list

        rec.insert(0,item_script)
        rec.extend([cycleno])
        rec.extend([0])                     # this is a placeholder for event duration
        log.append(rec)
        return

    #   Prints a formatted trace to std output
    def printTrace():
        global log
        for i in log:
            print i
        return

    #   write log to CSV file
    def writeCSV():
        global log, input_word
        header = ['Type','Input','Word','L1','L2','L1 LDT','L2 LDT','No. cycles','Event duration']
        last_cycleno = 0
        with open('log.csv', 'wb') as csvfile:
            logwriter = csv.writer(csvfile)
            logwriter.writerow(header)
            for rec in log:
                event_duration = rec[7] - last_cycleno
                rec[8] = event_duration
                logwriter.writerow(rec)
                last_cycleno = rec[7]
        csvfile.close()
        return


    def showScriptProgress():
        instr_params = str(line[1:]).strip('[]')
        print '-----------------------------------------------------'
        print '           Script: %s %s Mode: %s' % (instr, instr_params, mode)
        print ('                Trial: %d Cycle: %d' % (trial, cycleno))
        print
        print ('          %s' % console_message)
        return

#   Script processing is implemented as a switch using a Python dictionary
    run_script = {
        'b':    runBlankCycle,
        'c1':   doSetCue1,
        'c2':   doSetCue2,
        'd':    doDisplayItems,
        'n':    doNewWord,
        'pt':   printTrace,
        'r':    reset,
        'rc':   runCycle,
        'rs':   runSettle,
        't':    runTrace,
        'wt':   writeCSV
    }

    #   Read the script and process each items
    script_name = raw_input('             Please enter the script filename: ')
    script = load_script(script_name)
    script_mode = True
    ncycles = 0
    list_script = []
    item_script = ''
    temp = params['ncycles']
    params['ncycles'] = 1
    print script
    #
    #   pre-process script instructions
    for line in script:
        instr = line[0]

        if instr not in run_script:
            mode = 'Error in Script. Command not found.'
            buildConsoleMsg()
            break
        if (instr == 'rc') or (instr == 'b'):
            ncycles = int(float(line[1]))  # just in case a floating point is entered
        if (instr == 'rs') or (instr == 'n') or (instr == 't'):
            item_script = line[1]
        if instr == 'd':
            list_script = line[1:]
        run_script.get(instr,errhandler)()
        showScriptProgress()
    script_mode = False
    params['ncycles'] = temp
    #writeCSV()
    return


def showBanner():
    print
    print '******************************************************'
    print '      Bilingual Interactive Activation Model'
    print '     Andrew Valenti, HRI Lab, Tufts University'
    print
    print '              A: Auto-load words'
    print '              B: Blank word cycle'
    print '              C: Continue cycle'
    print '              Cue activation:'
    print '                  C1:  L1 cue activation'
    print '                  C2:  L2 cue activation'
    print '              Display activations:'
    print '                  D:   Enter 1 or more words or languages'
    print '                  D1:  All words, singe plot'
    print '                  D2:  Subplot words'
    print '                  D10: Top 10 word activations'
    print '              N:  Enter a new word'
    print '              P:  Set model parameters'
    print '              PW: Print Words in Lexicon'
    print '              R:  Reset model'
    print '              S:  Script processor'
    print '              T:  Toggle logging'
    print '              X:  Exit program'
    print
    print ('          Trial: %d Cycle: %d Mode: %s' % (trial, cycleno, mode))
    print ('          %s' % console_message)
    print '******************************************************'
    return

#   User interface is implemented as a switch using a Python dictionary
takeaction = {
    'A': doAutoLoad,
    'B': doBlankCycle,
    'C': doContinue,
    'D': doDisplayItems,
    'D1': doDisplay,
    'D2': doDisplaySubPlots_NEW,
    'D10': doDisplayTop10,
    'L': doDisplayLang,
    'P': doSetParams,
    'PAZ': printLets,
    'PW': printWords,
    'PL': printLang,
    'C1': doSetCue1,
    'C2': doSetCue2,
    'N': doNewWord,
    'R': reset,
    'S': scriptProcessor,
    'T': doLogging,
    'X': doExit
}
#   ****************************Model's User Interface Processing Loop*********************************
plt.ion()   # turn on interactive charting
while True:
    showBanner()
    action = raw_input('             Please enter an action: ')
    takeaction.get(action.upper(),errhandler)()
    # plt.show()













