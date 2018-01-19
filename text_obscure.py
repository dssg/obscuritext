import re
import numpy as np
import pandas as pd
import os, errno
import configparser, hashlib, base64

def hash_word(word, salt, concat_hashes, stop_words, stop_word_hash, stop_above_hash,
              stop_below_hash, stop_above_words, stop_below_words):
    '''
    Hashes the word with a custom salt. Hashes words in the three stop words sets to the same value.
    '''
    if word in stop_above_words:
        return stop_above_hash
    elif word in stop_below_words:
        return stop_below_words
    elif word in stop_words:
        return stop_word_hash
    else:
        to_hash = word + salt

    hasher = hashlib.sha1(to_hash.encode('utf-8'))
    #Hashes using SHA1 then optionally truncates to prevent too long of hashes. Removes the padding at the end.
    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8").replace("=", "")[:concat_hashes]

def replace_words(entry_words, words_dict, salt, concat_hashes, stop_words):
    '''
    Given a list of words from a csv cell, returns a string of obscured words.
    INPUTS:
        entry_words (list): the unhased words
        salt (string): the user's string for salting
    OUTPUT:
        return_string (string): the string of hashes to stand in for the original words
    '''
    replace_string = ""
    for word in entry_words:
        word_hash = words_dict[word][0]
        replace_string += str(word_hash) + " "

    return replace_string


def assign_or_replace_text(original_text, punctuation, words_dict, words_list,
                            assign, ps, stemming, case_sensitive, salt, concat_hashes, stop_words,
                          stop_word_hash, stop_above_hash, stop_below_hash, stop_above_words, stop_below_words):
    '''
    Loops through the original text. Depending on assign (bool), performs one of
    two options. Either assigns hashes to the unique words OR
    creates a new series of obscured text.
    INPUTS:
        original_text (Series): the column to be obscured
        punctuation (bool): if punctuation should be removed
        words_dict (dict): to be filled on first pass with word -> hash representative
            later to be used to replace words with hashes
        words_list (list of lists): contains all unique words_list
        assign (bool): tells whether to run to assign hashes or to retrieve hashes
        ps: PorterStemmer or none
        case_sensitive (bool): indicates whether to be case_sensitive
        salt (string): the user's string for salting

    OUTPUTS:
        Nothing on the first pass. Populates words_dict and words_list
        obscured_text (List of strings): the text with the hashes
    '''
    # A regex pattern for replacing all of the punctuation in one pass
    pattern = re.compile("(" + "[^A-Za-z0-9 ]+" + ")")

    if not assign:
        obscured_text = [] #Only used in the second pass

    for entry in original_text:
        if type(entry) is not str:
            text = str(entry)

        if punctuation:
            post_punc = pattern.sub(" ", entry)
        else:
            # Isolates punctuation to be treated as an individual word
            post_punc = pattern.sub(r' \1 ', entry)

        if case_sensitive:
            entry_words = post_punc.split()
        else:
            entry_words = post_punc.lower().split()

        if stemming:
            entry_words = [ps.stem(i) for i in entry_words]

        if assign:
            for word in entry_words:
                if word not in words_dict:
                    word_hash = hash_word(word, salt, concat_hashes, stop_words, stop_word_hash, stop_above_hash,
                                          stop_below_hash, stop_above_words, stop_below_words)
                    words_dict[word] = [word_hash, 1]
                    words_list.append([word, word_hash])
                else:
                    # Increases count by 1 if already in dictionary
                    words_dict[word][1] += 1
        else:
            replace_string = replace_words(entry_words, words_dict, salt, concat_hashes, stop_words)
            obscured_text.append(replace_string)

    if not assign:
        return obscured_text

