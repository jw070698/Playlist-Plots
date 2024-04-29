# -*- coding: utf-8 -*-
"""670_team_project (1) (2).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S4fj9aVLaAamPzYlvJgekIVzlSMmMMAR

### Text Sentiment Analysis for New Data

## Text Sentiment Analysis

- Using nrclex
- https://pypi.org/project/NRCLex/
"""

!pip install sentence-transformers
!pip install nrclex

import pandas as pd
book_info = pd.read_csv('Book_description.csv')
music_info = pd.read_csv('predicted_topics.csv')

book_description = book_info['description'].astype(str).apply(lambda x: x.lower())
book_description = book_description.str.replace('\n',' ')

music_lyrics = music_info['lyrics'].astype(str).apply(lambda x: x.lower())
music_lyrics = music_lyrics.str.replace('\n',' ')



import nltk
nltk.download('punkt')

# lyrics
from nrclex import NRCLex
results_lyrics = []
results_lyrics_score = []
for i in range(len(music_lyrics)):
    emotion = NRCLex(music_lyrics[i])
    raw_score = emotion.raw_emotion_scores
    if len(raw_score) > 1:
        mean_score = sum(raw_score.values()) / len(raw_score)
        std_dev = (sum((x - mean_score) ** 2 for x in raw_score.values()) / len(raw_score)) ** 0.5
    else:
        std_dev = 1  # Set std_dev to a non-zero value to avoid division by zero

    if std_dev == 0:
        normalized_score = {emotion: 0 for emotion, score in raw_score.items()}
    else:
        normalized_score = {emotion: (score - mean_score) / std_dev for emotion, score in raw_score.items()}

    if normalized_score:  # Check if the dictionary is not empty
        max_score = max(normalized_score.values())
        min_score = min(normalized_score.values())
    else:
        max_score, min_score = 0, 0

    if max_score != min_score:
        normalized_score = {emotion: (score - min_score) / (max_score - min_score) for emotion, score in normalized_score.items()}
    else:
        normalized_score = {emotion: 0 for emotion, score in raw_score.items()}

    formatted_score = {emotion: format(score, '.4f') for emotion, score in normalized_score.items()}


    results_lyrics.append(music_info.loc[i]['lyrics'])
    results_lyrics_score.append(formatted_score)

# lyrics to dataframe
title = pd.DataFrame(music_info['track_name'])
artist = pd.DataFrame(music_info['track_artist'])
lyrics = pd.DataFrame(music_info['lyrics'])
id_df = pd.DataFrame(results_lyrics)
score_df = pd.DataFrame(results_lyrics_score)
merged_df = pd.concat([title,artist,lyrics,id_df, score_df], axis=1)

merged_df

# lyrics to csv
results_lyrics_df = pd.DataFrame(merged_df)
results_lyrics_df.to_csv('NormalizationLyricsScore.csv', index=False)

# book descriptions
results_descriptions = []
results_descriptions_score = []
for i in range(len(book_description)):
    emotion = NRCLex(book_description[i])
    raw_score = emotion.raw_emotion_scores
    if len(raw_score) > 1:
        std_dev = (sum((x - mean_score) ** 2 for x in raw_score.values()) / len(raw_score)) ** 0.5
        mean_score = sum(raw_score.values()) / len(raw_score)
    else:
        std_dev = 1  # Set std_dev to a non-zero value to avoid division by zero

    if std_dev == 0:
        normalized_score = {emotion: 0 for emotion, score in raw_score.items()}
    else:
        normalized_score = {emotion: (score - mean_score) / std_dev for emotion, score in raw_score.items()}

    if normalized_score:  # Check if the dictionary is not empty
        max_score = max(normalized_score.values())
        min_score = min(normalized_score.values())
    else:
        max_score, min_score = 0, 0

    if max_score != min_score:
        normalized_score = {emotion: (score - min_score) / (max_score - min_score) for emotion, score in normalized_score.items()}
    else:
        normalized_score = {emotion: 0 for emotion, score in raw_score.items()}

    formatted_score = {emotion: format(score, '.4f') for emotion, score in normalized_score.items()}


    results_descriptions.append(book_info.loc[i]['title'])
    results_descriptions_score.append(formatted_score)

# book descriptions to dataframe
genres = pd.DataFrame(book_info["genres"])
id_df2 = pd.DataFrame(results_descriptions)
score_df2 = pd.DataFrame(results_descriptions_score)
merged_df2 = pd.concat([id_df2,genres, score_df2], axis=1)

# book descriptions to csv
results_description_df = pd.DataFrame(merged_df2)
results_description_df.to_csv('NormalizationDescriptionScore.csv', index=False)
results_description_df.rename(columns={results_description_df.columns[0]: 'book'}, inplace=True)

results_description_df.head(30)

#results_description_df = results_description_df.drop(['negative', 'positive'], axis=1)
results_lyrics_df = results_lyrics_df.drop(['negative', 'positive'], axis=1)

results_lyrics_df

