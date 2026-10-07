import pickle
import numpy as np
import os
import gc

CONVERTED_DIR = "../data/converted"
CLEAN_DIR = "../data/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

genres = [
    "Bauls",
    "Bhatiali",
    "Gidha",
    "Kajri",
    "Maand",
    "Sohar",
    "Sufi",
    "Uttarakhandi"
]

np.random.seed(42)

for genre_name in genres:

    print(f"\nProcessing {genre_name}...")

    input_path = os.path.join(
        CONVERTED_DIR,
        genre_name + ".pickle"
    )

    output_path = os.path.join(
        CLEAN_DIR,
        genre_name + "_clean.pickle"
    )

    with open(input_path, "rb") as f:
        df = pickle.load(f)

    songs = df["song"]
    genders = df["gender"]

    unique_songs = np.unique(songs)

    male_songs = []
    female_songs = []

    for song_name in unique_songs:

        song_genders = np.unique(
            genders[songs == song_name]
        )

        if len(song_genders) == 1:

            if song_genders[0] == "Male":
                male_songs.append(song_name)

            elif song_genders[0] == "Female":
                female_songs.append(song_name)

    male_songs = np.array(male_songs)
    female_songs = np.array(female_songs)

    female_count = min(10, len(female_songs))
    male_count = 20 - female_count

    selected_female = np.random.choice(
        female_songs,
        size=female_count,
        replace=False
    )

    selected_male = np.random.choice(
        male_songs,
        size=male_count,
        replace=False
    )

    selected_songs = np.concatenate(
        [selected_male, selected_female]
    )

    np.random.shuffle(selected_songs)

    mask = np.isin(
        songs,
        selected_songs
    )

    clean_df = {}

    for key, value in df.items():

        if (
            isinstance(value, np.ndarray)
            and value.shape[0] == len(songs)
        ):
            clean_df[key] = value[mask]
        else:
            clean_df[key] = value

    with open(output_path, "wb") as f:
        pickle.dump(
            clean_df,
            f,
            protocol=pickle.HIGHEST_PROTOCOL
        )

    selected_male_count = np.sum(
        np.isin(selected_songs, male_songs)
    )

    selected_female_count = np.sum(
        np.isin(selected_songs, female_songs)
    )

    print("Total unique songs:", len(unique_songs))
    print("Available male songs:", len(male_songs))
    print("Available female songs:", len(female_songs))
    print("Selected songs:", len(selected_songs))
    print("Male songs:", selected_male_count)
    print("Female songs:", selected_female_count)
    print("Mel-spectrogram samples:", np.sum(mask))
    print("Saved:", output_path)

    del df
    del songs
    del genders
    del unique_songs
    del male_songs
    del female_songs
    del selected_songs
    del mask
    del clean_df

    gc.collect()

print("\nAll genres processed successfully!")