def get_top_and_bottom_thresholds(top_thresh, bottom_thresh, words_df):
    '''
    If top_thresh or bottom_thresh was set to "ask" in the config file, shows the user the
    head or tail of the dataset and asks for the desired count.
    INPUTS:
        top_thresh (string): contains either an int, "ask", or "none"
        bottom_thresh (string): contains either an int, "ask", or "none
    OUTPUTS:
        top_thresh (int): the desired top threshold, as an integer
        bottom_thresh (int): the desired bottom threshold, as an integer
    '''
    if top_thresh == "none":
        top_thresh = None
    else:
        if top_thresh == "ask":
            print(words_df.head(20),  "\n")
            top_thresh = input("Combine words with counts above: ")
        while True:
            try:
                top_thresh = int(top_thresh)
                break
            except ValueError:
                print("combine_above was not a valid number. Please enter an integer")
                top_thresh = input("Combine words with counts above: ")


    if bottom_thresh == "none":
        bottom_thresh = None
    else:
        if bottom_thresh == "ask":
            print("\n", words_df.tail(20), "\n")
            bottom_thresh = input("Combine words with counts below: ")
        while True:
            try:
                bottom_thresh = int(bottom_thresh)
                break
            except ValueError:
                print("combine_below was not a valid number. Please enter an integer")
                bottom_thresh = input("Combine words with counts below: ")

    return top_thresh, bottom_thresh

def export_tables(csv_df, words_df, output_base, column_name, case_sensitive,
                    stemming, punctuation, top_thresh, bottom_thresh, index_num, path,
                    salt, stop_words, stop_above_words, stop_below_words):
    '''
    Strings together the options to create a descriptive filename.
    '''
    output_name = output_base + "_" + column_name

    output_name += "_Salt=" + salt

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
    words_df.to_csv(path + "mappings_" + output_name + ".csv", index=False)

    with open(path + "stop_words_" + output_name + ".txt", "w") as text_file:
        text_file.write("To encode new data with the same obscurations, copy and paste these into the configurations. \n\n")
        text_file.write("Stop Words: \n")
        text_file.write(" ".join(stop_words) + "\n\n\n")
        text_file.write("Stop Above Words: \n")
        text_file.write(" ".join(stop_above_words) + "\n\n\n")
        text_file.write("Stop Words Above Threshold: \n")
        text_file.write(" ".join(stop_below_words))