def fetch_lyrics(book_name, sample_description, new_results_lyrics_df):

    book_row = sample_description[sample_description['book'] == book_name]
    if book_row.empty:
        return "Book not found in the dataset."


    emotions = ['anticipation', 'disgust', 'joy', 'sadness', 'surprise', 'trust', 'anger', 'fear']
    book_row[emotions] = book_row[emotions].apply(pd.to_numeric, errors='coerce').fillna(0)


    return new_results_lyrics_df

book_name_input = "Little Women"
author_name = "Louisa May Alcott"

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_cosine_similarity(book_vector, song_vectors):
    book_vector = np.nan_to_num(book_vector, nan=0)
    song_vectors = np.nan_to_num(song_vectors, nan=0)
    similarities = cosine_similarity(book_vector.reshape(1, -1), song_vectors)
    return similarities.flatten()

def fetch_lyrics_and_calculate_similarity(book_name, results_description_df, results_lyrics_df):
    try:

      lyrics_with_max_emotion = fetch_lyrics(book_name, results_description_df, results_lyrics_df)

      if isinstance(lyrics_with_max_emotion, str):
          return lyrics_with_max_emotion

      book_row = results_description_df[results_description_df['book'] == book_name]
      emotions = ['anticipation', 'disgust', 'joy', 'sadness', 'surprise', 'trust', 'anger', 'fear']

      # Ensure the emotions columns match between book_row and lyrics_with_max_emotion
      common_emotions = list(set(emotions) & set(lyrics_with_max_emotion.columns))

      book_emotions = book_row[common_emotions].fillna(0).values.flatten().astype(float)
      song_emotions = lyrics_with_max_emotion[common_emotions].fillna(0).values.astype(float)

      similarities = calculate_cosine_similarity(book_emotions, song_emotions)

      lyrics_with_max_emotion['cos_similarity'] = similarities

      most_similar_songs = lyrics_with_max_emotion.sort_values(by='cos_similarity', ascending=False).head(50)

      print(f"Input Book: {book_name}")
      print(f"Genres: {book_row['genres'].values[0]}")
      return most_similar_songs

    except Exception as e:
        return results_lyrics_df


output_most_similar_songs = fetch_lyrics_and_calculate_similarity(book_name_input, results_description_df, results_lyrics_df)

import pandas as pd
from sentence_transformers import SentenceTransformer
from torch.nn.functional import cosine_similarity

# Load pre-trained Sentence Transformer model
model_name = 'paraphrase-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

#df = pd.read_csv('/content/predicted_topics.csv')
df = output_most_similar_songs

titles = df['track_name'].tolist()
artists = df['track_artist'].tolist()
lyrics = df['lyrics'].tolist()

# Encode lyrics using Sentence Transformers model
lyric_embeddings = model.encode(lyrics, convert_to_tensor=True)

import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords

import nltk
nltk.download('punkt')

# Download stopwords corpus
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))


def preprocess_text(text):
  #1 lowercase
  text = text.lower()

  #2 replace special characters
  text = re.sub('\n+', ' ', text)
  text = re.sub('[^\w\s]', ' ', text)
  text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

  return text


def tokenize_text(text):

    # Tokenize text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    tokens = [token for token in tokens if token not in stop_words]

    # # Join tokens back into a single string
    # tokenized_text = ' '.join(tokens)

    return tokens

import requests
summ1 = ''
def get_book_summary(book_title, author):
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}+inauthor:{author}&key=AIzaSyC7l7kUyLRQHu0flXHakLAlnPDhDXQaHu4"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            summ1 = item['volumeInfo'].get('description', 'Summary not available.')

get_book_summary(book_name_input, author_name)

summary = pd.read_csv('/content/book_summary.csv')

# Filter the rows based on book name and author
filtered_row = summary[(summary['title'] == book_name_input) & (summary['author'] == author_name)]
summ2 =''
if len(filtered_row)>0:
    summ2 = preprocess_text(filtered_row['summary'].iloc[0])

import pandas as pd

# Read the CSV file into a DataFrame
book_info = pd.read_csv('/content/Book_description.csv')

# Convert book name and author name to lowercase
book_name_lower = book_name_input.lower()
author_name_lower = author_name.lower()

# Filter the rows based on book name and author (case-insensitive)
filtered_row = book_info[(book_info['title'].str.lower() == book_name_lower) & (book_info['author'].str.lower().str.contains(author_name_lower))]

# Initialize an empty string for the book description
summ3 = ''

# Check if any rows match the criteria
if not filtered_row.empty:
    # Preprocess the description of the first matching row
    summ3 = preprocess_text(filtered_row['description'].iloc[0])
    print(summ3)
else:
    print("No matching book found.")

# Load query file
query = book_name_input + summ1 + summ2 + summ3

# Encode query
query_embedding = model.encode(query, convert_to_tensor=True)

# Compute cosine similarity between query and document lyrics
similarities = cosine_similarity(query_embedding, lyric_embeddings)

# Sort documents by similarity
sorted_indices = similarities.argsort(descending=True)
ranked_documents = [(titles[i], artists[i], similarities[i].item()) for i in sorted_indices]

print(book_name_input)
for title, artist, sim in ranked_documents[:10]:
    print(f"{title} - {artist}")