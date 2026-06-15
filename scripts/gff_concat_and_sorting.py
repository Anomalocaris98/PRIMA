#!/usr/bin/env python3
#works as follows: python3 gff_concat_and_sorting.py genemark.gff3 mfannot.gff3 merged.gff3
import sys

gff1 = sys.argv[1]
gff2 = sys.argv[2]
out  = sys.argv[3]

features = []

for gff in (gff1, gff2):

    with open(gff) as fh:

        for line in fh:

            if not line.strip():
                continue

            if line.startswith("#"):
                continue

            cols = line.rstrip("\n").split("\t")

            if len(cols) < 9:
                continue

            features.append(cols)

features.sort(
    key=lambda x: (x[0], int(x[3]))
)

with open(out, "w") as fh:

    fh.write("##gff-version 3\n")

    for cols in features:

        fh.write("\t".join(cols) + "\n")