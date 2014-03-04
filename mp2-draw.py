#!/usr/bin/env python

import networkx as nx
import cPickle
import os
from random import randint

# Constants
size_threshold = 5
printstages = False

# "Fun"
hawaiian_islands = "Hawaii, O'ahu, Maui, Kauai, Moloka'i, Lanai, Niihau, Kaho'olawe, Kure Atoll, Nihoa, Laysan, Lisianski Island, Molokini, Gardner Pinnacles, French Frigate Shoals, Maro Reef, Pearl and Hermes Atoll, Ka'ula, Lehua, Moku Manu, Na Mokulua, Ford Island, Manana, Coconut Island, Huelo, Sand Island, Mokoli'i, Poopoo, Disappearing Island, Tern Island, Eastern Island, Moku Nui, Popoia Island, Moku'ula, Mokauea Island, Pai Island, Bare Island, New Zealand, Reeds Island, Mokolea Rock, Skate Island, Kaohikaipu Island, Alau Island, Kah'lau, Mokupapapa, Mullet Island, Mokuho'oniki, Spit Island, Kalaepohaku, Southeast Island, Mokuauia".split(", ")

# Filepath
filepath = "1"

# Load data
ch_nets = cPickle.load(open("./data/ch_" + filepath + "_net.p"))
ch_sizes = cPickle.load(open("./data/ch_" + filepath + "_sizes.p"))
ch_edges = dict()
      
# Main graphing function
def graph():

    # === Make graph ===
    G=nx.Graph()
    nodeSize = dict()
    edgeWidth = []
    
    # Add nodes
    for w in ch_sizes.keys():
      
      # Skip nodes that are too small
      if ch_sizes[w] < size_threshold:
         continue
      
      # Add node
      G.add_node(w)
      ch_edges[w] = 0
      nodeSize[w] = ch_sizes[w]
    
    edgeCount = 0
    for w_a in ch_nets.keys():
    
      # Skip nodes that are too small
      if ch_sizes[w_a] < size_threshold:
         continue
    
      for w_b in ch_nets[w_a]:
      
         # Skip nodes that are too small
         if ch_sizes[w_b] < size_threshold:
            continue
               
         # Form edge
         if not G.has_edge(w_a, w_b):
            edge = G.add_edge(w_a, w_b)
            edgeCount += 1
            ch_edges[w_a] += 1
            ch_edges[w_b] += 1
         
    #print "EDGE COUNT: " + str(edgeCount)
    return (G, nodeSize)

# Specifies node color
def node_color(w):
   if ch_edges[w] == 0:
      return '#403a36'
   elif ch_sizes[w] > size_threshold * 3:
      return '#e3bf98'
   elif ch_sizes[w] > size_threshold * 1.5:
      return '#8f532b'
   else:
      return 'g'

def main():
    import networkx as nx
    import matplotlib.pyplot as plt
    
    G_tuple = graph()
    G = G_tuple[0]
    nodeSize = G_tuple[1]
    
    try:
        pos=nx.graphviz_layout(G)
    except:
        pos=nx.spring_layout(G,iterations=20)

    stage = 1
    stages = 4

    if printstages:
      print "STAGE " + str(stage) + "/" + str(stages); stage += 1
    #plt.rcParams['text.usetex'] = False
    plt.figure(figsize=(40, 40))
    nx.draw_networkx_edges(G,
                           pos,
                           alpha=0.3,
                           width=5,
                           edge_color='black')
    if printstages:
      print "STAGE " + str(stage) + "/" + str(stages); stage += 1
    nx.draw_networkx_nodes(G,
                           pos,
                           node_size=[abs(ch_sizes[w]*250) for w in G],
                           node_color=[node_color(w) for w in G],
                           alpha=1
                           )
    if printstages:
      print "STAGE " + str(stage) + "/" + str(stages); stage += 1
    nx.draw_networkx_labels(G,pos,fontsize=25)
    font = {'fontname'   : 'Helvetica',
            'color'      : 'k',
            'fontweight' : 'bold',
            'fontsize'   : 60}
    island_num = randint(0,len(hawaiian_islands)-1)
    plt.title(hawaiian_islands[island_num] + " (Chapter " + filepath + ")", font)

    # change font and write text (using data coordinates)
    plt.axis('off')
    if printstages:
      print "STAGE " + str(stage) + "/" + str(stages); stage += 1
    plt.savefig("vizzed_ch" + filepath + ".png",
                dpi=50,
                facecolor='#83f7e2')
    print("Wrote image")
    
# Go
main()
