# Data

The data is not included in this repository because the full dataset on Zenodo is approximately 22.8 GB (compressed `.7z` archives, one per folk style). The project uses a curated subset of the publicly available Indian Folk Music Dataset from Zenodo: 8 of the 15 folk styles (about 12.6 GB compressed), and 20 songs from each.

## Original source

**Indian Folk Music Dataset**  
Y. Singh, L. Waikhom, V. Meena, A. Biswas (2022). Zenodo.  
https://zenodo.org/records/6584021  
DOI: 10.5281/zenodo.6584021  
License: Creative Commons Attribution 4.0 International (CC BY 4.0)

The original dataset contains Mel-spectrogram features extracted from 3-second audio segments using a 1/2-second sliding window. It contains recordings from 15 Indian folk styles, of which this project uses 8.

Each segment contains metadata including:

- Folk style / genre
- State
- Artist
- Gender
- Song
- Source
- Artist and genre IDs

## Getting the raw data

On the Zenodo page, download the `.7z` archive for each of the 8 genres used in this project (Bauls, Bhatiali, Gidha, Kajri, Maand, Sohar, Sufi, Uttarakhandi). Extract each archive with a tool that supports 7-Zip (for example 7-Zip or `7z x`) and place the resulting `<Genre>.pickle` files in `data/raw/`.

## Dataset preprocessing pipeline

The dataset is processed in three stages. The scripts are in `utils/` and use relative paths (`../data/...`), so run them from inside the `utils/` folder, in this order:

```bash
cd utils
python data_type_conversion.py
python gender_correction.py      # add --dry-run first to preview the changes
python song_selection.py
```

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

### 2. Gender label correction

Some segments in the source metadata have misspelled gender labels (for example `femlae` or `Female ` with a trailing space). The song selection step only recognizes the exact labels `Male` and `Female`, so uncorrected labels would cause those songs to be silently dropped from the candidate pool.

The script `gender_correction.py`:

- Reads the `gender` field of each converted genre file.
- Maps misspelled, mis-cased, or whitespace-padded labels to `Male` or `Female`.
- Prints every distinct value found, each correction made, and how many segments it affected.
- Does not guess when a value is ambiguous. Such values are left unchanged and listed at the end for manual review, and the script exits with an error code.
- Reports songs that still contain both genders after correction (these are excluded by song selection).
- Corrects the files in `data/converted/` in place. Files in `data/raw/` are not modified.
- Supports `--dry-run` to preview all changes without writing any file.

### 3. Song selection and dataset curation

The script `song_selection.py` uses the corrected converted files to create the final curated dataset.

For each of the 8 selected genres:

- The dataset is loaded one genre at a time.
- Unique songs are identified.
- Only songs with a single vocalist gender are candidates.
- Up to 10 female songs are selected (all available female songs if fewer than 10 exist).
- The remaining songs are selected from male songs, for a total of 20 unique songs per genre.
- Selection is random with a fixed seed (42), so it is reproducible.
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
- Total size of `data/clean/`: approximately **6.82 GB**

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
├── converted/               # created by data_type_conversion.py, corrected by gender_correction.py
│   ├── Bauls.pickle
│   ├── Bhatiali.pickle
│   ├── Gidha.pickle
│   ├── Kajri.pickle
│   ├── Maand.pickle
│   ├── Sohar.pickle
│   ├── Sufi.pickle
│   └── Uttarakhandi.pickle
│
├── clean/                   # created by song_selection.py
│   ├── Bauls_clean.pickle
│   ├── Bhatiali_clean.pickle
│   ├── Gidha_clean.pickle
│   ├── Kajri_clean.pickle
│   ├── Maand_clean.pickle
│   ├── Sohar_clean.pickle
│   ├── Sufi_clean.pickle
│   └── Uttarakhandi_clean.pickle
│
└── extracted/               # created by notebooks/02_Rhythm_Feature_Extraction.ipynb
    ├── rhythm_features.parquet
    └── rhythm_features.pkl
```