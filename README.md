# obscuritext
A Python script to obscure free text into anonymized data by hashing each word. These hashes can still be used for statistical modeling but have no identifying information and are completely unreadable.

## Requirements:
The text to be obscured should be stored in a named column in a CSV file. This file should be stored in the same directory as the script file.

To run, use: python3 text_obscure.py

The script uses the following packages for Python3:
- numpy
- pandas
- NLTK


## Configurations
file_name: Specify the name of the CSV file without its extension:
output_base: Specify the base output name for the cleansed file:
column_name: Specify the name of the column to cleanse
delete_column: Would you like to delete that column in the output file? (Yes/No)
index_num: The number (starting with 0) of the index column. Write None is none exists
case_sensitive: Would you like to run as case sensitive? (Yes, No, or Both)
stemming: Would you like to use stemming, which requires importing NLTK? (Yes, No, or Both)
remove_punctuation: Would you like to remove punctuation (Yes, No, or Both)? Selecting 'No' will treat punctuation as words themselves.
random_seed: Please enter a seed integer for the randomizer
combine_above: Combine words with counts above (an integer, or, if you want to be shown the counts and then input a number in the terminal, write 'Ask')
combine_below = 1: Combine words with counts below (an integer or 'Ask')
