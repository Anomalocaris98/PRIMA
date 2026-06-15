#!/usr/bin/env python3

"""
tbl_to_gff3.py

Convert MFannot .tbl output into GFF3.

Input:
    input.tbl

Output:
    output.gff3

Example:
    python tbl_to_gff3.py \
        sample.tbl \
        sample_mfannot.gff3
"""

import argparse
from pathlib import Path


def main():

    parser = argparse.ArgumentParser(
        description="Convert MFannot TBL output to GFF3."
    )

    parser.add_argument(
        "input",
        help="MFannot .tbl file"
    )

    parser.add_argument(
        "output",
        help="Output GFF3 file"
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(args.input)

    print(f"[INFO] Reading: {args.input}")

    current_gene = None
    seqid = None
    n_features = 0

    with open(args.input) as fh:
        lines = [x.rstrip("\n") for x in fh]

    with open(args.output, "w") as out:

        out.write("##gff-version 3\n")

        i = 0

        while i < len(lines):

            line = lines[i]

            if line.startswith(">Feature"):

                parts = line.split()

                if len(parts) >= 2:
                    seqid = parts[1]

                i += 1
                continue

            if not line:
                i += 1
                continue

            fields = line.split("\t")

            if len(fields) >= 3 and fields[0] and fields[1]:

                start = int(fields[0])
                end = int(fields[1])

                strand = "+"

                if start > end:
                    start, end = end, start
                    strand = "-"

                feature_type = fields[2]

                attrs = {}

                i += 1

                while i < len(lines):

                    nxt = lines[i]

                    if not nxt:
                        i += 1
                        continue

                    f = nxt.split("\t")

                    if len(f) >= 3 and f[0] and f[1]:
                        break

                    if len(f) >= 5 and f[3]:
                        attrs[f[3]] = f[4]

                    i += 1

                if feature_type == "gene":

                    gene = attrs.get(
                        "gene",
                        "unknown"
                    )

                    current_gene = gene

                    out.write(
                        f"C_0\tMFannot\tgene\t"
                        f"{start}\t{end}\t.\t"
                        f"{strand}\t.\t"
                        f"ID={gene};Name={gene}\n"
                    )

                else:

                    product = attrs.get(
                        "product",
                        ""
                    )

                    pid = attrs.get(
                        "protein_id",
                        ""
                    )

                    out.write(
                        f"C_0\tMFannot\t{feature_type}\t"
                        f"{start}\t{end}\t.\t"
                        f"{strand}\t.\t"
                        f"ID={current_gene}_{feature_type};"
                        f"Parent={current_gene};"
                        f"product={product};"
                        f"protein_id={pid}\n"
                    )

                n_features += 1

            else:
                i += 1

    print(f"[INFO] Features written : {n_features}")
    print(f"[INFO] Saved            : {args.output}")


if __name__ == "__main__":
    main()