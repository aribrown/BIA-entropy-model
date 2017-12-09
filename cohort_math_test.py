import cohort_math_activations as cm

mingain, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['hello', 0.5]],
	should_recenter=False,
	aggregator=cm.sum,
	maxval = 5)
print str(mingain)

maxgain_list, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 0.5]],
	should_recenter=False,
	aggregator=cm.append_str,
	maxval = 5)
print str(maxgain_list)

maxgain_sum, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 0.5]],
	should_recenter=False,
	aggregator=cm.sum,
	maxval = 5)
print str(maxgain_sum)

maxgain_avg, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 0.5]],
	should_recenter=False,
	aggregator=cm.avg,
	maxval = 5)
print str(maxgain_avg)

midgain_list, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 0.5], ['hello', 0.5]],
	should_recenter=False,
	aggregator=cm.append_str,
	maxval = 5)
print str(midgain_list)

midgain_list_recenter, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['xxxxx', 0.5], ['hello', 0.5]],
	should_recenter=True,
	aggregator=cm.append_str,
	maxval = 5)
print str(midgain_list_recenter)

neggain_list, _ = cm.get_info_gain(
	input_word='hello',
	activations=[['hello', -0.5]],
	should_recenter=True,
	aggregator=cm.append_str,
	maxval = 5)
print str(neggain_list)

