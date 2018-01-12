import re
import numpy as np
import pandas as pd
import os, errno
import configparser

# A regex pattern for replacing all of the punctuation in one pass
replace_chars = [".", "?", "!", "\\", "(", ")", ",", "/", "*", "&", "#", "\"",
                ";", ":", "-", "_", "=", "@", "[", "]", "+", "$", "~", "'", "`", '\\\"']
replace_chars = set(re.escape(k) for k in replace_chars)
pattern = re.compile("(" + "|".join(replace_chars) + ")")

def get_nums(word_list, word_numbers, word_numbers_list, number):
    '''
    Given a list of words from a csv cell, returns a string of cleansed words.
    INPUTS:
        word_list (list): the original words
        word_numbers (dict): contains parings of word -> number
        word_numbers_list (list of lists): contains words, numbers, count (initialized to None)
    OUTPUT:
        return_string (string): the string of numbers to stand in for the original words
    '''
    for word in word_list:
        if word not in word_numbers:
            # Dictionary of {word -> [number, count]}
            word_numbers[word] = [number, 1]
            # List of lists with the form [[word, number]]
            word_numbers_list.append([word, number])
            number += 1
        else:
            # Increases count by 1 if already in dictionary
            word_numbers[word][1] += 1

    return number

def replace_words(word_list, word_numbers):
    '''
    Given a list of words from a csv cell, returns a string of cleansed words.
    INPUTS:
        word_list (list): the unhased words
        word_numbers (dict): contains parings of word -> number
        word_numbers_list (list of lists): contains words, numbers
        bottom_thresh (int): only replace the word if count above this
        top_thresh (int): only replace the word if count below this
    OUTPUT:
        return_string (string): the string of numbers to stand in for the original words
    '''
    replace_string = ""
    for word in word_list:
        # Retrieves the shuffled number for that word
        word_number = word_numbers[word][0]
        replace_string += str(word_number) + " "

    return replace_string


def assign_or_replace_text(uncleansed_text, punctuation, word_numbers, word_numbers_list, assign, ps, stemming):
    '''
    Loops through the uncleansed text. Depending on assign (bool), performs one of 
    two options. Either assigns ascending numbers to the unique words OR, after shuffling,
    creates a new series of cleansed text.
    INPUTS:
        uncleansed_text (Series): the column to be cleansed
        punctuation (bool): if punctuation should be removed
        word_numbers (dict): to be filled on first pass with word -> number representative
            later to be used to replace words with shuffled numbers
        word_numbers_list (list of lists): same info as above
        assign (bool): tells whether to run to assign numbers or to retrieve numbers
        bottom_thresh (int): only replace the word if count above this
        top_thresh (int): only replace the word if count below this
    OUTPUTS:
        Nothing on the first pass. Populates word_numbers and word_numbers_list
        cleansed_text (List of strings): the text with the shuffled numbers
    '''
    if assign:
        number = 1 #Only used in the first pass
    else:    
        cleansed_text = [] #Only used in the second pass
    
    for text in uncleansed_text:
        # Only performs punctuation stripping and splitting if the field is a string
        if type(text) is str:
            if punctuation:
                post_punc = pattern.sub("", text)
            else:
                # Isolates punctuation to be treated as an individual word
                post_punc = pattern.sub(r' \1 ', text)
                
            if case_sensitive:
                words_list = post_punc.split()
            else:
                words_list = post_punc.lower().split()
            
            if stemming:
                words_list = [ps.stem(i) for i in words_list]
        # If the field is not a string, simply sends the whole field to be numerated 
        else: 
            words_list = [text]
            
        if assign:
            number = get_nums(words_list, word_numbers, word_numbers_list, number)
        else:
            replace_string = replace_words(words_list, word_numbers)
            cleansed_text.append(replace_string)
    
    if not assign:
        return cleansed_text

def get_top_and_bottom_thresholds(top_thresh, bottom_thresh, word_numbers_df):
    '''
    If top_thresh or bottom_thresh was set to "Ask" in the config file, shows the user the
    head or tail of the dataset and asks for the desired count. 
    INPUTS:
        top_thresh (string): contains either an int or "Ask"
        bottom_thresh (string): contains either an int or "Ask"
    OUTPUTS:
        top_thresh (int): the desired top threshold, as an integer
        bottom_thresh (int): the desired bottom threshold, as an integer
    '''
    if top_thresh.lower() == "ask":
        print(word_numbers_df.head(20),  "\n")
        top_thresh = input("Combine words with counts above: ")
    try:
        top_thresh = int(top_thresh)
    except ValueError:
        print("combine_above was not a valid number. Please enter an integer")
        
    if bottom_thresh.lower() == "ask":
        print("\n", word_numbers_df.tail(20), "\n")
        bottom_thresh = input("Combine words with counts below: ")
    try:
        bottom_thresh = int(bottom_thresh)
    except ValueError:
        print("combine_below was not a valid number. Please enter an integer")
    
    return top_thresh, bottom_thresh


