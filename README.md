# Computational Analysis of Rhythm Features in North and East Indian Folk Music

A large-scale computational study of rhythm-related acoustic features across **eight North and East Indian folk music genres**. The project tests whether rhythm alone, independent of melody or lyrics, carries genre-distinguishing information, and how strong that information is once statistical inflation from a very large sample is accounted for.

Carried out under the **Indian Knowledge Systems (IKS) Internship Program 2026** at the **National Institute of Technology Silchar**, as part of the IKS-funded project *"Analyzing the Raag Origins of Indian Traditional Folk Music"*.

- **Supervisor:** Dr. Aparajita Dutta
- **Principal Investigator:** Dr. Anupam Biswas
- **Author:** Ankit Yadav (Scholar ID: 2412099), B.Tech CSE, NIT Silchar

---

## Highlights

- **8 genres**, **160 songs** (20 per genre), **59 unique artists**, **109,089 Mel-spectrogram segments**
- **34 rhythm-centric parameters** extracted per segment (33 usable after removing one constant feature)
- **Within-genre cosine similarity (0.0737)** is over 20x the across-genre similarity (0.0031)
- **32 of 33** parameters differ significantly across genres after Benjamini-Hochberg FDR correction, but effect sizes are small-to-moderate (max eta-squared = 0.155)
- Song-grouped SVM (RBF) reaches **40.4% held-out accuracy** (macro-F1 0.366) on unseen songs, against a 12.5-16.8% chance baseline
- Conclusion: rhythm carries **real but moderate** genre information; statistical significance alone overstates practical separability

---

## Genres

| Genre | State / Region |
|---|---|
| Bauls | West Bengal |
| Bhatiali | West Bengal |
| Gidha | Punjab |
| Kajri | Uttar Pradesh |
| Maand | Rajasthan |
| Sohar | Uttar Pradesh |
| Sufi | Northern India |
| Uttarakhandi | Uttarakhand |

---

## Pipeline

```text
Raw Mel-spectrogram dataset (Zenodo)
        │
        ▼
Preprocessing (type conversion, gender correction, song-level selection)
        │
        ▼
Balanced clean dataset (8 genres x 20 songs)
        │
        ▼
Rhythm feature extraction (34 parameters)
        │
        ▼
Unsupervised analysis ── Cosine similarity · K-NN (k=5) · PCA
        │
        ▼
Statistical testing ──── Kruskal-Wallis · BH-FDR · eta-squared
        │
        ▼
Supervised classification ── Random Forest · SVM (RBF), song-grouped CV
```

---

## Repository Structure

```text
indian-folk-music-rhythm-analysis/
├── data/
│   ├── raw/                 # Downloaded Zenodo data (NOT in repo)
│   ├── converted/           # Type-converted data (NOT in repo)
│   ├── clean/               # Balanced 160-song dataset (NOT in repo)
│   ├── extracted/           # Extracted rhythm features (NOT in repo)
│   └── README.md            # Data source and preprocessing details
├── notebooks/
│   ├── 00_Preprocessing.ipynb
│   ├── 01_Dataset_Exploration.ipynb
│   ├── 02_Rhythm_Feature_Extraction.ipynb
│   ├── 03_Exploratory_Rhythm_Analysis.ipynb
│   ├── 04_Segment_Similarity.ipynb
│   ├── 05_Clustering_Analysis.ipynb
│   ├── 06_Statistical_Analysis.ipynb
│   ├── 07_Publication_Figures.ipynb
│   └── 08_Classification_Baseline.ipynb
├── utils/
│   ├── data_type_conversion.py
│   ├── gender_correction.py
│   ├── song_selection.py
│   ├── feature_extraction.py
│   └── similarity.py
├── figures/                 # Generated figures
├── tables/                  # Generated result tables
├── requirements.txt
└── README.md
```

---

## Dataset

The raw data is **not included** in this repository because of its size (the full Zenodo record is approximately **22.8 GB** of compressed archives). It uses the publicly available Indian Folk Music Dataset hosted on Zenodo. The Folk dataset contains Mel-spectrogram features extracted from **3-second audio segments using a 1/2-second sliding window**, covering **15 Indian folk styles**, of which this project analyzes 8. See [`data/README.md`](data/README.md) for source details and the preprocessing pipeline.

**Indian Folk Music Dataset**
Y. Singh, L. Waikhom, V. Meena, A. Biswas (2022). Zenodo.
https://zenodo.org/records/6584021 (DOI: 10.5281/zenodo.6584021)

