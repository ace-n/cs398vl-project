# FOR GRAPH GENERATION: http://networkx.lanl.gov/index.html
import json
import nltk
from nltk.corpus import brown, PlaintextCorpusReader
from nltk.corpus import wordnet as wn
import cPickle
import copy
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import RegexpStemmer
import networkx as nx

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

# Count number of synonyms of a word in a paragraph
def count_total_synonyms(word, paragraph, st):
   st_syns = list(set([st.stem(s.lemma_names[0]) for s in wn.synsets(word)]))
   count = 0

   for sent in paragraph:
      for word in sent:

         # Hacky fix based on observations
         if word.lower() == "in":
            continue

         st_word = st.stem(word)
         for st_s in st_syns:

            if st_s == st_word:
               count += 1
               #print "\t" + st_word
    
   # Done!
   return count

def get_corr_coefs(wordlists, st, words, paras, print_out, motifs):

   # Get raw syncounts
   freqs = dict()
   syncounts = dict()
   output = ""
   for m in motifs:
      arr = []
      freqs[m] = 0
      for p in paras:
         syncnt = float(count_total_synonyms(m,p,st))
         arr.append(syncnt)
         freqs[m] += syncnt
      syncounts[m] = arr
        
   # Get correlations
   corrs = dict()
   for m1 in motifs:      
   
      if m1 not in corrs:
         corrs[m1] = dict()
      d1 = syncounts[m1]
      
      for m2 in motifs:
      
         if m2 not in corrs:
            corrs[m2] = dict()

         # Skip equals/repeats
         if m1 <= m2:
            continue
         d2 = syncounts[m2]
          
         # Find correlation coefficient (not the STAT400 one)
         corr_modded = False
         corr_coef = 0.0
         for i in range(0,len(d1)):

            a = float(min(d1[i], d2[i]))
            b = float(max(d1[i], d2[i]))
              
            # Skip pairs that have no occurrences of either word
            if b == 0:
               continue

            # The greater the magnitude of this, the more the paragraphs are correlated
            corr = a/b
            corr_coef += corr

            one_is_null = len(m1) == 0 or len(m2) == 0

            if (corr != 0) or one_is_null:
               corr_modded = not one_is_null # If either is '', we're just concerned about 1 motif
               
               if print_out:
                  output += "<p>" + generate_blurb(m1, m2, paras[i], st) + "</p><hr>\n"
               
         if corr_modded:
            corrs[m1][m2] = corr_coef
            corrs[m2][m1] = corr_coef
            #print m1 + " --> " + m2 + ":\t\t" + str(corr_coef)
                
   # Done!
   return (corrs, freqs, output)

# Generates an HTML block for each paragraph with the appropriate word coloring
def generate_blurb(m1, m2, paragraph, st):

   if m1 < m2:
      temp = m1
      m1 = m2
      m2 = temp

   st_syns1 = list(set([st.stem(s.lemma_names[0]) for s in wn.synsets(m1)]))
   st_syns2 = list(set([st.stem(s.lemma_names[0]) for s in wn.synsets(m2)]))

   # Get paragraph
   para_str = ""
   for sent in paragraph:
      for word in sent:

         # Punctuation
         if len(word) == 1 and word not in "abcdefghijklmnopqrstuvwxyz":
            para_str += word + ""
            continue

         # Actual words
         st_word = st.stem(word)
         cond1 = st_word in st_syns1 and word.lower() != "in" # In showed up way too much during testing
         cond2 = st_word in st_syns2 and word.lower() != "in"
         if len(para_str) != 0 and para_str[-1] in "'-":
             para_str += word
         elif cond1 and cond2 :
             para_str += " <b><font color='purple'>" + word + "</font></b>"
         elif cond1:
             para_str += " <b><font color='red'>" + word + "</font></b>"
         elif cond2:
             para_str += " <b><font color='blue'>"+ word + "</font></b>"
         else:
             para_str += " " + word
    
   # Done!
   return para_str

# Misc. minor functions
def smin(a,b):
  return (a if a <=b else b)
  
def smax(a,b):
  return (b if a <b else a)

def quotify(s):
  return "\"" + s + "\""

