#!/usr/bin/env python3

"""
add_gene_names.py

Annotate GeneMark predictions using BLASTP hits.

Input:
    blast_hits.tsv    Output of blastp_mito_hits.py
    genemark.gff      GeneMark GFF2 file

Output:
    named.gff         GeneMark GFF with gene names added

Genes without a BLAST hit are retained and labelled as "orf"
for manual curation.
"""

import argparse
import re
from pathlib import Path


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Add gene names from BLASTP annotations "
            "to a GeneMark GFF file."
        )
    )

    parser.add_argument(
        "blast_file",
        help="BLAST annotation table (.tsv)"
    )

    parser.add_argument(
        "gff_file",
        help="GeneMark GFF file"
    )

    parser.add_argument(
        "output",
        help="Output annotated GFF"
    )

    args = parser.parse_args()

    if not Path(args.blast_file).exists():
        raise FileNotFoundError(
            f"BLAST file not found: {args.blast_file}"
        )

    if not Path(args.gff_file).exists():
        raise FileNotFoundError(
            f"GFF file not found: {args.gff_file}"
        )

    print(f"[INFO] Reading BLAST annotations: {args.blast_file}")

    names = {}

    with open(args.blast_file) as fh:

        next(fh)  # skip header

        for line in fh:

            fields = line.rstrip("\n").split("\t")

            gene_id = fields[0]

            gid = gene_id.split("|")[0]
            gid = re.sub(r"^gene_", "", gid)

            gene = fields[4].lower()

            # Normalize naming
            gene = re.sub(r"^nadh", "nad", gene)
            gene = re.sub(r"^rpl", "rpl", gene)
            gene = re.sub(r"^rps", "rps", gene)

            names[gid] = gene

    annotated = 0
    unknown = 0

    print(f"[INFO] Annotating GFF: {args.gff_file}")

    with open(args.gff_file) as fin, open(args.output, "w") as fout:

        for line in fin:

            if line.startswith("#"):
                fout.write(line)
                continue

            cols = line.rstrip("\n").split("\t")

            if len(cols) < 9:
                fout.write(line)
                continue

            m = re.search(r"gene_id=(\d+)", cols[8])

            if m:

                gid = m.group(1)

                gene = names.get(gid)

                if gene is None:
                    gene = "orf"
                    unknown += 1
                else:
                    annotated += 1

                cols[8] += f";gene={gene}"

            fout.write("\t".join(cols) + "\n")

    print(f"[INFO] Annotated genes : {annotated}")
    print(f"[INFO] Putative ORFs   : {unknown}")
    print(f"[INFO] Saved          : {args.output}")


if __name__ == "__main__":
    main()