import argparse
import difflib
import os
import pickle
import re
import sys
from collections import Counter

import numpy as np

CONVERTED_DIR = "../data/converted"

GENRES = [
    "Bauls", "Bhatiali", "Gidha", "Kajri",
    "Maand", "Sohar", "Sufi", "Uttarakhandi",
]


def normalize(label):
    """Return 'Male', 'Female' or None (could not decide safely)."""
    s = re.sub(r"[^a-z]", "", str(label).lower())
    if not s:
        return None
    if s == "male":
        return "Male"
    if s == "female":
        return "Female"

    r_male = difflib.SequenceMatcher(None, s, "male").ratio()
    r_female = difflib.SequenceMatcher(None, s, "female").ratio()

    if s[0] == "f" and r_female >= 0.6:
        return "Female"
    if s[0] == "m" and r_male >= 0.6:
        return "Male"

    best, other = max(r_male, r_female), min(r_male, r_female)
    if best >= 0.75 and (best - other) >= 0.10:
        return "Female" if r_female > r_male else "Male"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change without writing any file")
    args = ap.parse_args()

    unresolved = {}
    total_fixed = 0

    for genre in GENRES:
        path = os.path.join(CONVERTED_DIR, genre + ".pickle")
        if not os.path.exists(path):
            print(f"[skip] {path} not found")
            continue

        with open(path, "rb") as f:
            df = pickle.load(f)

        gender = np.asarray(df["gender"]).astype(str)
        counts = Counter(gender.tolist())
        print(f"\n=== {genre} ===")
        print("Distinct values before:", dict(counts))

        mapping = {}
        for raw_value in counts:
            fixed = normalize(raw_value)
            if fixed is None:
                unresolved.setdefault(genre, []).append(raw_value)
            else:
                mapping[raw_value] = fixed

        changes = {k: v for k, v in mapping.items() if k != v}
        for k, v in changes.items():
            print(f"  fix: {k!r} -> {v!r}   ({counts[k]} segments)")

        if not changes:
            print("  no corrections needed")
            continue

        new_gender = np.array([mapping.get(g, g) for g in gender.tolist()])
        total_fixed += int(sum(counts[k] for k in changes))
        print("Distinct values after: ", dict(Counter(new_gender.tolist())))

        songs = np.asarray(df["song"]).astype(str)
        mixed = [s for s in np.unique(songs)
                 if len(np.unique(new_gender[songs == s])) > 1]
        if mixed:
            print(f"  note: {len(mixed)} song(s) have both genders "
                  "(excluded by song_selection.py)")

        if args.dry_run:
            continue

        df["gender"] = new_gender
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)
        print(f"  saved: {path}")

    print(f"\nSegments corrected: {total_fixed}")
    if unresolved:
        print("\nUNRESOLVED values (not changed, please check manually):")
        for g, vals in unresolved.items():
            print(f"  {g}: {vals}")
        sys.exit(1)
    print("All gender labels are now 'Male' or 'Female'." if not args.dry_run
          else "Dry run finished, no files were modified.")


if __name__ == "__main__":
    main()