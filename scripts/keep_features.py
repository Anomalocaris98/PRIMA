#!/usr/bin/env python3
#keeping rna and trna genes from the mfannot gff3 file
#usage: python keep_features.py \
#    input_mfannot.gff \
#    output_mfannot_keep.gff

import sys
import re

input_gff = sys.argv[1]
output_gff = sys.argv[2]

with open(input_gff) as fin, open(output_gff, "w") as fout:

    for line in fin:

        if line.startswith("#"):
            fout.write(line)
            continue

        cols = line.rstrip("\n").split("\t")

        if len(cols) < 9:
            continue

        feature = cols[2]
        attrs = cols[8]

        if feature == "gene":

            if re.search(r'ID=(trn|rnl|rns)', attrs):
                fout.write(line)

        else:

            if re.search(r'Parent=(trn|rnl|rns)', attrs):
                fout.write(line)