#!/usr/bin/python
"""
My solution to a programming assignment
for the Stanford class "Mining Massive Datasets,"
a fall 2014 MOOC taught by Jure Leskovec, 
Anand Rajaraman, and Jeff Ullman.

Task: Read in a file sentences.txt, which consists
of over 9 million sentences of 10 words or greater,
one per line (lines begin with a line number).
File originally available here:
https://d396qusza40orc.cloudfront.net/mmds/datasets/sentences.txt.zip

Output the total number of pairs of sentences which
are "edit distance" one apart, where an edit can be
an insertion, deletion, or mutation (i.e. changing one
word to another).

Strategy: Two sentences of 10+ words which differ by
one word edit must agree in either their first 5 words
exactly, or last 5 words exactly.

Thus we create two dictionaries (in other languages, we'd
use a hash table), one to hold sentence beginnings (first 5
words) and one to hold sentence endings (last 5 words).
Dictionary value is a list of line numbers of the sentences
mapping to that key ("bin").

Then we compare each pair of indices in the same bin.

Optimizations: First remove duplicate lines (counting
the remainder of the line after the initial line number)
and record, as an extra entry for each line kept, the
number of copies of that line in the original file.

Then sort lines by number of words and step through,
only ever comparing words of the same length, or of
that length and the previous length.

Result: 429493953 total matching pairs (at edit distance <= 1)
from the list of 9397023 sentences. Of these, 426873920 were
due to duplicate lines.

Running time: pre-processing phase takes ~6.5 minutes on my
Macbook Pro 2.5 GHz 16 GB (running single-threaded),
including creating a file with no duplicates and an extra field
for number of duplicates of that line, plus a file listing
line numbers of duplicates, in case this is needed later

The final counting, including reading from the pre-processed
file, takes ~3 minutes on my laptop
"""

import string
import time
import random
from math import floor
from collections import defaultdict

def edit1(s1,s2):
    """
    Takes two lists. Returns true if they differ by at most one of:
    deletion, insertion, mutation, in one element
    """    
    l1 = len(s1)
    l2 = len(s2)
    if l1 == l2:
        n = 0
        for i in xrange(l1):
            if s1[i] != s2[i]:
                n += 1
                if n == 2:
                    return False
        #eq += 1
        return True
    elif l1 == l2 - 1:
        i = 0
        j = 0
        while i < l1:
            if s1[i] != s2[j]:
                j += 1
                if j-i == 2:
                    return False
            else:
                i += 1
                j += 1
        return True
    elif l1 == l2 + 1:
        i = 0
        j = 0
        while j < l2:          
            if s1[i] != s2[j]:
                i += 1
                if i-j == 2:
                    return False
            else:
                i += 1
                j += 1
        return True
    else:
        return False

def main():
    start_time = time.time()
    
    sent_file = open("sentences.txt", "r")
    
    # compute word list and store sentence words
    
    s_list = []
    s = sent_file.readline()

    while not (s == ""):
        s_words = (s[:-1]).split()
        if len(s_words) >= 10:
            s_list.append(s_words)
        s = sent_file.readline()

    n_sent = len(s_list)
    
    sent_file.close()   

#########
    
    run_time = time.time() - start_time
    run_min = floor(run_time/60)
    run_sec = round(run_time - 60 * run_min,2)
    print "Done constructing word list"
    print "Running time: " + str(run_min) + " minutes, " + str(run_sec) + " seconds"
    start_time = time.time()
    
#########
    
    # Remove duplicates and write output files
    
    s_list.sort(key=lambda s: s[1:]) # sort by the sentence
                                     # ignoring the line number
                                     # printed in the file
    
    nodupes = open("sentnodupes.txt", "w")
    dupelist = open("sentdupelist.txt", "w")
    
    k = 0
    dup_matches = 0
    dup_count = 1
    tmp_list = []
    for k in xrange(n_sent):
        if k == n_sent - 1 or s_list[k][1:] != s_list[k+1][1:]:
            # output unique sentences, with the number of duplicates of
            # that sentence appended to the end
            nodupes.write(" ".join(s_list[k]) + " " + str(dup_count) + "\n")
            if dup_count > 1:
                # count matches due to duplicates
                dup_matches += (dup_count * (dup_count - 1))/2
                # write duplicates to file in case they're needed later
                dupelist.write(s_list[k][0] + " " + " ".join(tmp_list) + "\n")
                dup_count = 1
                tmp_list = []
        else:
            dup_count += 1
            tmp_list.append(s_list[k][0])
    
    print "
    
    nodupes.close()
    dupelist.close()
    
    del s_list
    
    print "Total matches due to duplicates: " + str(dup_matches)
    
#########
    
    run_time = time.time() - start_time
    run_min = floor(run_time/60)
    run_sec = round(run_time - 60 * run_min,2)
    print "Done printing duplicate free file and duplicate list"
    print "Running time: " + str(run_min) + " minutes, " + str(run_sec) + " seconds"
    start_time = time.time()

