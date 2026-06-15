#!/usr/bin/env python3

"""
mitoannotate.py

Master pipeline for mitochondrial genome annotation.

WORKFLOWS
=========

1) GeneMark-only workflow
-------------------------

Predict and annotate protein-coding genes.

Steps:

    blastp_mito_hits.py
        ↓
    add_gene_names.py
        ↓
    gff2_to_gff3.py
        ↓
    gb_builder.py

Output:

    PREFIX/
        PREFIX.gb


2) MFannot-only workflow
------------------------

Convert MFannot annotations and retain
only RNA features (tRNAs and rRNAs).

Steps:

    tbl_to_gff3.py
        ↓
    keep_features.py
        ↓
    gb_builder.py

Output:

    PREFIX/
        PREFIX.gb


3) Full workflow
----------------

Combine GeneMark protein-coding genes
with MFannot RNA annotations.

Steps:

    GeneMark branch
        ↓
    MFannot branch
        ↓
    gff_concat_and_sorting.py
        ↓
    gb_builder.py

Output:

    PREFIX/
        PREFIX.gb


EXAMPLES
========

GeneMark only:

    python mitoannotate.py genemark \
        --faa sample.faa \
        --gff sample.gff \
        --fasta sample.fsa \
        --db paramecium_mito_db \
        --prefix sample


MFannot only:

    python mitoannotate.py mfannot \
        --tbl sample.tbl \
        --fasta sample.fsa \
        --prefix sample


Full workflow:

    python mitoannotate.py full \
        --faa sample.faa \
        --gff sample.gff \
        --tbl sample.tbl \
        --fasta sample.fsa \
        --db paramecium_mito_db \
        --prefix sample


RESULTS
=======

All intermediate files are saved inside:

    PREFIX/

allowing manual inspection and curation
at every step of the workflow.
"""

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parent /
    "scripts"
)


def run(cmd):

    print()
    print("[RUN]")
    print(" ".join(map(str, cmd)))
    print()

    subprocess.run(cmd, check=True)


def script(name):

    path = SCRIPT_DIR / name

    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find script: {path}"
        )

    return str(path)


def genemark_branch(args, results):

    blast_hits = results / f"{args.prefix}_blastp_mito_hits.tsv"

    named_gff = results / f"{args.prefix}_named.gff"

    genemark_gff3 = results / f"{args.prefix}_genemark.gff3"

    run([
        sys.executable,
        script("blastp_mito_hits.py"),
        args.faa,
        args.db,
        str(blast_hits)
    ])

    run([
        sys.executable,
        script("add_gene_names.py"),
        str(blast_hits),
        args.gff,
        str(named_gff)
    ])

    run([
        sys.executable,
        script("gff2_to_gff3.py"),
        str(named_gff),
        str(genemark_gff3)
    ])

    return genemark_gff3


def mfannot_branch(args, results):

    mfannot_gff3 = results / f"{args.prefix}_mfannot.gff3"

    mfannot_keep = results / f"{args.prefix}_mfannot_keep.gff3"

    run([
        sys.executable,
        script("tbl_to_gff3.py"),
        args.tbl,
        str(mfannot_gff3)
    ])

    run([
        sys.executable,
        script("keep_features.py"),
        str(mfannot_gff3),
        str(mfannot_keep)
    ])

    return mfannot_keep


def main():

    parser = argparse.ArgumentParser(
        description="Mitochondrial annotation pipeline"
    )

    parser.add_argument(
        "mode",
        choices=[
            "genemark",
            "mfannot",
            "full"
        ]
    )

    parser.add_argument(
        "--faa",
        help="GeneMark protein FASTA (.faa)"
    )

    parser.add_argument(
        "--gff",
        help="GeneMark GFF file"
    )

    parser.add_argument(
        "--tbl",
        help="MFannot .tbl file"
    )

    parser.add_argument(
        "--fasta",
        help="Genome FASTA file"
    )

    parser.add_argument(
        "--db",
        help="BLAST database prefix"
    )

    parser.add_argument(
        "--prefix",
        required=True,
        help="Output prefix"
    )

    args = parser.parse_args()

    #
    # Validate inputs
    #

    if args.mode == "genemark":

        required = [
            args.faa,
            args.gff,
            args.fasta,
            args.db
        ]

        if any(x is None for x in required):

            parser.error(
                "genemark mode requires "
                "--faa --gff --fasta --db"
            )

    elif args.mode == "mfannot":

        required = [
            args.tbl,
            args.fasta
        ]

        if any(x is None for x in required):

            parser.error(
                "mfannot mode requires "
                "--tbl --fasta"
            )

    elif args.mode == "full":

        required = [
            args.faa,
            args.gff,
            args.tbl,
            args.fasta,
            args.db
        ]

        if any(x is None for x in required):

            parser.error(
                "full mode requires "
                "--faa --gff --tbl --fasta --db"
            )

    #
    # Results directory
    #

    results = Path(args.prefix)

    results.mkdir(
        exist_ok=True
    )

    print()
    print(f"[INFO] Results directory: {results}")
    print()

    #
    # GeneMark workflow
    #

    if args.mode == "genemark":

        genemark_gff3 = genemark_branch(
            args,
            results
        )

        gb = results / f"{args.prefix}.gb"

        run([
            sys.executable,
            script("gb_builder.py"),
            args.fasta,
            str(genemark_gff3),
            str(gb)
        ])

    #
    # MFannot workflow
    #

    elif args.mode == "mfannot":

        mfannot_gff3 = mfannot_branch(
            args,
            results
        )

        gb = results / f"{args.prefix}.gb"

        run([
            sys.executable,
            script("gb_builder.py"),
            args.fasta,
            str(mfannot_gff3),
            str(gb)
        ])

    #
    # Full workflow
    #

    elif args.mode == "full":

        genemark_gff3 = genemark_branch(
            args,
            results
        )

        mfannot_gff3 = mfannot_branch(
            args,
            results
        )

        merged = results / f"{args.prefix}_merged.gff3"

        run([
            sys.executable,
            script("gff_concat_and_sorting.py"),
            str(genemark_gff3),
            str(mfannot_gff3),
            str(merged)
        ])

        gb = results / f"{args.prefix}.gb"

        run([
            sys.executable,
            script("gb_builder.py"),
            args.fasta,
            str(merged),
            str(gb)
        ])

    print()
    print("[DONE]")
    print(f"Results directory: {results}")
    print()


if __name__ == "__main__":
    main()