#!/usr/bin/env python3

"""
prima.py

Master pipeline for protist mitochondrial genome annotation

INPUT FILES
=========
The pipeline automatically looks for:

    PREFIX.faa #genemarkS proteins FASTA
    PREFIX.gff #genemarkS gff2 output file
    PREFIX.tbl #MFAnnot output file
    PREFIX.fsa #assembled mitogenome FASTA

in the current working directory.

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

    results/
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

    results/
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

    results/
        PREFIX.gb

BLAST PARAMETERS
================

The GeneMark and Full workflows allow the user
to customize BLASTP settings.

Available options:

    --evalue FLOAT
        BLASTP E-value cutoff
        (default: 1e-10)

    --threads INT
        Number of CPU threads
        (default: 8)

Examples:

    python3 mitoannotate.py genemark \
        --prefix sample \
        --db paramecium_mito_db \
        --evalue 1e-10 \
        --threads 8

    python3 mitoannotate.py full \
        --prefix sample \
        --db paramecium_mito_db \
        --evalue 1e-10 \
        --threads 8

EXAMPLES
========

GeneMark only:

    python3 mitoannotate.py genemark \
        --prefix sample \
        --db paramecium_mito_db \
        --evalue 1e-10 \
        --threads 32


MFannot only:

    python3 mitoannotate.py mfannot \
    --prefix sample


Full workflow:

    python3 mitoannotate.py full \
        --prefix sample \
        --db paramecium_mito_db \
        --evalue 1e-10 \
        --threads 32


RESULTS
=======

All intermediate files are saved inside:

    results/

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

if not SCRIPT_DIR.exists():

    raise FileNotFoundError(
        f"Scripts directory not found: {SCRIPT_DIR}"
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
        str(blast_hits),
        "--evalue", str(args.evalue),
        "--threads", str(args.threads)
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
        "--db",
        help="BLAST database prefix"
    )

    parser.add_argument(
        "--prefix",
        required=True,
        help=(
            "Sample prefix. The pipeline expects "
            "PREFIX.faa, PREFIX.gff, PREFIX.tbl and PREFIX.fsa"
        )   
    )
    
    parser.add_argument(
        "--evalue",
        type=float,
        default=1e-10,
        help="BLASTP E-value cutoff"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=8,
        help="Number of CPU threads"
    )

    args = parser.parse_args()

    #
    # Resolve input files from prefix
    #

    args.faa = f"{args.prefix}.faa"
    args.gff = f"{args.prefix}.gff"
    args.tbl = f"{args.prefix}.tbl"
    args.fasta = f"{args.prefix}.fsa"

    #
    # Validate inputs
    #

    if args.mode in ("genemark", "full"):

        if args.db is None:

            parser.error(
                "--db is required for GeneMark workflows"
            )

        for f in (args.faa, args.gff, args.fasta):

            if not Path(f).exists():

                parser.error(
                    f"Missing required file: {f}"
                )

    if args.mode in ("mfannot", "full"):

        for f in (args.tbl, args.fasta):

            if not Path(f).exists():

                parser.error(
                    f"Missing required file: {f}"
                )

    #
    # Results directory
    #

    results = Path.cwd() / "results"

    results.mkdir(
        exist_ok=True
    )

    print()
    print(f"[INFO] Results directory: {results}")
    print()
    
    normalized_fasta = (
        results /
        f"{args.prefix}_normalized.fsa"
    )

    run([
        sys.executable,
        script("normalize_fasta.py"),
        args.fasta,
        str(normalized_fasta)
    ])

    args.fasta = str(normalized_fasta)

    #
    # GeneMarkS workflow
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