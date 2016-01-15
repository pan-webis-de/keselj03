# corpusdir - name of subdir with corpus
# META_FNAME - name of the meta-file.json
# OUT_FNAME - file to write the output in (out.json)
# upath - path of the 'unknown' dir in the corpus (from json)
# candidates - list of candidate author names (from json)
# unknowns - list of unknown filenames (from json)
# trainings - dictionary with lists of filenames of trainingstexts for each author
# 	{"candidate2":["file1.txt", "file2.txt", ...], "candidate2":["file1.txt", ...] ...}

# Usage:
# loadJson(corpusname), with corpusname from commandline
# OPTIONAL: loadTraining()
# OPTIONAL: getTrainingText(jsonhandler.candidate[i], jsonhandler.trainingss[jsonhandler.candidates[i]][j]), gets trainingsstext j from candidate i as a string
# getUnknownText(jsonhandler.unknowns[i]), gets unknown text i as a string
# storeJson(candidates, texts, scores), with list of candidates as
# candidates (jsonhandler.candidates can be used), list of texts as texts
# and list of scores as scores, last argument can be ommitted

import math
import os
import json


class Jsonhandler:

    def __init__(self, corpus, meta="meta-file.json", out="out.json"):
        self.META_FNAME = meta
        self.OUT_FNAME = out
        self.corpusdir = corpus
        with open(os.path.join(self.corpusdir, self.META_FNAME), "r") as mfile:
            self.metajson = json.load(mfile)
        self.upath = os.path.join(self.corpusdir, self.metajson["folder"])

        self.candidates = [author["author-name"]
                           for author in self.metajson["candidate-authors"]]
        self.trainings = dict()
        self.unknowns = []
        self.ground_truth = None

    def loadTraining(self, ratio=0.1):
        self.ground_truth = dict()
        self.unknowns = []
        for cand in self.candidates:
            texts = []
            for subdir, dirs, files in os.walk(os.path.join(self.corpusdir, cand)):
                for doc in files:
                    texts.append(doc)
            split = int(math.ceil(ratio * len(texts)))
            # make that every author has at least one known text
            if split == len(texts):
                split = len(texts) - 1
            for doc in texts[:split]:
                complete_path = os.path.join(self.corpusdir, cand, doc)
                self.unknowns.append(complete_path)
                self.ground_truth[complete_path] = cand
            self.trainings[cand] = texts[split:]

    def loadTesting(self):
        self.groundtruth = None
        self.unknowns = [os.path.join(self.upath, text["unknown-text"]) for
                         text in self.metajson["unknown-texts"]]
        for cand in self.candidates:
            self.trainings[cand] = []
            for subdir, dirs, files in os.walk(os.path.join(self.corpusdir, cand)):
                for doc in files:
                    self.trainings[cand].append(doc)

    def getUnknownText(self, fname):
        dfile = open(fname)
        s = dfile.read()
        dfile.close()
        return s

    def getTrainingText(self, cand, fname):
        dfile = open(os.path.join(self.corpusdir, cand, fname))
        s = dfile.read()
        dfile.close()
        return s

    def evalTesting(self, texts, cands, scores=None):
        succ = 0
        fail = 0
        sucscore = 0
        failscore = 0
        for i in range(len(texts)):
            if self.ground_truth[texts[i]] == cands[i]:
                succ += 1
                if scores != None:
                    sucscore += scores[i]
            else:
                fail += 1
                if scores != None:
                    failscore += scores[i]
        result = {"fail": fail, "success": succ, "accuracy":
                  succ / float(succ + fail)}
        return result

    def storeJson(self, texts, cands, scores=None, path=None):
        answers = []
        if scores == None:
            scores = [1 for text in texts]
        if path == None:
            path = self.corpusdir
        for i in range(len(texts)):
            answers.append({"unknown_text":
                            os.path.basename(texts[i]), "author": cands[i], "score": scores[i]})
        f = open(os.path.join(path, self.OUT_FNAME), "w")
        json.dump({"answers": answers}, f, indent=2)
        f.close()