#########
              
    # END PRE-PROCESSING PHASE
    # SCRIPT WILL CONTINUE TO DETERMINE TOTAL
    # NUMBER OF MATCHES
    
    # TO RUN THE NEXT PART SEPARATELY, COMMENT OUT THE ABOVE
    # AND PUT THE RESULT PRINTED OUT FOR dup_matches HERE:
                
    tot = dup_matches # new variable to count total matches starting
                      # with the total coming from duplicated lines
        
    nodupes_read = open("sentnodupes.txt", "r")
    
    # compute duplicate free word list and store sentence words
    
    s_list = []
    s = nodupes_read.readline()

    while not (s == ""):
        s_words = (s[:-1]).split()
        if len(s_words) >= 10:
            s_list.append(s_words)
        s = nodupes_read.readline()

    n_sent = len(s_list)
    
    sent_file.close()    
    
    s_list.sort(key=len)
    
#########
    
    run_time = time.time() - start_time
    run_min = floor(run_time/60)
    run_sec = round(run_time - 60 * run_min,2)
    print "Done reading duplicate free list and sorting by number of words"
    print "Running time: " + str(run_min) + " minutes, " + str(run_sec) + " seconds"
    start_time = time.time()
    
#########

    h1o = defaultdict(list) # for odd sentence word length
    h2o = defaultdict(list)
    
    h1e = defaultdict(list) # for even sentence word length
    h2e = defaultdict(list)
    
    h1 = [h1e,h1o]    # two dictionaries to store first 5
    h2 = [h2e,h2o]    # and last 5 words as keys, with lists
                      # of sentence numbers as values
                   
    match1 = set()    # to store the list of values
                      # as tuples (index 1, index 2, weight)
                      # where weight is the product of the number
                      # of duplicates of the two sentences
    
    p = 12
    i = 0
    while(True):
        if (i == n_sent or len(s_list[i]) > p):
            # get all pairs of length p
            for k in h1[p%2].keys():
                for m in xrange(len(h1[p%2][k])):
                    ind1 = h1[p%2][k][m]
                    for n in xrange(m+1,len(h1[p%2][k])):
                        ind2 = h1[p%2][k][n]
                        if edit1(s_list[ind1][1:-1],s_list[ind2][1:-1]):
                            mult = int(s_list[ind1][-1]) * int(s_list[ind2][-1])
                            if ind1 < ind2:
                                match1.add((ind2,ind1, mult))
                            else:
                                match1.add((ind2,ind1, mult))
            for k in h2[p%2].keys():
                for m in xrange(len(h2[p%2][k])):
                    ind1 = h2[p%2][k][m]
                    for n in xrange(m+1,len(h2[p%2][k])):
                        ind2 = h2[p%2][k][n]
                        if edit1(s_list[ind1][1:-1],s_list[ind2][1:-1]):
                            mult = int(s_list[ind1][-1]) * int(s_list[ind2][-1])
                            if ind1 < ind2:
                                match1.add((ind2,ind1, mult))
                            else:
                                match1.add((ind2,ind1, mult))
            tmp = 0
            for m in match1:
                tmp += m[2]
            tot += tmp
            del match1
            match1 = set()
            
            # get all pairs of length p & p-1
            for k in h1[p%2].keys():
                if h1[(p+1)%2].get(k,-1) != -1:
                    for m in xrange(len(h1[p%2][k])):
                        ind1 = h1[p%2][k][m]
                        for n in xrange(len(h1[(p+1)%2][k])):
                            ind2 = h1[(p+1)%2][k][n]
                            if edit1(s_list[ind1][1:-1],s_list[ind2][1:-1]):
                                mult = int(s_list[ind1][-1]) * int(s_list[ind2][-1])
                                if ind1 < ind2:
                                    match1.add((ind2,ind1,mult))
                                else:
                                    match1.add((ind2,ind1,mult))
            for k in h2[p%2].keys():
                if h2[(p+1)%2].get(k,-1) != -1:
                    for m in xrange(len(h2[p%2][k])):
                        ind1 = h2[p%2][k][m]
                        for n in xrange(len(h2[(p+1)%2][k])):
                            ind2 = h2[(p+1)%2][k][n]
                            if edit1(s_list[ind1][1:-1],s_list[ind2][1:-1]):
                                mult = int(s_list[ind1][-1]) * int(s_list[ind2][-1])
                                if ind1 < ind2:
                                    match1.add((ind2,ind1,mult))
                                else:
                                    match1.add((ind2,ind1,mult))
            tmp = 0
            for m in match1:
                tmp += m[2]
            tot += tmp
            del match1
            match1 = set()
            
            h1[(p+1)%2] = defaultdict(list)
            h2[(p+1)%2] = defaultdict(list)
            p += 1
            if i == n_sent:
                break      
        else:
            # add the sentence to the dictionaries
            cur_list = s_list[i]
            cur_str = ' '.join(cur_list[1:6])
            h1[p%2][cur_str].append(i)
            cur_str = ' '.join(cur_list[-6:-1])
            h2[p%2][cur_str].append(i)
            i += 1            
        
#########
    
    run_time = time.time() - start_time
    run_min = floor(run_time/60)
    run_sec = round(run_time - 60 * run_min,2)
    print "Done counting: " + str(tot) + " matches!"
    print "Running time: " + str(run_min) + " minutes, " + str(run_sec) + " seconds"
    start_time = time.time()
    
#########

if __name__ == "__main__":
    main()