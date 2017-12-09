import cohort_math_activations as cm

def append_str(floats):
	return ','.join([str(f) for f in floats])

mingain = cm.get_info_gain(
	input_word='hello',
	activations=[['hello'], [0.5]],
	should_recenter=False,
	aggregator=cm.sum,
	maxval = 5)
print str(mingain)

maxgain_list = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx'], [0.5]],
	should_recenter=False,
	aggregator=append_str,
	maxval = 5)
print str(maxgain_list)

maxgain_sum = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx'], [0.5]],
	should_recenter=False,
	aggregator=cm.sum,
	maxval = 5)
print str(maxgain_sum)

maxgain_avg = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx'], [0.5]],
	should_recenter=False,
	aggregator=cm.avg,
	maxval = 5)
print str(maxgain_avg)

midgain_list = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 'hello'], [0.5, 0.5]],
	should_recenter=False,
	aggregator=append_str,
	maxval = 5)
print str(midgain_list)

