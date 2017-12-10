import codecs
import sys

def main():
	language = 'english'
	minlen = 3
	maxlen = 5
	
	print

	try:
		max_words = int(sys.argv[1])
		infilename = sys.argv[2]
		outfilename = sys.argv[3]
	except Exception as e:
		print 'Usage: ' + sys.argv[0] + ' max_words infile outfile'
		print
		raise e

	good_words = set()

	with codecs.open(infilename, 'r', 'utf-8') as infile:
		for line in infile:
			if len(good_words) >= max_words:
				break
			
			word = get_filtered_word(line, minlen, maxlen)
			if word is not None:
				good_words.add(word)
	
	with open(outfilename, 'w') as outfile:
		for word in good_words:
			outfile.write(word + ',' + language + '\n')

	print 'Wrote ' + str(len(good_words)) + ' words to ' + outfilename + '.'

def get_filtered_word(line, minlen, maxlen):
	line = line.strip()	
	
	length = len(line)
	if length > maxlen or length < minlen:
		return None

	for ch in line:
		if not ch.isalpha():
			return None

	return line.decode('utf-8').lower()

if __name__ == '__main__':
	main()

