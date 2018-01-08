import re
import hashlib
import numpy as np
import pandas as pd
import csv
import uuid

# A regex pattern for replacing all of the punctuation in one pass
replace_chars = [".", "?", "!", "\\", "(", ")", ",", "/", "*", "&", "#", "\"",
                ";", ":", "-", "_", "=", "@", "[", "]", "+", "$", "~", "'", "`", '\\\"']
replace_chars = set(re.escape(k) for k in replace_chars)
pattern = re.compile("|".join(replace_chars))

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


if __name__ == "__main__":
    '''
    Replaces the text of a given column in a csv file with randomized numbers,
    exporting the original file with the given column removed and with the new
    column added. Exports another csv file with the mapping of orignal words to numbers.
    '''

    file_name = input("Enter the name of your csv (not including extension): ")
    column_name = input("Enter the name of the column to cleanse: ")
    seed = input("Enter a seed for randomizing (int): ")

    #Contains a dictionary of uncleansed word -> number of word
    word_numbers = {}
    #Contains the same information for export to csv (using list of lists for efficiency)
    word_numbers_list = []
    number = 1

    csv_df = pd.read_csv(file_name + ".csv")
    uncleansed_text = csv_df[column_name]
    # A series of strings with hashed words
    cleansed_text = []

    '''Iterates over the uncleansed text. Normalizes words by removing
    punctuation and making all letters lowercase '''
    for text in uncleansed_text:
        chars_removed = pattern.sub("", text)
        words_list = chars_removed.lower().split()
        number = get_nums(words_list, word_numbers, word_numbers_list, number)

    #Shuffles the assigned numbers according to the seed number
    word_numbers_df = pd.DataFrame(word_numbers_list, columns=["Original_Word", "Numbers"])
    np.random.seed(int(seed))
    word_numbers_df["Numbers"] = np.random.permutation(word_numbers_df["Numbers"])


    for row in word_numbers_df.itertuples():
        word_numbers[getattr(row, "Original_Word")] = getattr(row, "Numbers")

    for text in uncleansed_text:
        chars_removed = pattern.sub("", text)
        words_list = chars_removed.lower().split()
        replace_string = replace_words(words_list, word_numbers)
        cleansed_text.append(replace_string)

    csv_df["Cleansed_text"] = cleansed_text
    del csv_df[column_name]
    csv_df.to_csv("cleansed_" + file_name + ".csv")
    word_numbers_df.to_csv(file_name + "_" + column_name + "_numbers.csv")
