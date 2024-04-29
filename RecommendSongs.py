#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Text Sentiment Analysis
import pandas as pd
import numpy as np
import re
import nltk
nltk.download('punkt')
from nrclex import NRCLex
import random

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity

results_lyrics_df = pd.read_csv('app/NormalizationLyricsScore.csv')
results_description_df = pd.read_csv('app/NormalizationDescriptionScore.csv')

def fetch_lyrics(book_name, results_description_df, new_results_lyrics_df):
    # Ensure sample_description is a DataFrame
    if not isinstance(results_description_df, pd.DataFrame):
        return "Error: results_description is not a pandas DataFrame."

    # Check if 'book' column exists in the DataFrame
    if 'book' not in results_description_df.columns:
        return "Error: 'book' column not found in results_description DataFrame."
    
    book_row = results_description_df[results_description_df['book'] == book_name]
    if book_row.empty:
        return "Book not found in the dataset."

    emotions = ['anticipation', 'disgust', 'joy', 'sadness', 'surprise', 'trust', 'anger', 'fear']
    book_row[emotions] = book_row[emotions].apply(pd.to_numeric, errors='coerce').fillna(0)
    return new_results_lyrics_df

def calculate_cosine_similarity(book_vector, song_vectors):
    book_vector = np.nan_to_num(book_vector, nan=0)
    song_vectors = np.nan_to_num(song_vectors, nan=0)
    similarities = cosine_similarity(book_vector.reshape(1, -1), song_vectors)
    return similarities.flatten()

'''def fetch_lyrics_and_calculate_similarity(book_name):
    results_description_df = pd.read_csv('app/NormalizationDescriptionScore.csv')
    results_lyrics_df = pd.read_csv('app/NormalizationLyricsScore.csv')

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
    
    most_similar_songs = lyrics_with_max_emotion.sort_values(by='cos_similarity', ascending=False).head(10)

    most_similar_songs
    return most_similar_songs'''

def fetch_lyrics_and_calculate_similarity(book_name):
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

        most_similar_songs = lyrics_with_max_emotion.sort_values(by='cos_similarity', ascending=False).head(20)

        return most_similar_songs

    except Exception as e:
        return results_lyrics_df.head(20)


