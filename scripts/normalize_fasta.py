#!/usr/bin/env python3

"""
normalize_fasta.py

Normalize a FASTA file so that the sequence ID is always:

    C_0

This avoids identifier mismatches between:

    FASTA
    GeneMark
    MFannot
    GFF3
    GenBank

Usage:

    python3 normalize_fasta.py \
        input.fsa \
        output.fsa
"""

import argparse
from pathlib import Path
from Bio import SeqIO


def main():

    parser = argparse.ArgumentParser(
        description="Normalize FASTA headers."
    )

    parser.add_argument(
        "input",
        help="Input FASTA"
    )

    parser.add_argument(
        "output",
        help="Output FASTA"
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(args.input)

    records = list(
        SeqIO.parse(args.input, "fasta")
    )

    if len(records) != 1:
        raise ValueError(
            "Expected a single mitochondrial contig."
        )

    rec = records[0]

    rec.id = "C_0"
    rec.name = "C_0"
    rec.description = "C_0"

    SeqIO.write(
        [rec],
        args.output,
        "fasta"
    )

    print(f"[INFO] Saved: {args.output}")


if __name__ == "__main__":
    main()