# Function that coordinates tasks for a particular chapter
def main(print_out, motifs, chapter):
   wordlists = PlaintextCorpusReader('', 'Punctuated/pot_ch[12345]\.txt')

   #rep_words = nltk.FreqDist(brown.words()) # Get representative word counts

   st = LancasterStemmer()
   #st = RegexpStemmer('ing$|s$|e$', min=4)

   for i in range(1,6): 
   
      if i != chapter:
        continue   
   
      g = nx.Graph()

      words = wordlists.words('Punctuated/pot_ch{!s}.txt'.format(str(i)))
      paras = wordlists.paras('Punctuated/pot_ch{!s}.txt'.format(str(i)))

      # Generate HTML
      #with open("test" + str(i) + ".txt", "w+") as fi:
      #   output = generate_html_level2(wordlists, st, words, paras, i)
      #   fi.write(output)
      
      json_dict = {}
      json_dict["nodes"] = []
      json_dict["edges"] = []

      # Get correlation coefficients
      corr_data = get_corr_coefs(wordlists, st, words, paras, print_out, motifs)
      corr_coefs = corr_data[0]
      corr_freqs = corr_data[1]

      # ---------------------------------- NetworkX ----------------------------------
      # Get NetworkX nodes
      nx_added_nodes = []
      for m1 in corr_coefs:
         g.add_node(m1)

      # Get NetworkX edges
      for m1 in corr_coefs:
         for m2 in corr_coefs[m1]:

             # Avoid repeats
             if m1 <= m2:
                 continue

             g.add_edge(m1, m2)

      # -------------------------------- End NetworkX --------------------------------

      # -------------------------------------- d3.js --------------------------------------
      # Get d3-js nodes
      json_node_numbers = dict()
      square_size = 0
      for m1 in corr_coefs:

         sz = int(min(corr_freqs[m1]/3.0,50))*3
         #print sz

         json_node  = {
                                    "name": m1,
                                    "size": str(sz),
                                    "color": "#aaaaaa"
                                }
         json_dict["nodes"].append(json_node)
         json_node_numbers[m1] = len(json_node_numbers)

      # Get d3-js edges
      m1m2 = 0;
      for m1 in corr_coefs:
         for m2 in corr_coefs[m1]:

             # Avoid repeats
             if m1 <= m2:
                 continue

             # No need to worry about repeats, since corr_coefs won't contain them
             edge_size = corr_coefs[m1][m2]
             #print "ES " + m1 + "/" + m2 + ": " + str(edge_size)
             json_edge = {
                                   "name": m1 + "-" + m2,
                                   "source": json_node_numbers[m1],
                                   "target": json_node_numbers[m2],
                                   "size": str(edge_size)
                                   }
             json_dict["edges"].append(json_edge)

      # Add boundary d3-js node
      json_dict["nodes"].append({"id":"the-end",
                                                    "x":square_size,
                                                    "y":square_size,
                                                    "size":"1",
                                                    "color":"#000000"
      })

      # Write JSON to file
      if not print_out:
          with open("OFFICIAL/data" + str(i) + ".json", "w+") as fi:
            fi.write("var json_str_" + str(i) + "=" + json.dumps(json_dict, fi, indent = 2))
      else:
          mn = smin(motifs[0],motifs[1])
          mx = smax(motifs[0],motifs[1])

          path = "OFFICIAL/inserts/" + mn + ("-" if len(mn) != 0 else "") + mx + "-" + str(chapter) + ".html"
          print path
          with open(path, "w+") as fi:
             fi.write(corr_data[2])

# --- Runner helper function ---
def run(args, chapter):
    print "Running " + str(args) + "."
    print_out = False
    if len(args) > 2:
        motifs = args[1:3]
        print "MOTIFS: " + str(motifs)
        print_out = True
    main(print_out, motifs, chapter)
    
# --- Run data generation ---
motifs_all = ["light", "dark",
          "hot", "cold", "wet", "dry",
          "good", "bad", "evil"]

# Chapter graphs
if False:
    for i in range(1,6):
        run([''], i)
    
# Motif pairs
for m1 in motifs_all:
    for m2 in motifs_all:
    
        if m1 <= m2:
            continue
            
        for i in range(1,6):
            pass
            #run(['',m1,m2], i)
        
# Individual motifs
for m1 in motifs_all:
    for i in range(1,6):
        run(['',m1,''], i)