def run_program(file_name, column_name, output_base, delete_orig, index_num, case_sensitive,
                stemming, punctuation, salt, top_thresh, bottom_thresh, concat_hashes, stop_words,
                stop_above_words, stop_below_words):
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
        salt (string): a user-inputed string for the salting the hashes
        punctuation (bool): to remove punctuation
        top_thresh ("Ask" or int): combine words above this count
        bottom_thresh ("Ask or int): combine words below this count
        concat_hashes (int or None): number of bytes to concatenate the hashes
    Output:
        Nothing, but exports a two files: one with the obscured text and the other mapping original_word -> hash
    '''
    #Contains a dictionary of original word -> [hash of word, count]
    words_dict = {}
    #Contains the same information for export to csv (using list of lists for efficiency)
    words_list = []

    # Defines a hash for all the stop words, so that they don't all need to be hashed.
    stop_word_hash = hash_word("stop words", salt, concat_hashes, stop_words, '', '', '', stop_above_words, stop_below_words)
    stop_above_hash = hash_word("stop above", salt, concat_hashes, stop_words, '', '', '', stop_above_words, stop_below_words)
    stop_below_hash = hash_word("stop below", salt, concat_hashes, stop_words, '', '', '', stop_above_words, stop_below_words)

    # Reads our initial csv
    csv_df = pd.read_csv(file_name + ".csv", encoding = "ISO-8859-1", index_col = index_num)
    original_text = csv_df[column_name]

    #Creates a set of stop_words, based on case sensitivtivity.
    if case_sensitive:
        stop_words = set(stop_words.split())
    else:
        stop_words = set(stop_words.lower().split())

    #The first pass through assign_or_replace_text to get all the unique words. Fills words_list and words_dict
    assign_or_replace_text(original_text, punctuation, words_dict, words_list, True,
                            ps, stemming, case_sensitive, salt, concat_hashes, stop_words,
                            stop_word_hash, stop_above_hash, stop_below_hash, stop_above_words,
                            stop_below_words)


    #Fetches the counts of the words, in order, to be filled into the words_df created below
    counts = []
    for word, word_hash in words_list:
        counts.append(words_dict[word][1])

    #Assigns the proper counts, and sorts by them
    words_df = pd.DataFrame(words_list, columns=["Original_Word", "Hash"])
    words_df["Count"] = counts
    words_df.sort_values(by = "Count", ascending=False, inplace=True)

    #If the user hasn't already picked thresholds, asks for them. Converts to ints
    top_thresh, bottom_thresh = get_top_and_bottom_thresholds(top_thresh, bottom_thresh, words_df)

    # Creates a set for the words above the top threshold. When hashing, will hash these the same
    if top_thresh != None:
        words_df.loc[words_df.Count > top_thresh, 'Hash'] = stop_above_hash

        above_thresh_df = words_df[(words_df.Count > top_thresh)]
        # For exporting to a text file
        stop_above_words = list(above_thresh_df.Original_Word)

        # Refilling the words_dict with the new hashes
        for row in above_thresh_df.itertuples():
            words_dict[getattr(row, "Original_Word")][0] = getattr(row, "Hash")

    # Creates a set for the words below the top threshold. When hashing, will hash these the same
    if bottom_thresh != None:
        words_df.loc[words_df.Count < bottom_thresh, 'Hash'] = stop_below_hash

        below_thresh_df = words_df[(words_df.Count < bottom_thresh)]
        # For exporting to a text file
        stop_below_words = list(below_thresh_df.Original_Word)

        # Refilling the words_dict with the new hashes
        for row in below_thresh_df.itertuples():
            words_dict[getattr(row, "Original_Word")][0] = getattr(row, "Hash")


    # Iterates back over the text, replacing the words with their hashes
    obscured_text = assign_or_replace_text(original_text, punctuation, words_dict,
                                            words_list, False, ps, stemming,
                                            case_sensitive, salt, concat_hashes, stop_words,
                                            stop_word_hash, stop_above_hash, stop_below_hash,
                                            stop_above_words, stop_below_words)


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

    export_tables(csv_df, words_df, output_base, column_name, case_sensitive,
                    stemming, punctuation, top_thresh, bottom_thresh, index_num, path,
                    salt, stop_words, stop_above_words, stop_below_words)


    print(len(words_df), "unique words numeralized from", len(original_text),
          "lines. Case Sensitive: " + str(case_sensitive) + ". Stemming: " + str(stemming) +
          ". Punctuation: "+ str(punctuation))

if __name__ == "__main__":
    '''
    Replaces the text of a given column in a csv file with hashes,
    exporting the original file with the given column removed and with the new
    column added. Exports another csv file with the mapping of orignal words to hashes.
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
    salt = config['Processing']['salt_string']
    concat_hashes = config['Processing']['concat_hashes']
    top_thresh = config['Processing']['combine_above'].lower()
    bottom_thresh = config['Processing']['combine_below'].lower()
    stop_words = config['Processing']['stop_words']
    stop_above_words = config['Processing']['stop_above_words']
    stop_below_words = config['Processing']['stop_below_words']

    if stemming:
        from nltk.stem import PorterStemmer
        ps = PorterStemmer()
    else:
        ps = None

    # The column of the index in the original file
    try:
        index_num = int(index_num)
    except ValueError:
        index_num = None

    # To shorten the hashes to limit file size
    try:
        concat_hashes = int(concat_hashes)
    except ValueError:
        concat_hashes = None

    stop_above_words = set(stop_above_words.split())
    stop_below_words = set(stop_below_words.split())

    if (len(stop_above_words) != 0 or len(stop_above_words) != 0) and (top_thresh != "none" or bottom_thresh != "none"):
        raise ValueError('If there are stop_above_words or stop_below_words present, the top and bottom thresholds must be set to None')

    # Runs the program with every combination of case_sensitive, stemming, and punctuation given by the user
    options = [case_sensitive, stemming, punctuation]
    affirmative = {"yes", "y", "t", "true", "1", "on"}
    negative = {"no", "n", "f", "false", "0", "off"}

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
                run_program(file_name, column_name, output_base, delete_orig, index_num,
                case, stem, punc, salt, top_thresh, bottom_thresh, concat_hashes, stop_words,
                            stop_above_words, stop_below_words)
