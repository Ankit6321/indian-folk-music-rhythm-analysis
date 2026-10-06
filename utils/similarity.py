"""
utils/similarity.py

Similarity and distance utilities for comparing rhythmic feature
representations across genres, states, or arbitrary groupings.
Operates on precomputed feature DataFrames (e.g. rhythm_features.parquet).
"""

from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform


# ----------------------------------------------------------------------
# Feature matrix preparation
# ----------------------------------------------------------------------

def get_feature_columns(df: pd.DataFrame, exclude: Optional[List[str]] = None) -> List[str]:
    """Return numeric feature column names, excluding metadata columns."""
    default_exclude = ["genre", "state", "artist", "gender", "song", "source", "source_file"]
    exclude_cols = set(default_exclude) if exclude is None else set(exclude)
    return [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]


def build_feature_matrix(df: pd.DataFrame, feature_cols: Optional[List[str]] = None) -> np.ndarray:
    """Extract a numeric feature matrix from a DataFrame."""
    cols = feature_cols if feature_cols is not None else get_feature_columns(df)
    return df[cols].to_numpy(dtype=float)


def z_score_normalize(matrix: np.ndarray) -> np.ndarray:
    """Column-wise z-score normalization."""
    mean = np.mean(matrix, axis=0)
    std = np.std(matrix, axis=0)
    std[std == 0] = 1e-10
    return (matrix - mean) / std


# ----------------------------------------------------------------------
# Group centroids
# ----------------------------------------------------------------------

def compute_group_centroids(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: Optional[List[str]] = None,
    normalize: bool = True,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Compute mean feature vector (centroid) per group (e.g. genre or state).
    Returns a DataFrame indexed by group label, and the list of feature columns used.
    """
    cols = feature_cols if feature_cols is not None else get_feature_columns(df)
    matrix = build_feature_matrix(df, cols)

    if normalize:
        matrix = z_score_normalize(matrix)

    work_df = pd.DataFrame(matrix, columns=cols)
    work_df[group_col] = df[group_col].values

    centroids = work_df.groupby(group_col)[cols].mean()
    return centroids, cols


# ----------------------------------------------------------------------
# Cosine similarity
# ----------------------------------------------------------------------

def cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    """Pairwise cosine similarity matrix for rows of a 2D array."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized = matrix / norms
    return normalized @ normalized.T


def group_cosine_similarity(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: Optional[List[str]] = None,
    normalize: bool = True,
) -> pd.DataFrame:
    """Cosine similarity matrix between group centroids, as a labeled DataFrame."""
    centroids, cols = compute_group_centroids(df, group_col, feature_cols, normalize)
    sim = cosine_similarity_matrix(centroids.to_numpy())
    return pd.DataFrame(sim, index=centroids.index, columns=centroids.index)


# ----------------------------------------------------------------------
# Euclidean / general distance
# ----------------------------------------------------------------------

def pairwise_distance_matrix(
    matrix: np.ndarray, metric: str = "euclidean"
) -> np.ndarray:
    """Pairwise distance matrix for rows of a 2D array using scipy pdist."""
    return squareform(pdist(matrix, metric=metric))


def group_distance_matrix(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: Optional[List[str]] = None,
    normalize: bool = True,
    metric: str = "euclidean",
) -> pd.DataFrame:
    """Distance matrix between group centroids, as a labeled DataFrame."""
    centroids, cols = compute_group_centroids(df, group_col, feature_cols, normalize)
    dist = pairwise_distance_matrix(centroids.to_numpy(), metric=metric)
    return pd.DataFrame(dist, index=centroids.index, columns=centroids.index)


# ----------------------------------------------------------------------
# Correlation-based similarity
# ----------------------------------------------------------------------

def group_correlation_matrix(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: Optional[List[str]] = None,
    normalize: bool = True,
    method: str = "pearson",
) -> pd.DataFrame:
    """Correlation matrix between group centroids across feature dimensions."""
    centroids, cols = compute_group_centroids(df, group_col, feature_cols, normalize)
    return centroids.T.corr(method=method)


# ----------------------------------------------------------------------
# Most similar / most dissimilar pairs
# ----------------------------------------------------------------------

def top_similar_pairs(
    similarity_df: pd.DataFrame, n: int = 5, exclude_diagonal: bool = True
) -> pd.DataFrame:
    """Extract top-n most similar group pairs from a similarity matrix."""
    sim = similarity_df.copy()
    if exclude_diagonal:
        np.fill_diagonal(sim.values, -np.inf)

    pairs = []
    labels = sim.index.tolist()
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            pairs.append((labels[i], labels[j], sim.iloc[i, j]))

    pairs_df = pd.DataFrame(pairs, columns=["group_a", "group_b", "similarity"])
    return pairs_df.sort_values("similarity", ascending=False).head(n).reset_index(drop=True)


def top_dissimilar_pairs(similarity_df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Extract top-n most dissimilar group pairs from a similarity matrix."""
    sim = similarity_df.copy()
    labels = sim.index.tolist()

    pairs = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            pairs.append((labels[i], labels[j], sim.iloc[i, j]))

    pairs_df = pd.DataFrame(pairs, columns=["group_a", "group_b", "similarity"])
    return pairs_df.sort_values("similarity", ascending=True).head(n).reset_index(drop=True)


# ----------------------------------------------------------------------
# Per-feature group comparison
# ----------------------------------------------------------------------

def feature_wise_group_deviation(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Standard deviation across group centroids for each feature,
    highlighting which rhythm descriptors differ most between groups.
    """
    centroids, cols = compute_group_centroids(df, group_col, feature_cols, normalize=True)
    deviation = centroids.std(axis=0).sort_values(ascending=False)
    return deviation.to_frame(name="cross_group_std")