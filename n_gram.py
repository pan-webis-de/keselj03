import jsonhandler
from collections import Counter

candidates = jsonhandler.candidates
unknowns = jsonhandler.unknowns
jsonhandler.loadJson("./pan11large-v2")

cand_nu = 0     # candidate number
cand_pr = []    # candidate profile
counts = []     # summ of all n-gram
bigram_profile = []
text = ''
found_bit = 0
found_list = []
result = []     # dissimilarity of a text according to all candidates
name_of_candidates = []

n = 3           # size of n-gram
L = 50  #250    # size of profile


summe = 0.0     # dissimilarity
f1 = 0.0        # frequence of n-gram in text 1
f2 = 0.0        # frequence of n-gram in text 2


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

# If you want to do training:
jsonhandler.loadTraining()
for cand in candidates:
    name_of_candidates.append(cand)
    cand_nu += 1      
    for file in jsonhandler.trainings[cand]:
		# Get content of training file 'file' of candidate 'cand' as a string with:
            text = text + jsonhandler.getTrainingText(cand, file)
    bigram_all = Counter(find_ngrams(text, n))
    
    counts.append(sum(bigram_all.values()))
    bigram_profile.append(bigram_all.most_common(L))
    text = ''    
  

# Create lists for your answers (and scores)
authors = []
scores = []

for file in unknowns:
    result = []
    # Get content of unknown file 'file' as a string with:
    test = ''    
    test = jsonhandler.getUnknownText(file)
    # Determine author of the file, and score (optional)
    bigram_all = Counter(find_ngrams(test, n)) 
    counts_test = sum(bigram_all.values())
    bigram_test = bigram_all.most_common(L)

    if len(bigram_test)<L:
        limit_test = len(bigram_test)
    else:
        limit_test = L
           
    for cand_nu in range(len(name_of_candidates)):
        
        if len(bigram_profile[cand_nu])<L:
            limit_profile = len(bigram_profile[cand_nu])
        else:
            limit_profile = L
        
        for i in range(limit_profile):
            for j in range(limit_test):
                if bigram_profile[cand_nu][i][0]==bigram_test[j][0]:
                    found_bit = 1
                    found_list.append(j)
                    f1 = float(bigram_profile[cand_nu][i][1]) / counts[cand_nu]
                    f2 = float(bigram_test[j][1]) / counts_test
                    summe = summe + (2*(f1-f2)/(f1+f2))**2

            if found_bit == 0:
                f1 = float(bigram_profile[cand_nu][i][1]) / counts[cand_nu]
                f2 = 0
                summe = summe + (2*(f1-f2)/(f1+f2))**2
            found_bit = 0
            
        for k in range(L):
            if not k in found_list:
                f1 = 0
                f2 = float(bigram_test[j][1]) / counts_test
                summe = summe + (2*(f1-f2)/(f1+f2))**2 
            
        result.append(summe)
        summe = 0    
        author = name_of_candidates[result.index(min(result))]
   
 
#    author = "oneAuthor"
    score = 1
    authors.append(author)
    scores.append(score)
    


# Save results to json-file out.json (passing 'scores' is optional)
jsonhandler.storeJson(unknowns, authors, scores)