if __name__ == "__main__":
    '''
    Replaces the text of a given column in a csv file with randomized numbers,
    exporting the original file with the given column removed and with the new
    column added. Exports another csv file with the mapping of orignal words to numbers.
    '''
    config = configparser.ConfigParser()
    config.read('obscuritext_configs.ini')

    #Configurations 
    file_name = config['Data']['file_name']
    column_name = config['Data']['column_name']
    delete_orig = config.getboolean('Data', 'delete_column')
    
    case_sensitive = config.getboolean('Processing', 'case_sensitive')
    stemming = config.getboolean('Processing', 'stemming')
    seed = int(config['Processing']['random_seed'])
    punctuation = config.getboolean('Processing', 'remove_punctuation')
    top_thresh = config['Processing']['combine_above']
    bottom_thresh =config['Processing']['combine_below']
    
    if stemming:
        from nltk.stem import PorterStemmer
        ps = PorterStemmer()
    else:
        ps = None
    
    #Contains a dictionary of uncleansed word -> [number of word, count]
    word_numbers = {}
    #Contains the same information for export to csv (using list of lists for efficiency)
    word_numbers_list = []

    csv_df = pd.read_csv(file_name + ".csv", encoding = "ISO-8859-1")
    uncleansed_text = csv_df[column_name]

    #The first pass through assign_or_replace_text to assign ascending numbers 
    assign_or_replace_text(uncleansed_text, punctuation, word_numbers, word_numbers_list, True, ps, stemming)
    
    #Fetches the counts of the words, in order, to be filled into the word_numbers_df created below
    counts = []
    for word, number in word_numbers_list:
        counts.append(word_numbers[word][1])
        

    #Assigns the proper counts, and sorts by them
    word_numbers_df = pd.DataFrame(word_numbers_list, columns=["Original_Word", "Number"])
    word_numbers_df["Count"] = counts
    word_numbers_df.sort_values(by = "Count", ascending=False, inplace=True)
    
    #If the user hasn't already picked thresholds, asks for them.
    top_thresh, bottom_thresh = get_top_and_bottom_thresholds(top_thresh, bottom_thresh, word_numbers_df)
    
    #Shuffles the numbers 
    np.random.seed(seed)
    word_numbers_df["Number"] = np.random.permutation(word_numbers_df["Number"])
    
    # Retrieves the first word's number above the user count threshold (if it exists) and sets them all to it.
    above_thresh_nums = list(word_numbers_df[(word_numbers_df.Count > top_thresh)].Number)
    if len(above_thresh_nums) != 0: 
        above_thresh_num = above_thresh_nums[0]
        word_numbers_df.loc[word_numbers_df.Count > top_thresh, 'Number'] = above_thresh_num
    
    
    # The same process for the words below the bottom threshold
    below_thresh_nums = list(word_numbers_df[(word_numbers_df.Count < bottom_thresh)].Number)
    if len(below_thresh_nums) != 0: 
        below_thresh_num = below_thresh_nums[0]
        word_numbers_df.loc[word_numbers_df.Count < bottom_thresh, 'Number'] = below_thresh_num
    
    # Refills the dictionary of {words -> [number, count]} with the shuffled numbers
    for row in word_numbers_df.itertuples():
        word_numbers[getattr(row, "Original_Word")][0] = getattr(row, "Number")
    
    # Iterates back over the text, replacing the words with their shuffled numbers
    cleansed_text = assign_or_replace_text(uncleansed_text, punctuation, word_numbers, word_numbers_list, False, ps, stemming)

    csv_df["Cleansed_"+ column_name] = cleansed_text
    if delete_orig: 
        del csv_df[column_name]
    # Creates a subdirectory to store the cleansed files
    try:
        os.makedirs(r"./cleansed_" + file_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    path = r"./cleansed_" + file_name + r"/"
    csv_df.to_csv(path + "cleansed_" + column_name + "_" + file_name + ".csv")
    word_numbers_df.to_csv( path + file_name + "_" + column_name + "_numbers.csv", index=False)
    
    print(len(word_numbers_df), "unique words numeralized from", len(uncleansed_text), "lines.")