#!/usr/bin/env python3

"""
gb_builder.py

Build a GenBank file from:

    FASTA
    +
    merged GFF3

The resulting GenBank file is intended
for visualization with OGDRAW.

Usage:

    python gb_builder.py \
        input.fsa \
        merged.gff3 \
        output.gb
"""

import argparse
from pathlib import Path

from BCBio import GFF
from Bio import SeqIO


def main():

    parser = argparse.ArgumentParser(
        description="Build GenBank file from FASTA + GFF3."
    )

    parser.add_argument(
        "fasta",
        help="Input FASTA file"
    )

    parser.add_argument(
        "gff3",
        help="Input merged GFF3 file"
    )

    parser.add_argument(
        "output",
        help="Output GenBank file"
    )

    args = parser.parse_args()

    if not Path(args.fasta).exists():
        raise FileNotFoundError(args.fasta)

    if not Path(args.gff3).exists():
        raise FileNotFoundError(args.gff3)

    print(f"[INFO] Reading FASTA : {args.fasta}")
    print(f"[INFO] Reading GFF3  : {args.gff3}")

    seq_dict = SeqIO.to_dict(
        SeqIO.parse(args.fasta, "fasta")
    )

    with open(args.gff3) as gff:

        records = list(
            GFF.parse(
                gff,
                base_dict=seq_dict
            )
        )

    print(f"[INFO] Parsed records : {len(records)}")

    total_features = 0

    for rec in records:

        rec.annotations["molecule_type"] = "DNA"

        new_features = []

        for feat in rec.features:

            #
            # gene features
            #
            if feat.type == "gene":

                gene = None

                if "Name" in feat.qualifiers:
                    gene = feat.qualifiers["Name"][0]

                elif "ID" in feat.qualifiers:
                    gene = feat.qualifiers["ID"][0]

                if gene:

                    feat.qualifiers = {
                        "gene": [gene]
                    }

                new_features.append(feat)
                total_features += 1

            #
            # CDS / tRNA / rRNA
            #
            if hasattr(feat, "sub_features"):

                for sf in feat.sub_features:

                    gene = None

                    if "gene" in sf.qualifiers:
                        gene = sf.qualifiers["gene"][0]

                    elif "Parent" in sf.qualifiers:
                        gene = sf.qualifiers["Parent"][0]

                    q = {}

                    if gene:

                        q["ID"] = [gene]
                        q["Name"] = [gene]
                        q["gene"] = [gene]

                    for key in (
                        "product",
                        "protein_id",
                        "source",
                        "score",
                        "phase",
                    ):

                        if key in sf.qualifiers:
                            q[key] = sf.qualifiers[key]

                    sf.qualifiers = q

                    new_features.append(sf)
                    total_features += 1

        rec.features = new_features

    SeqIO.write(
        records,
        args.output,
        "genbank"
    )

    print(f"[INFO] Features written : {total_features}")
    print(f"[INFO] Saved           : {args.output}")


if __name__ == "__main__":
    main()