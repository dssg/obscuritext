# obscuritext
A Python script to transform free text into de-identified data by hashing each word. These hashes can still be used for statistical modeling while effectively making the text unreadable.

## Usage
To run the obscuring process:
- Download the following files from this repository: Dockerfile, obscuritext_configs.cfg, and run_in_docker.sh
- Place the Dockerfile in a folder, build an image using `docker build (name of folder) -t (name):(tag)" ] `.
- Note the image ID or find it with `docker images`. Run it using `docker run -it -d (image ID)`.
- Find the running container id using `docker ps -a`. Copy it.
- Place your csv file to obscure in a directory with the downloaded obscuritext_configs.cfg and run_in_docker.sh
- Edit the obscuritext_configs.cfg to reflect your desired configuration options. Leave the name as "obscuritext_configs.cfg".
- On the command line, run: `./run_in_docker.sh [csv file name without extension] [container ID]` in that directory
- The files will be copied into the docker, obscured, and returned in a new subdirectory called "obscured_[original file name]"

## Requirements
The text to be obscured should be stored in a named column in a CSV file. This file should be stored in the same directory as the script file, and its name should not contain spaces. This name must be specified in the configuration file.

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
