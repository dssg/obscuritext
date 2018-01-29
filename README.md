# obscuritext
A Python script to obscure free text into anonymized data by hashing each word. These hashes can still be used for statistical modeling but have no identifying information and are completely unreadable.

## Usage
To run the obscuration process:
- Download the following files from this repository: Dockerfile, obscuritext_configs.cfg, and run_in_docker.sh
- Using the Dockerfile, build an image and run it with the -d flag for detached. Find the container id of the running container and copy it.
- Place your csv file to obscure in a directory with the downloaded obscuritext_configs.cfg and run_in_docker.sh
- Edit the obscuritext_configs.cfg to reflect your desired configuration options. Leave the name as "obscuritext_configs.cfg".
- On the command line, run: ./run_in_docker.sh <csv file name without extension> <container ID>
- The files will be copied into the docker, obscured, and the results returned in a subdirectory.

## Requirements
The text to be obscured should be stored in a named column in a CSV file. This file should be stored in the same directory as the script file.

To run, use: python3 text_obscure.py

The script uses the following packages for Python3:
- pandas
- NLTK


## Configurations
- file_name: The name of the CSV file without its extension
- output_base: The base output name for the cleansed file
- column_names: The names of the columns to cleanse, separated by a space
- delete_column: Delete the original column in the output file? (Yes/No)
- index_num: The number (starting with 0) of the index column. 'None' if not present
- case_sensitive: Run as case sensitive? (Yes, No, or Both)
- stemming: Use stemming, which requires importing NLTK? (Yes, No, or Both)
- remove_punctuation: Remove punctuation (Yes, No, or Both)? Selecting 'No' will treat punctuation as words themselves.
- salt_string: A string to be used as a salt during hashing
- concat_hashes: How many characters to which to concatenate the hashes (Int or None)
- combine_above: Combine words with counts above (an integer or 'Ask)
- combine_below: Combine words with counts below (an integer or 'Ask')
- stop_words: Custom stop words that the user can enter
- stop_above_words: If encoding new data with the same encoding as prior data, fill with the "Stop words above threshold: " exported from the original encoding.
- stop_below_words: If encoding new data with the same encoding as prior data, fill with the "Stop words below threshold: " exported from the original encoding.
