from jsonhandler import Jsonhandler
from collections import Counter


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def dissimilarity(corpus_profile, corpus_size, unknown_profile,
        unknown_size):
    keys = set(corpus_profile.keys()) | set(corpus_profile.keys())
    summe = 0.0
    for k in keys:
        f1 = float(corpus_profile[k]) / corpus_size
        f2 = float(unknown_profile[k]) / unknown_size
        summe = summe + (2*(f1-f2)/(f1+f2))**2
    return summe

def create_ranking(handler, n, L):
# If you want to do training:
    bigram_profile = []
    counts = []     # summ of all n-gram
    for cand in handler.candidates:
        text = ''
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

        for cand_nu in range(len(handler.candidates)):
            result.append(dissimilarity(bigram_profile[cand_nu], counts[cand_nu],
                    bigram_test, counts_test))
            author = handler.candidates[result.index(min(result))]
     
#    author = "oneAuthor"
        score = 1
        authors.append(author)
        scores.append(score)
    return (authors, scores)

# Save results to json-file out.json (passing 'scores' is optional)
handler = Jsonhandler("./pan12I")
handler.loadTesting()
authors, scores = create_ranking(handler, n=5, L=500)
handler.storeJson(handler.unknowns, authors, scores)
