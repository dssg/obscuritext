import re
import numpy as np
import pandas as pd
import os, errno

# A regex pattern for replacing all of the punctuation in one pass
replace_chars = [".", "?", "!", "\\", "(", ")", ",", "/", "*", "&", "#", "\"",
                ";", ":", "-", "_", "=", "@", "[", "]", "+", "$", "~", "'", "`", '\\\"']
replace_chars = set(re.escape(k) for k in replace_chars)
pattern = re.compile("(" + "|".join(replace_chars) + ")")

def get_nums(word_list, word_numbers, word_numbers_list, number):
    '''
    Given a list of words from a csv cell, returns a string of cleansed words.
    INPUTS:
        word_list (list): the unhased words
        word_numbers (dict): contains parings of word -> number
        word_numbers_list (list of lists): contains words, numbers
    OUTPUT:
        return_string (string): the string of numbers to stand in for the original words
    '''
    for word in word_list:
        if word not in word_numbers:
            word_numbers[word] = number
            word_numbers_list.append([word, number])
            number += 1

    return number

def replace_words(word_list, word_numbers):
    '''
    Given a list of words from a csv cell, returns a string of cleansed words.
    INPUTS:
        word_list (list): the unhased words
        word_numbers (dict): contains parings of word -> number
        word_numbers_list (list of lists): contains words, numbers
    OUTPUT:
        return_string (string): the string of numbers to stand in for the original words
    '''
    replace_string = ""
    for word in word_list:
        word_number = word_numbers[word]
        replace_string += str(word_number) + " "

    return replace_string


def assign_or_replace_text(uncleansed_text, punctuation, word_numbers, word_numbers_list, assign):
    '''
    Loops through the uncleansed text. Depending on assign (bool), performs one of 
    two options. Either assigns ascending numbers to the unique words OR, after shuffling,
    creates a new series of cleansed text.
    INPUTS:
        uncleansed_text (Series): the column to be cleaned
        punctuation (bool): if punctuation should be treated as a word
        word_numbers (dict): to be filled on first pass with word -> number representative
            later to be used to replace words with shuffled numbers
        word_numbers_list (list of lists): same info as above
        assign (bool): tells whether to run to assign numbers or to retrieve numbers
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
                post_punc = pattern.sub(r' \1', text)
            else:
                post_punc = pattern.sub("", text)
            words_list = post_punc.lower().split()
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
    

if __name__ == "__main__":
    '''
    Replaces the text of a given column in a csv file with randomized numbers,
    exporting the original file with the given column removed and with the new
    column added. Exports another csv file with the mapping of orignal words to numbers.
    '''

    file_name = input("Enter the name of your csv (not including extension): ")
    column_name = input("Enter the name of the column to cleanse: ")
    seed = int(input("Enter a seed for randomizing (int): "))
    delete_orig = input("Would you like to delete the original column (Y/N)? ").lower() == "y"
    punctuation = input("Would you like to treat punctuation as words (Y/N)? ").lower() == "y"    
    

    #Contains a dictionary of uncleansed word -> number of word
    word_numbers = {}
    #Contains the same information for export to csv (using list of lists for efficiency)
    word_numbers_list = []

    csv_df = pd.read_csv(file_name + ".csv")
    uncleansed_text = csv_df[column_name]

    #The first pass through assign_or_replace_text to assign ascending numbers 
    assign_or_replace_text(uncleansed_text, punctuation, 
                           word_numbers, word_numbers_list, True)

    #Shuffles the assigned numbers according to the seed number
    word_numbers_df = pd.DataFrame(word_numbers_list, columns=["Original_Word", "Numbers"])
    np.random.seed(seed)
    word_numbers_df["Numbers"] = np.random.permutation(word_numbers_df["Numbers"])

    # Refills the dictionary of words -> numbers with the shuffled numbers
    for row in word_numbers_df.itertuples():
        word_numbers[getattr(row, "Original_Word")] = getattr(row, "Numbers")
    
    # Iterates back over the text, replacing the words with their shuffled numbers
    cleansed_text = assign_or_replace_text(uncleansed_text, punctuation, 
                                           word_numbers, word_numbers_list, False)

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
    word_numbers_df.to_csv( path + file_name + "_" + column_name + "_numbers.csv")
