# Data

The data is not included in this repository because the raw dataset is approximately 22.8 GB. The project uses a curated subset of the publicly available Indian Folk Music Dataset from Zenodo.

## Original source

**Indian Folk Music Dataset**  
Y. Singh, L. Waikhom, V. Meena, A. Biswas (2022). Zenodo.  
https://zenodo.org/records/6584021  
DOI: 10.5281/zenodo.6584021

The original dataset contains Mel-spectrogram features extracted from 3-second audio segments using a 1/2-second sliding window. It contains recordings from 15 Indian folk styles.

Each segment contains metadata including:

- Folk style / genre
- State
- Artist
- Gender
- Song
- Source
- Artist and genre IDs

## Dataset preprocessing pipeline

The dataset is processed in two stages.

### 1. Data type conversion

The original pickle files contain some metadata fields stored as byte strings and numerical fields stored as bytes.

The script `data_type_conversion.py`:

- Processes one genre at a time to reduce memory usage.
- Converts text fields from bytes to UTF-8 strings.
- Converts ID and count fields from bytes to integers.
- Converts Mel-spectrogram values to `float32`.
- Saves the converted files to `data/converted/`.
- Automatically creates the `data/converted/` directory if it does not exist.

The original files in `data/raw/` are not modified.

### 2. Song selection and dataset curation

The script `song_selection.py` uses the converted files to create the final curated dataset.

For each of the 8 selected genres:

- The dataset is loaded one genre at a time.
- Unique songs are identified.
- Songs are selected while maintaining a balanced male/female distribution.
- Up to 10 female songs are selected.
- The remaining songs are selected from male songs.
- A maximum of 20 unique songs is selected per genre.
- If a genre contains fewer than 20 unique songs, all available songs are retained.
- All Mel-spectrogram segments belonging to a selected song are retained.
- The resulting files are saved to `data/clean/`.
- The `data/clean/` directory is created automatically if it does not exist.

This ensures that selection is performed at the **song level rather than at the individual Mel-spectrogram segment level**.

## Final curated subset

The final dataset contains:

- **20 unique songs per genre**
- **160 unique songs in total**
- **8 genres:**
  - Bauls
  - Bhatiali
  - Gidha
  - Kajri
  - Maand
  - Sohar
  - Sufi
  - Uttarakhandi
- **109,089 Mel-spectrogram segments**
- Mel-spectrogram shape: **(128, 130)**

## Directory structure

After downloading the original dataset and running the preprocessing scripts, the data directory should look like:

```text
data/
├── raw/
│   ├── Bauls.pickle
│   ├── Bhatiali.pickle
│   ├── Gidha.pickle
│   ├── Kajri.pickle
│   ├── Maand.pickle
│   ├── Sohar.pickle
│   ├── Sufi.pickle
│   └── Uttarakhandi.pickle
│
├── converted/
│   ├── Bauls.pickle
│   ├── Bhatiali.pickle
│   ├── Gidha.pickle
│   ├── Kajri.pickle
│   ├── Maand.pickle
│   ├── Sohar.pickle
│   ├── Sufi.pickle
│   └── Uttarakhandi.pickle
│
└── clean/
    ├── Bauls_clean.pickle
    ├── Bhatiali_clean.pickle
    ├── Gidha_clean.pickle
    ├── Kajri_clean.pickle
    ├── Maand_clean.pickle
    ├── Sohar_clean.pickle
    ├── Sufi_clean.pickle
    └── Uttarakhandi_clean.pickle