# obscuritext
A Python script to obscure free text into anonymized data by hashing each word. These hashes can still be used for statistical modeling but have no identifying information and are completely unreadable.

## Requirements
The text to be obscured should be stored in a named column in a CSV file. This file should be stored in the same directory as the script file.

To run, use: python3 text_obscure.py

The script uses the following packages for Python3:
- numpy
- pandas
- NLTK


## Configurations
- file_name: The name of the CSV file without its extension:
- output_base: The base output name for the cleansed file:
- column_name: The name of the column to cleanse
- delete_column: Delete the original column in the output file? (Yes/No)
- index_num: The number (starting with 0) of the index column. 'None' if not present
- case_sensitive: Run as case sensitive? (Yes, No, or Both)
- stemming: Use stemming, which requires importing NLTK? (Yes, No, or Both)
- remove_punctuation: Remove punctuation (Yes, No, or Both)? Selecting 'No' will treat punctuation as words themselves.
- salt_string: A string to be used as a salt during hashing
- concat_hashes: How many characters to which to concatenate the hashes. (Int or None)
- combine_above: Combine words with counts above (an integer or 'Ask)
- combine_below = 1: Combine words with counts below (an integer or 'Ask')
