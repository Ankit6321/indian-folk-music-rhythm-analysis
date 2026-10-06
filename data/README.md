# Data

The data is not included in this repository (the raw dataset is ~22.8 GB). This project uses a curated subset of a publicly available Zenodo dataset.

## Original source

**Indian Folk Music Dataset**
Y. Singh, L. Waikhom, V. Meena, A. Biswas (2022). Zenodo.
https://zenodo.org/records/6584021 (DOI: 10.5281/zenodo.6584021)

The dataset contains Mel-spectrogram features extracted from 3-second segments (1/2-second sliding window) of 606 recordings across 15 folk styles. Each segment is annotated with folk_style, state, artist, gender, song, and source.

## Curated subset used in this project

The raw dataset was preprocessed to build a balanced corpus:

- 20 unique songs per genre, 160 songs in total
- 8 genres: Bauls, Bhatiali, Gidha, Kajri, Maand, Sohar, Sufi, Uttarakhandi
- 109,089 Mel-spectrogram segments of shape (128, 130)