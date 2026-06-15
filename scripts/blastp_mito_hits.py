#!/usr/bin/env python3

"""
blastp_mito_hits.py

Compare GeneMark-predicted proteins against a custom mitochondrial
protein database using BLASTP.

Input:
    query.faa      GeneMark protein FASTA
    blast_db       BLAST database prefix

Output:
    output.tsv     BLAST annotation table

Example:
    python blastp_mito_hits.py \
        sample.faa \
        mito_db \
        sample_blastp_mito_hits.tsv

Custom parameters:

    python blastp_mito_hits.py \
        sample.faa \
        mito_db \
        sample_blastp_mito_hits.tsv \
        --evalue 1e-5 \
        --threads 8
"""

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Annotate GeneMark proteins using BLASTP "
            "against a custom mitochondrial protein database."
        )
    )

    parser.add_argument(
        "query",
        help="GeneMark protein FASTA (.faa)"
    )

    parser.add_argument(
        "db",
        help="BLAST database prefix"
    )

    parser.add_argument(
        "output",
        help="Output TSV file"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=32,
        help="Number of BLAST threads (default: 32)"
    )

    parser.add_argument(
        "--evalue",
        type=float,
        default=1e-10,
        help="BLAST E-value cutoff (default: 1e-10)"
    )

    args = parser.parse_args()

    if not Path(args.query).exists():
        raise FileNotFoundError(
            f"Query file not found: {args.query}"
        )

    print("[INFO] Running BLASTP")
    print(f"[INFO] Query    : {args.query}")
    print(f"[INFO] Database : {args.db}")
    print(f"[INFO] E-value  : {args.evalue}")
    print(f"[INFO] Threads  : {args.threads}")

    with tempfile.NamedTemporaryFile(mode="w+") as tmp:

        subprocess.run(
            [
                "blastp",
                "-query", args.query,
                "-db", args.db,
                "-outfmt",
                "6 qseqid sseqid pident length qlen slen qstart qend evalue",
                "-evalue", str(args.evalue),
                "-max_target_seqs", "1",
                "-max_hsps", "1",
                "-num_threads", str(args.threads)
            ],
            stdout=tmp,
            check=True
        )

        tmp.flush()
        tmp.seek(0)

        with open(args.output, "w", newline="") as out:

            writer = csv.writer(
                out,
                delimiter="\t"
            )

            writer.writerow([
                "gene_id",
                "start",
                "end",
                "strand",
                "gene_name",
                "pident",
                "qcov",
                "scov",
                "qstart",
                "qend",
                "evalue"
            ])

            for line in tmp:

                (
                    qseqid,
                    sseqid,
                    pident,
                    length,
                    qlen,
                    slen,
                    qstart,
                    qend,
                    evalue
                ) = line.rstrip().split("\t")

                fields = qseqid.split("|")

                strand = fields[3]
                start = fields[4]
                end = fields[5]

                gene_name = sseqid.split("|")[0]

                qcov = (
                    f"{100 * int(length) / int(qlen):.2f}"
                )

                scov = (
                    f"{100 * int(length) / int(slen):.2f}"
                )

                writer.writerow([
                    qseqid,
                    start,
                    end,
                    strand,
                    gene_name,
                    pident,
                    qcov,
                    scov,
                    qstart,
                    qend,
                    evalue
                ])

    print(f"[INFO] Saved: {args.output}")


if __name__ == "__main__":
    main()