### Curated subset

| Genre | Segments | Artists | Male segments | Female segments |
|---|---:|---:|---:|---:|
| Bauls | 8,450 | 8 | 4,684 | 3,766 |
| Bhatiali | 8,808 | 7 | 6,915 | 1,893 |
| Gidha | 8,228 | 9 | 4,560 | 3,668 |
| Kajri | 20,580 | 6 | 10,636 | 9,944 |
| Maand | 17,796 | 8 | 8,530 | 9,266 |
| Sohar | 12,994 | 5 | 7,158 | 5,836 |
| Sufi | 19,213 | 9 | 11,360 | 7,853 |
| Uttarakhandi | 13,020 | 7 | 9,765 | 3,255 |
| **Total** | **109,089** | **59** | | |

The curated dataset in `data/clean/` is approximately **6.82 GB**. Each segment is a Mel-spectrogram of shape **(128, 130)**. Selection is done at the **song level**: 20 unique songs per genre, and **all** segments of a selected song are kept. Per-segment metadata includes folk style / `genre`, `state`, `artist`, `gender`, `song`, `source` / `source_file`, and artist and genre IDs.

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/Ankit6321/indian-folk-music-rhythm-analysis.git
cd indian-folk-music-rhythm-analysis
pip install -r requirements.txt
```

### 2. Download the data

Download the `.7z` archives for the 8 genres used here from the Zenodo link above (about 12.6 GB compressed), extract them, and place the genre `.pickle` files in:

```text
data/raw/
```

### 3. Preprocess

Preprocessing reduces the raw data to the balanced 20-songs-per-genre dataset in three stages. The scripts use relative paths (`../data/...`), so run them from inside the `utils/` folder:

```bash
cd utils
python data_type_conversion.py
python gender_correction.py     # add --dry-run to preview changes
python song_selection.py
```

1. **Data type conversion** (`utils/data_type_conversion.py`): converts byte-string metadata to UTF-8 strings, ID and count fields to integers, and Mel-spectrograms to `float32`. Genres are processed one at a time to limit memory use. Output goes to `data/converted/`.
2. **Gender label correction** (`utils/gender_correction.py`): fixes typos and inconsistent spellings in the `gender` field of `data/converted/` (for example `femlae`, `Female `, `FEMALE`) so that every label is exactly `Male` or `Female`. Values it cannot resolve safely are reported for manual review instead of being guessed.
3. **Song selection** (`utils/song_selection.py`): for each of the 8 genres, selects 20 unique songs at the song level. Only songs with a single vocalist gender are candidates. Up to 10 female songs are chosen (all of them if fewer than 10 exist) and the rest are male songs, using a fixed random seed (42). All segments of the selected songs are kept. Output goes to `data/clean/`.

Files in `data/raw/` are never modified. `notebooks/00_Preprocessing.ipynb` is an initial inspection of a raw file (keys, shapes, metadata, song and gender counts), not part of the scripted pipeline.

### 4. Run the analysis

Run the notebooks in order (`00` to `08`). Each notebook reads from `data/clean/` or `data/extracted/` and writes to `figures/` and `tables/`.

| Notebook | Purpose |
|---|---|
| `00_Preprocessing` | Initial inspection of the raw data (keys, shapes, metadata, song/gender counts) |
| `01_Dataset_Exploration` | Structure, metadata, counts, gender distribution, sample spectrograms |
| `02_Rhythm_Feature_Extraction` | Extract 34 rhythm parameters per segment |
| `03_Exploratory_Rhythm_Analysis` | Feature distributions and genre-wise exploration |
| `04_Segment_Similarity` | Within- vs across-genre cosine similarity |
| `05_Clustering_Analysis` | K-NN neighborhood agreement, PCA |
| `06_Statistical_Analysis` | Kruskal-Wallis, FDR correction, eta-squared |
| `07_Publication_Figures` | Report-ready figures |
| `08_Classification_Baseline` | Song-grouped Random Forest and SVM |

---

## Rhythm Features

34 parameters were extracted from each Mel-spectrogram, covering:

- **Energy distribution:** mean, std, max, min, range, skewness
- **Spectral flux:** sum, mean
- **Frame-level entropy:** mean, std
- **Autocorrelation:** peak value and lag
- **Tempogram descriptors:** dominant lag, stability, energy, variance
- **Onset and peak metrics:** onset density, peak count

`tempogram_stability` was constant across the whole corpus and was removed, leaving **33 usable parameters**.

---

## Methods

**Unsupervised analysis.** Genre centroids are compared with cosine similarity and Euclidean distance. K-NN (k=5) measures how often a segment's nearest neighbors share its genre. PCA on z-scored features visualizes genre overlap.

**Statistical testing.** Most features violate normality (93%) and homogeneity of variance (97%), so the **Kruskal-Wallis H-test** is used, with **Benjamini-Hochberg FDR** correction across 33 tests and **eta-squared** effect sizes to separate significance from practical importance.

**Supervised classification.** Random Forest (`n_estimators=300`, balanced subsample weights) and SVM (RBF, `C=10`, `gamma=scale`, balanced weights) are trained on standardized features. Because all segments of a song are highly correlated, evaluation is **song-grouped**: 20% of songs are held out entirely, and 5-fold `GroupKFold` is used on the rest. Three dummy classifiers provide chance baselines.

---

## Results

### Unsupervised

- Mean within-genre cosine similarity: **0.0737** vs across-genre **0.0031**
- K-NN neighborhood agreement (chance ≈ 12.5%): Sufi **43.1%**, Maand **34.8%**, Uttarakhandi **34.1%**, Bauls lowest at **17.4%**
- PCA: PC1 explains 27.9% and PC2 21.6% of variance; 10 components are needed for over 87%, so no single parameter dominates

### Statistical

- 32 of 33 parameters significant after FDR correction (p < 0.001)
- Largest effect sizes: `energy_min` (η² = 0.155) and `frame_entropy_mean` (η² = 0.149), both small-to-moderate by Cohen's conventions

### Classification (song-grouped)

| Model | CV Accuracy | CV Macro-F1 | Held-out Acc. | Held-out Macro-F1 |
|---|---|---|---|---|
| Dummy (uniform) | 12.6% | N/A | N/A | N/A |
| Dummy (stratified) | 13.1% | N/A | N/A | N/A |
| Dummy (most frequent) | 16.8% | N/A | N/A | N/A |
| Random Forest | 28.9% ± 5.1% | 0.279 ± 0.041 | N/A | N/A |
| **SVM (RBF)** | **32.7% ± 4.9%** | **0.304 ± 0.039** | **40.4%** | **0.366** |

Held-out test set: 18,256 segments from 32 unseen songs.

**Per-genre performance (SVM, held-out):**

| Genre | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Bauls | 0.30 | 0.33 | 0.31 | 2,324 |
| Bhatiali | 0.20 | 0.25 | 0.22 | 1,300 |
| Gidha | 0.25 | 0.45 | 0.32 | 755 |
| Kajri | 0.33 | 0.24 | 0.28 | 3,063 |
| Maand | 0.25 | 0.25 | 0.25 | 1,972 |
| Sohar | 0.61 | 0.65 | 0.63 | 3,609 |
| Sufi | 0.54 | 0.54 | 0.54 | 3,165 |
| Uttarakhandi | 0.44 | 0.32 | 0.37 | 2,068 |

### Key takeaways

- Rhythm carries real, generalizable genre information, but it is **moderate rather than strongly separating**.
- Sufi and Sohar are the most classifiable; Bhatiali, Maand, and Kajri are weakly separable.
- Univariate significance and multivariate predictive importance disagree: `energy_min` has the largest effect size but ranks only 9th in Random Forest importance, while `modulation_dominant_freq_bin` ranks 2nd. `frame_entropy_mean` ranks first by both measures.

---

## Limitations

- Features are computed from **pre-computed Mel-spectrograms**, not raw audio, which limits onset and micro-timing resolution.
- Genre and state labels from the source datasets are treated as ground truth without independent verification.
- The eight genres do not cover all North and East Indian folk traditions.
- Only classical ML on hand-crafted features was used; deep models may capture additional structure.
- Statistical significance on a corpus this large does not imply practical discriminability.

## Future Work

- Train CNN / CNN-RNN models end-to-end on Mel-spectrograms, especially for Bhatiali, Maand, and Kajri
- Analyze confusion at the genre-pair level (e.g. Bhatiali/Bauls, Kajri/Maand) to separate true rhythmic overlap from shared instrumentation
- Expand to more folk traditions and extend toward raga-correspondence analysis for the broader IKS project

---

## Acknowledgement

This research was funded under grant number **2-146/IKS2.0/InternshipProgram/2026-27/102** for the project *"Analyzing the Raag Origins of Indian Traditional Folk Music"* by the **IKS Division, Ministry of Education, Government of India**. The Principal Investigator is Dr. Anupam Biswas.