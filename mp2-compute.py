# FOR GRAPH GENERATION: http://networkx.lanl.gov/index.html
import json
import nltk
from nltk.corpus import brown, PlaintextCorpusReader
from nltk.corpus import wordnet as wn
import cPickle
import copy

# Get (relative) frequencies of words
def get_freqs(chapter, wordlists, rep_words):

   ch_words = wordlists.words('Nopunct/ofk_ch{!s}.txt'.format(str(chapter)))
   ch_freqs = nltk.FreqDist(ch_words) # Frequency dictionary (key = word; value = freq.)
   
   # Normalize frequencies
   ch_freq_table = dict()
   for w in ch_freqs:
      ch_freq_table[w] = float(ch_freqs[w]*5) / float(rep_words.get(w,1))
   
   # Done!
   return ch_freq_table

# Helper function that gets the "best" sense of a word (based on synonym counts)
# - Doesn't really work with n-grams (where n > 1), but is a pretty general/simple method for now
def get_best_sense(word, ch_freqs):

   bestSense = None
   bestScore = -1
   
   for synset in wn.synsets(word):
   
      curScore = 0.005
   
      for lname in synset.lemma_names:
         curScore += 0.0 if lname not in ch_freqs else ch_freqs[lname]
         
      if curScore > bestScore:
         bestScore = curScore
         bestSense = synset
         
   return bestSense

# Recursive helper function (for hypernym net system)
def add_to_net(w_cur, w_child, ch_hypernyms, ch_sizes):

   w_cur_str = str(w_cur)[8:-2]
   w_child_str = str(w_child)[8:-2]

   # Base case: parent is already in the hypernyms list
   if w_cur_str in ch_hypernyms and w_child_str in ch_hypernyms[w_cur_str]:
      return
      
   # Recursive case (pt 1/2): add current word to hypernym tree
   if w_cur_str not in ch_hypernyms:
      ch_hypernyms[w_cur_str] = []
      ch_sizes[w_cur_str] = 0
   if w_child_str not in ch_hypernyms[w_cur_str]:
      ch_hypernyms[w_cur_str].append(w_child_str)
      ch_sizes[w_cur_str] += ch_sizes[w_child_str]
         
   # Recursive case (pt 2/2): repeat the following procedure for w_cur's hypernyms
   cur_hypernyms = w_cur.hypernyms()
   for h in cur_hypernyms:
      add_to_net(h, w_cur, ch_hypernyms, ch_sizes)
   

# Get hypernym relationships between words
def get_hypernym_net(chapter, wordlists, ch_freqs):
      
   # Init hypernym net
   ch_hypernyms = dict()
   ch_sizes = dict()
   for w in ch_freqs:
      
      # Get most common sense (only applies to leaves)
      bestSense = get_best_sense(w, ch_freqs)
      
      # If wordNet doesn't understand the word, skip it
      if bestSense is None:
         print "skipped " + w
         continue
   
      # Add this sense to the hypernym net (recursively)
      for h in bestSense.hypernyms():
         h_str = str(h)[8:-2]
         ch_hypernyms[h_str] = []
         ch_sizes[h_str] = 1
         add_to_net(bestSense, h, ch_hypernyms, ch_sizes)
   
   # Done!
   return (ch_hypernyms, ch_sizes)

def main():
   wordlists = PlaintextCorpusReader('', 'Nopunct/ofk_ch[123]\.txt')

   rep_words = nltk.FreqDist(brown.words()) # Get representative word counts

   for i in range(1,4): 
      ch_freqs = get_freqs(1, wordlists, rep_words)
      tupperware = get_hypernym_net(1, wordlists, ch_freqs)
      
      ch_hynet = tupperware[0]
      ch_sizes = tupperware[1]
   
      #print hynet
      cPickle.dump(ch_hynet, open("data/ch_" + str(i) + "_net.p", "wb"))
      cPickle.dump(ch_sizes, open("data/ch_" + str(i) + "_sizes.p", "wb"))

# Do something
main()
