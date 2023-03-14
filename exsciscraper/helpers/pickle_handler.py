import pickle
import sys


def load_pickle(file_path):
    try:
        with open("/Users/spleut/Projects/Coding/exsciscraper/resources/pickles/wrapped_list_pair.pkl", "rb") as file:
            filename = "/Users/spleut/Projects/Coding/exsciscraper/resources/pickles/wrapped_list_pair.pkl".split('/')[
                -1].replace('.pkl', '')
            globals()[filename] = pickle.load(file)
            if filename in globals().keys():
                print(f"{filename} successfully loaded.")
                return globals()[filename]
    except OSError:
        print("Could not open pickles.")
        sys.exit(1)
