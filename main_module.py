'''

@author: maxx
'''

import queue
import threading
import itertools
import hashlib

#input anagram phrase, without spaces
anagram_phrase = "poultryoutwitsants"
#queue for sending information to the calculator_md5 thread
queue_anagrams = queue.Queue()
#set of md5's to be found
md5_list = {'665e5bcb0c20062fe8abaaf4628bb154', 'e4820b45d2277f3844eac66c903e84be', '23170acc097c24edb98fc5488ab033fe'}
#program finish flag. It is not thread safe since it transfers data only in one direction. The event would be more correct
finish_flag = False

def calculator_md5():
    '''
    This is the thread which 
        get list of the words (suitable for anagram), 
        gets all permutations
        calculate md5's and compare with targets md5's
        also responsible for the program finishing
    '''
    global md5_list, finish_flag
    while True:
        #get element for calculating
        item = queue_anagrams.get()
        if item is None:
            break
        for i in itertools.permutations(item):
            # calculate md5 for all permutations
            if hashlib.md5(" ".join(i).encode('utf-8')).hexdigest() in md5_list:
                print(hashlib.md5(" ".join(i).encode('utf-8')).hexdigest() + " - " + " ".join(i))
                # not need md5 collisions
                md5_list = md5_list - {hashlib.md5(" ".join(i).encode('utf-8')).hexdigest()} 
                if not len(md5_list):
                    #all md5's are calculated - can finish the program
                    print("finish")
                    finish_flag = True
                    return True

def check_word2(stack, word, position_word):
    '''
    This function append word (with settings) to the stack if this word suitable for anagram (particulary)
    return True if word particulary suitable for anagram
    return False if word not suitable for anagram OR if all stack is a complete anagram
    '''
    #if length of the word is bigger of the anagram rest
    #OR rest of anagram length is = 1 (not available since we did not take into account words with a length of 1 (removed such words from the list))  
    #(word not suitable for anagram)
    if stack[-1][0] < len(word) or len(word) + 1 == stack[-1][0]:
        return False
    #should to use copy to prevent modify stack data
    anagram_dict_copy_copy = stack[-1][1].copy()
    for letter in word:
        if anagram_dict_copy_copy[letter] < 1:
            #in the incoming word, the letters do not fit the anagram
            return False
        anagram_dict_copy_copy[letter] -= 1
    if stack[-1][0] == len(word):
        # if we find the anagram fit 
        tmp = [x[3] for x in stack[1:]]
        tmp.append(word)
        #sending this data to the md5 calculator thread
        queue_anagrams.put(tmp)
        #and return False to move forward
        return False
    # particularly fit brunch
    stack.append([stack[-1][0] - len(word), anagram_dict_copy_copy, position_word, word])
    return True

def main():
    '''
    the main func
    '''
    #creating calculator_md5 thread
    threading.Thread(target=calculator_md5).start()
    #this dict contain letters from the input anagram (keys) and count of this letter in the input anagram (values)
    #for example {'a':2, 'b':1}
    anagram_dict = {}
    for letter in anagram_phrase:
        anagram_dict[letter] = anagram_dict.get(letter, 0) + 1
    #contains all words from the lexicon file 'wordlist'
    all_words_list = []

    flag = True
    # filling all_words_list
    # removing 1-letter words, duplicates
    # sorting by word length
    with open("wordlist", "r") as fil:
        for line in fil:
            flag = True
            line = line.strip()
            if len(line) == 1:
                continue
            for letter in line:
                if letter not in anagram_dict:
                    flag = False
                    break
            if flag:
                anagram_dict_copy = anagram_dict.copy()
                for letter in line:
                    if anagram_dict_copy[letter] < 1:
                        flag = False
                        break
                    anagram_dict_copy[letter] -= 1
                if flag:
                    all_words_list.append(line)
    all_words_list = list(set(all_words_list))
    all_words_list.sort(key=len, reverse=True)

    # using stack and recursion-like brute-force
    # combine words from the longest to the shortest
    i = 0
    stack = [[len(anagram_phrase), anagram_dict, -1, ""]]
    
    #finishing program from the middle of the loop
    while True:
        #
        while i < len(all_words_list):
            if check_word2(stack, all_words_list[i], i):
                #word is added if it fits the anagram
                i += 1
                break
            i += 1
        if i == len(all_words_list):
            #if we went through the entire lexicon
            if finish_flag:
                # all three md5's was found
                return
            #take a step back on the stack
            i = stack[-1][2] + 1
            if len(stack) == 2 and i == len(all_words_list):
                #all combinations are finished
                return
            stack.pop()

if __name__ == '__main__':
    main()
    