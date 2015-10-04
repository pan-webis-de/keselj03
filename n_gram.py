from jsonhandler import Jsonhandler
from collections import Counter

import logging


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def dissimilarity(corpus_profile, corpus_size, unknown_profile, unknown_size):
    keys = set(corpus_profile.keys()) | set(unknown_profile.keys())
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
        logging.info("%s attributed to %s", file, author)
        authors.append(author)
        scores.append(score)
    return (authors, scores)

def fit_parameters(handler):
    n_range = [3, 4, 5, 6]
    L_range = [500, 1000, 2000, 3000, 5000]
#    n_range = [2,3]
#    L_range = [20, 50, 100]
    handler.loadTraining()
    results = []
    for n in n_range:
        for L in L_range:
            logging.info("Test parameters: n=%d, l=%d", n, L)
            authors, scores = create_ranking(handler, n, L)
            evaluation = handler.evalTesting(handler.unknowns, authors)
            results.append((evaluation["accuracy"], n, L))
    return results

def main(corpus):
    handler = Jsonhandler(corpus)
    parameters = fit_parameters(handler)
    acc, n, L = max(parameters, key = lambda r: r[0])
    logging.info("Choose parameters: n=%d, l=%d", n, L)
    handler.loadTesting()
    authors, scores = create_ranking(handler, n, L)
    handler.storeJson(handler.unknowns, authors, scores)

# Save results to json-file out.json (passing 'scores' is optional)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')
main("C10")
