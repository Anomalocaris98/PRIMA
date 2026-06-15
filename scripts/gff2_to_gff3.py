#!/usr/bin/env python3

"""
gff2_to_gff3.py

Convert GeneMark GFF2 output into GFF3 format.

Each CDS prediction is converted into:

    gene
      └── CDS

Input:
    input.gff

Output:
    output.gff3

Example:
    python gff2_to_gff3.py \
        sample_named.gff \
        sample_named.gff3
"""

import argparse
import re
from pathlib import Path


def main():

    parser = argparse.ArgumentParser(
        description="Convert GeneMark GFF2 to GFF3."
    )

    parser.add_argument(
        "input",
        help="Input GeneMark GFF2 file"
    )

    parser.add_argument(
        "output",
        help="Output GFF3 file"
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(args.input)

    print(f"[INFO] Reading: {args.input}")

    n_features = 0

    with open(args.output, "w") as out:

        out.write("##gff-version 3\n")

        with open(args.input) as fh:

            for line in fh:

                line = line.rstrip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                cols = re.split(
                    r"\s+",
                    line,
                    maxsplit=8
                )

                if len(cols) != 9:
                    continue

                (
                    seqid,
                    source,
                    feature,
                    start,
                    end,
                    score,
                    strand,
                    phase,
                    attrs
                ) = cols

                m = re.search(
                    r"gene_id=(\d+)",
                    attrs
                )

                if not m:
                    continue

                gid = m.group(1)

                g = re.search(
                    r"gene=([^;]+)",
                    attrs
                )

                if g:
                    gene_name = g.group(1)
                else:
                    gene_name = f"gene_{gid}"

                out.write(
                    f"{seqid}\t{source}\tgene\t"
                    f"{start}\t{end}\t.\t"
                    f"{strand}\t.\t"
                    f"ID={gene_name};Name={gene_name}\n"
                )

                out.write(
                    f"{seqid}\t{source}\tCDS\t"
                    f"{start}\t{end}\t"
                    f"{score}\t{strand}\t{phase}\t"
                    f"ID={gene_name}_CDS;"
                    f"Parent={gene_name};"
                    f"gene={gene_name}\n"
                )

                n_features += 1

    print(f"[INFO] Converted CDSs : {n_features}")
    print(f"[INFO] Saved          : {args.output}")


if __name__ == "__main__":
    main()