from jsonhandler import Jsonhandler
from collections import Counter

handler = Jsonhandler("./pan12I")

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

cand_nu = 0     # candidate number
cand_pr = []    # candidate profile
counts = []     # summ of all n-gram
bigram_profile = []
text = ''
found_bit = 0
found_list = []
result = []     # dissimilarity of a text according to all candidates
name_of_candidates = []

n = 5           # size of n-gram
L = 500  #250    # size of profile


def dissimilarity(corpus_profile, corpus_size, unknown_profile,
        unknown_size):
    keys = set(corpus_profile.keys()) | set(corpus_profile.keys())
    summe = 0.0
    for k in keys:
        f1 = float(corpus_profile[k]) / corpus_size
        f2 = float(unknown_profile[k]) / unknown_size
        summe = summe + (2*(f1-f2)/(f1+f2))**2
    return summe


# If you want to do training:
handler.loadTesting()
for cand in handler.candidates:
    name_of_candidates.append(cand)
    cand_nu += 1      
    for file in handler.trainings[cand]:
		# Get content of training file 'file' of candidate 'cand' as a string with:
            text = text + handler.getTrainingText(cand, file)
    bigram_all = Counter(find_ngrams(text, n))
    
    counts.append(sum(bigram_all.values()))
    bigram_profile.append(Counter(dict(bigram_all.most_common(L))))
    text = ''    

# Create lists for your answers (and scores)
authors = []
scores = []

for file in handler.unknowns:
    result = []
    # Get content of unknown file 'file' as a string with:
    test = ''    
    test = handler.getUnknownText(file)
    # Determine author of the file, and score (optional)
    bigram_all = Counter(find_ngrams(test, n)) 
    counts_test = sum(bigram_all.values())
    bigram_test = Counter(dict(bigram_all.most_common(L)))

    for cand_nu in range(len(name_of_candidates)):
        result.append(dissimilarity(bigram_profile[cand_nu], counts[cand_nu],
                bigram_test, counts_test))
        author = name_of_candidates[result.index(min(result))]
   
 
#    author = "oneAuthor"
    score = 1
    authors.append(author)
    scores.append(score)

# Save results to json-file out.json (passing 'scores' is optional)
handler.storeJson(handler.unknowns, authors, scores)
