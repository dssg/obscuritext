import re
import numpy as np
import pandas as pd
import os, errno
import configparser


def get_nums(word_list, word_numbers, word_numbers_list, number):
    '''
    Given a list of words from a csv cell, returns a string of obscured words.
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
    Given a list of words from a csv cell, returns a string of obscured words.
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


def assign_or_replace_text(original_text, punctuation, word_numbers, word_numbers_list, assign, ps, stemming, case_sensitive):
    '''
    Loops through the original text. Depending on assign (bool), performs one of
    two options. Either assigns ascending numbers to the unique words OR, after shuffling,
    creates a new series of obscured text.
    INPUTS:
        original_text (Series): the column to be obscured
        punctuation (bool): if punctuation should be removed
        word_numbers (dict): to be filled on first pass with word -> number representative
            later to be used to replace words with shuffled numbers
        word_numbers_list (list of lists): same info as above
        assign (bool): tells whether to run to assign numbers or to retrieve numbers
        ps: PorterStemmer or none
        case_sensitive (bool): indicates whether to be case_sensitive

    OUTPUTS:
        Nothing on the first pass. Populates word_numbers and word_numbers_list
        obscured_text (List of strings): the text with the shuffled numbers
    '''
    # A regex pattern for replacing all of the punctuation in one pass
    pattern = re.compile("(" + "[^A-Za-z0-9 ]+" + ")")

    if assign:
        number = 1 #Only used in the first pass
    else:
        obscured_text = [] #Only used in the second pass

    for text in original_text:
        # Only performs punctuation stripping and splitting if the field is a string
        if type(text) is str:
            if punctuation:
                post_punc = pattern.sub(" ", text)
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
            obscured_text.append(replace_string)

    if not assign:
        return obscured_text

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
    while True:
        try:
            top_thresh = int(top_thresh)
            break
        except ValueError:
            print("combine_above was not a valid number. Please enter an integer")
            top_thresh = input("Combine words with counts above: ")

    if bottom_thresh.lower() == "ask":
        print("\n", word_numbers_df.tail(20), "\n")
        bottom_thresh = input("Combine words with counts below: ")
    while True:
        try:
            bottom_thresh = int(bottom_thresh)
            break
        except ValueError:
            print("combine_below was not a valid number. Please enter an integer")
            bottom_thresh = input("Combine words with counts below: ")

    return top_thresh, bottom_thresh

def export_tables(csv_df, word_numbers_df, output_base, column_name, case_sensitive,
                    stemming, punctuation, top_thresh, bottom_thresh, index_num, path):
    '''
    Strings together the options to create a descriptive filename.
    '''
    output_name = output_base + "_" + column_name

    if case_sensitive:
        output_name += "_Case"
    else:
        output_name += "_NoCase"

    if stemming:
        output_name += "_Stem"
    else:
        output_name += "_NoStem"

    if punctuation:
        output_name += "_NoPunc"
    else:
        output_name += "_Punc"

    output_name += "_Above" + str(top_thresh)
    output_name += "_Below" + str(bottom_thresh)


    csv_df.to_csv(path + output_name + ".csv", index= not type(index_num) is int)
    word_numbers_df.to_csv(path + "mappings_" + output_name + ".csv", index=False)

def run_program(file_name, column_name, output_base, delete_orig, index_num, case_sensitive,
                stemming, punctuation, seed, top_thresh, bottom_thresh):
    '''
    Given the configuration settings, runs the obscuration process. Can be called many times for different settings.
    Inputs:
        file_name (str): name of the file to obscured
        column_name (str): name of column in file
        output_base (str): the base name of the output files
        delete_orig (bool): indicated whether the original column should be deleted
        index_num (int or None): the number of the column in the original file with idecies
        case_sensitive (bool):
        stemming (bool): to use NLTK word stemming
        seed (int): a random seed for the shuffling
        punctuation (bool): to remove punctuation
        top_thresh ("Ask" or int): combine words above this count
        bottom_thresh ("Ask or int): combine words below this count
    Output:
        Nothing, but exports a two files: one with the obscured text and the other mapping original_word -> number
    '''

    if stemming:
        from nltk.stem import PorterStemmer
        ps = PorterStemmer()
    else:
        ps = None

    try:
        index_num = int(index_num)
    except ValueError:
        index_num = None

    #Contains a dictionary of original word -> [number of word, count]
    word_numbers = {}
    #Contains the same information for export to csv (using list of lists for efficiency)
    word_numbers_list = []

    csv_df = pd.read_csv(file_name + ".csv", encoding = "ISO-8859-1", index_col = index_num)
    original_text = csv_df[column_name]

    #The first pass through assign_or_replace_text to assign ascending numbers
    assign_or_replace_text(original_text, punctuation, word_numbers, word_numbers_list, True, ps, stemming, case_sensitive)

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
    obscured_text = assign_or_replace_text(original_text, punctuation, word_numbers, word_numbers_list, False, ps, stemming, case_sensitive)

    csv_df["obscured_"+ column_name] = obscured_text
    if delete_orig:
        del csv_df[column_name]
    # Creates a subdirectory to store the obscured files
    try:
        os.makedirs(r"./obscured_" + file_name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    path = r"./obscured_" + file_name + r"/"

    export_tables(csv_df, word_numbers_df, output_base, column_name, case_sensitive,
                    stemming, punctuation, top_thresh, bottom_thresh, index_num, path)

    print(len(word_numbers_df), "unique words numeralized from", len(original_text),
          "lines. Case Sensitive: " + str(case_sensitive) + ". Stemming: " + str(stemming) +
          ". Punctuation: "+ str(punctuation))



if __name__ == "__main__":
    '''
    Replaces the text of a given column in a csv file with randomized numbers,
    exporting the original file with the given column removed and with the new
    column added. Exports another csv file with the mapping of orignal words to numbers.
    '''
    config = configparser.ConfigParser()
    config.read('obscuritext_configs.cfg')

    #Configurations
    file_name = config['Data']['file_name']
    column_name = config['Data']['column_name']
    output_base = config['Data']['output_base']
    delete_orig = config.getboolean('Data', 'delete_column')
    index_num = config['Data']['index_num']

    case_sensitive = config['Processing']['case_sensitive'].lower()
    stemming = config['Processing']['stemming'].lower()
    punctuation = config['Processing']['remove_punctuation'].lower()
    seed = int(config['Processing']['random_seed'])
    top_thresh = config['Processing']['combine_above']
    bottom_thresh =config['Processing']['combine_below']

    options = [case_sensitive, stemming, punctuation]

    affirmative = {"yes", "y", "t", "true", "1", "on"}
    negative = {"no", "n", "f", "false", "0", "off"}

    # Tests for a positive or negative answer for the three options, defaulting to both
    for i, option in enumerate(options):
        if option in affirmative:
            options[i] = [True]
        elif option in negative:
            options[i]  = [False]
        else:
            options[i] = [True, False]

    case_sensitive = options[0]

    stemming = options[1]
    punctuation = options[2]

    for case in case_sensitive:
        for stem in stemming:
            for punc in punctuation:
                run_program(file_name, column_name, output_base, delete_orig, index_num, case, stem, punc, seed, top_thresh, bottom_thresh)
