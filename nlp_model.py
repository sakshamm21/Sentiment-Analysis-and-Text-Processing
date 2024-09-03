import os
import pandas as pd
from nltk.corpus import cmudict
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Function to load positive or negative words from a file
def load_words(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
        words = {line.strip() for line in file}
    return words

# Function to perform sentimental analysis
def calculate_sentiment_scores(words, positive_words, negative_words):
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(-1 for word in words if word in negative_words) * -1
    polarity_score = (positive_score - negative_score) / (positive_score + negative_score + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(words) + 0.000001)
    return positive_score, negative_score, polarity_score, subjectivity_score

# Function to count complex words
def count_complex_words(words, cmu_dict):
    return sum(1 for word in words if syllable_count(word, cmu_dict) > 2)

# Function to calculate readability
def calculate_readability(words, sentences, cmu_dict):
    average_sentence_length = len(words) / len(sentences)
    complex_words = [word for word in words if syllable_count(word, cmu_dict) > 2]
    percentage_complex_words = len(complex_words) / len(words)
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
    return average_sentence_length, percentage_complex_words, fog_index

# Function to count personal pronouns
def count_personal_pronouns(text):
    personal_pronoun_pattern = re.compile(r'\b(?:I|we|my|ours|us)\b', flags=re.IGNORECASE)
    return len(re.findall(personal_pronoun_pattern, text))

# Function to calculate average word length
def calculate_avg_word_length(words):
    total_characters = sum(len(word) for word in words)
    return total_characters / len(words)

# Function to get the syllable count using CMU Pronouncing Dictionary
def syllable_count(word, cmu_dict):
    if word.lower() in cmu_dict:
        return max([len(list(y for y in x if y[-1].isdigit())) for x in cmu_dict[word.lower()]])
    else:
        return 1  # Default to 1 if the word is not found in cmudict

# Function to calculate syllables per word
def calculate_syllables_per_word(words, cmu_dict):
    return [syllable_count(word, cmu_dict) for word in words]

# Tokenize and preprocess the text
stop_words = set(stopwords.words("english"))
cmu_dict = cmudict.dict()

def preprocess_text(text):
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    return words

# Load positive and negative words
positive_words = load_words('positive-words.txt')
negative_words = load_words('negative-words.txt')

# Folder containing text files
folder_path = 'text'

# List to store data for each file
data_list = []

# Loop through all files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        file_path = os.path.join(folder_path, file_name)

        # Load the text data
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Check if text is empty
        if not text.strip():
            # Set variables to zero if no text is present
            data_list.append({
                'URL_ID': file_name[:-4],
                'POSITIVE SCORE': 0,
                'NEGATIVE SCORE': 0,
                'POLARITY SCORE': 0,
                'SUBJECTIVITY SCORE': 0,
                'AVG SENTENCE LENGTH': 0,
                'PERCENTAGE OF COMPLEX WORDS': 0,
                'FOG INDEX': 0,
                'AVG NUMBER OF WORDS PER SENTENCE': 0,
                'COMPLEX WORD COUNT': 0,
                'WORD COUNT': 0,
                'SYLLABLE PER WORD': 0,
                'PERSONAL PRONOUNS': 0,
                'AVG WORD LENGTH': 0,
            })
            continue  # Skip further processing if no text is present

        # Tokenize and preprocess the text
        words = preprocess_text(text)
        sentences = sent_tokenize(text)

        # Calculate variables
        positive_score, negative_score, polarity_score, subjectivity_score = calculate_sentiment_scores(words, positive_words, negative_words)
        average_sentence_length, percentage_complex_words, fog_index = calculate_readability(words, sentences, cmu_dict)
        avg_words_per_sentence = len(words) / len(sentences)
        complex_word_count = count_complex_words(words, cmu_dict)
        word_count = len(words)
        syllables_per_word = calculate_syllables_per_word(words, cmu_dict)
        personal_pronoun_count = count_personal_pronouns(text)
        avg_word_length = calculate_avg_word_length(words)

        # Append data to the list
        data_list.append({
            'URL_ID': file_name[:-4],  # Remove the file extension to get the URL_ID
            'POSITIVE SCORE': positive_score,
            'NEGATIVE SCORE': negative_score,
            'POLARITY SCORE': polarity_score,
            'SUBJECTIVITY SCORE': subjectivity_score,
            'AVG SENTENCE LENGTH': average_sentence_length,
            'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
            'FOG INDEX': fog_index,
            'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
            'COMPLEX WORD COUNT': complex_word_count,
            'WORD COUNT': word_count,
            'SYLLABLE PER WORD': sum(syllables_per_word) / len(syllables_per_word),
            'PERSONAL PRONOUNS': personal_pronoun_count,
            'AVG WORD LENGTH': avg_word_length,
        })

# Create a DataFrame
df = pd.DataFrame(data_list)

# Save to Excel
df.to_excel("Output.xlsx", index=False)
