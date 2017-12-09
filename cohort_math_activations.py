import numpy

"""
Calculates an aggregate information gain (float) given the inputs:
	input_word (string): the word presented to the model
	activations (list(string), list(float)): word unit words and their activations
	should_recenter (bool): recenter all activations such that they are nonnegative?
	aggregator (list(float) -> float): function to transform list of per-letter info gain values
		to a single return value
	maxval (float): maximum information gain possible
		(used as the infogain function approaches infinity)
"""
def get_info_gain(input_word, activations, should_recenter, aggregator, maxval):
	words = activations[0]
	actvals = activations[1]
	if should_recenter:
		actvals = __recenter__(actvals)

	actval_sum = numpy.sum(actvals)
	# gains starts as a list of inverse probabilities...
	gains = []
	for i in range(len(input_word)):
		one_over_p = __get_inverse_p__(
			input_letter=input_word[i],
			input_pos=i,
			words=words,
			actvals=actvals,
			sum_of_all_actvals=actval_sum)
		gains.append(one_over_p)
	
	# ...and then becomes a list of information gains
	def maxval_ceiling(floatnum):
		if floatnum > maxval:
			return maxval
		return floatnum
	gains = [maxval_ceiling(gain) for gain in numpy.log2(gains)]
	return aggregator(gains)

def sum(floats):
	return numpy.sum(floats)

def avg(floats):
	return numpy.mean(floats)

def append_str(floats):
	return ','.join([str(f) for f in floats])

"""
Return a recentered copy of the float list `a` such that the minimum value is positive
"""
def __recenter__(a):
	minval = numpy.min(a)
	if minval > 0.0:
		return a
	
	epsilon = 0.01
	offset = -1 * minval + epsilon
	return numpy.add(a, offset)

"""
Calculate the `1/p_k` term for the information gain formula
"""
def __get_inverse_p__(input_letter, input_pos, words, actvals, sum_of_all_actvals):	
	matching_actvals = []
	for i in range(len(words)):
		word = words[i]
		if len(word) > input_pos and word[input_pos] == input_letter:
			matching_actvals.append(actvals[i])
	if len(matching_actvals) == 0:
		return float("inf")

	p_numer = numpy.sum(matching_actvals)
	if p_numer == 0.0:
		return float("inf")
	
	p_denom = sum_of_all_actvals
	return p_denom/p_numer
