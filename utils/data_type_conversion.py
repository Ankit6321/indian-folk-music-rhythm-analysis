import pickle
import numpy as np
import os
import gc

RAW_DIR = "../data/raw"
CONVERTED_DIR = "../data/converted"

os.makedirs(CONVERTED_DIR, exist_ok=True)

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

for genre_name in genres:

    print(f"\nProcessing {genre_name}...")

    input_path = os.path.join(
        RAW_DIR,
        genre_name + ".pickle"
    )

    output_path = os.path.join(
        CONVERTED_DIR,
        genre_name + ".pickle"
    )

    with open(input_path, "rb") as f:
        df = pickle.load(f)

    df["genre"] = np.array([x.decode("utf-8") for x in df["genre"]])
    df["state"] = np.array([x.decode("utf-8") for x in df["state"]])
    df["artist"] = np.array([x.decode("utf-8") for x in df["artist"]])
    df["gender"] = np.array([x.decode("utf-8") for x in df["gender"]])
    df["song"] = np.array([x.decode("utf-8") for x in df["song"]])
    df["source"] = np.array([x.decode("utf-8") for x in df["source"]])

    df["genre_id"] = np.array([int(x) for x in df["genre_id"]])
    df["state_id"] = np.array([int(x) for x in df["state_id"]])
    df["artist_id"] = np.array([int(x) for x in df["artist_id"]])
    df["gender_id"] = np.array([int(x) for x in df["gender_id"]])
    df["no_of_artists"] = np.array([int(x) for x in df["no_of_artists"]])

    df["mel_spec"] = df["mel_spec"].astype(np.float32)

    with open(output_path, "wb") as f:
        pickle.dump(
            df,
            f,
            protocol=pickle.HIGHEST_PROTOCOL
        )

    print(f"Saved: {output_path}")

    del df
    gc.collect()

print("\nAll files converted successfully!")