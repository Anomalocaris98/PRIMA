# PRIMA

**PRIMA** (**PR**otist **I**ntegrated **M**itogenome **A**nnotation) is a lightweight Python pipeline for the annotation of protist mitochondrial genomes.

The pipeline requires a previously assembled mitochondrial genome FASTA file. This sequence must first be submitted to the GeneMarkS and MFannot web servers to generate the input files required by PRIMA.

PRIMA integrates:

* GeneMarkS protein-coding gene predictions
* BLASTP-based functional annotation against a custom mitochondrial protein database
* MFannot RNA annotations and protein-coding gene predictions
* GenBank file generation for downstream visualization with OGDRAW

---

## Workflow Overview

### 1. Prepare the mitochondrial genome

Start from an assembled mitochondrial genome FASTA file.

Submit the sequence to:

* GeneMarkS: https://exon.gatech.edu/genemarks.cgi
* MFannot: https://megasun.bch.umontreal.ca/apps/mfannotweb/

- MFAnnot outputs a .zip archive; the only file of interest is the .tbl one.
- remember to output a GFF in GeneMarkS webtool, open the results in new browser tabs and save them in new files

### 2. Create a working directory

*** ATTENTION *** Place all files associated with a single mitochondrial genome in the same directory using a common prefix.

Example:

```text
Paramecium_aurelia/
├── Paramecium_aurelia.faa
├── Paramecium_aurelia.gff
├── Paramecium_aurelia.tbl
└── Paramecium_aurelia.fsa
```

where:

```text
.faa  = GeneMarkS predicted proteins
.gff  = GeneMarkS annotation file
.tbl  = MFannot annotation table
.fsa  = mitochondrial genome FASTA
```

The filename prefix must be identical for all files.

### 3. Run PRIMA

PRIMA can be executed in three different modes depending on the desired annotation strategy.From inside the working directory:

*** Full mode (recommended) ***

Combines GeneMarkS and MFannot annotations.

Workflow:

GeneMarkS CDS annotation
            +
MFannot RNA annotation
            ↓
Merged annotation
            ↓
GenBank output

Produces a complete GenBank file containing:

-Protein-coding genes
-tRNAs
-rRNAs
-ORFs



*** GeneMark mode ***

Uses only GeneMarkS predictions.

Workflow:

GeneMarkS proteins
        ↓
BLASTP annotation
        ↓
Gene naming
        ↓
GenBank output

Produces a GenBank file containing only protein-coding genes.

*** MFannot mode ***

Uses only MFannot predictions.

Workflow:

MFannot annotations
        ↓
RNA extraction
        ↓
GenBank output

---

### 4. Visualize the annotation

All the interemediate files are available for inspection or further refinement with any other tool in the *** results *** directory . The final GenBank file can be uploaded directly to OGDRAW https://chlorobox.mpimp-golm.mpg.de/OGDraw.html for graphical visualization.



---

## Requirements

### Python packages

* biopython
* bcbio-gff

Install:

```bash
pip install biopython bcbio-gff
```

### Additional requirements

#### BLAST+

BLAST+ executables must be installed and available in your `$PATH`.

#### Custom mitochondrial protein database

ATTENTION, PRIMA is not shipped with any database. PRIMA assigns putative gene names to GeneMarkS predictions by searching a user-defined protein database with BLASTP.

The database can be fully customized according to the user's taxonomic group or research interests. In the example directory, the BLAST database was build using all manually annotated mitogenomes of the ciliate of the genus Paramecium from https://paramecium.i2bc.paris-saclay.fr/ and the assembled mitogenome FASTA file retrieved from https://ncbi.nlm.nih.gov/nucleotide/NC001324 

Create the BLAST database using:

```bash
makeblastdb \
    -in mito_proteins.faa \
    -dbtype prot \
    -out mito_database
```

and provide the resulting database prefix through:

```bash
--db mito_database
```

The quality and specificity of the final annotation depend on the composition of this database.


---

## Repository Structure

```text
PRIMA/
├── mitoannotate.py
├── scripts/
│   ├── normalize_fasta.py
│   ├── blastp_mito_hits.py
│   ├── add_gene_names.py
│   ├── gff2_to_gff3.py
│   ├── tbl_to_gff3.py
│   ├── keep_features.py
│   ├── gff_concat_and_sorting.py
│   └── gb_builder.py
├── docs/
│   └── mito_annotation_pipeline.pdf
└── README.md
```

---

## Input Files

PRIMA automatically searches the current directory for:

```text
PREFIX.faa
PREFIX.gff
PREFIX.tbl
PREFIX.fsa
```

where `PREFIX` is specified by the user.

---

## GeneMark Workflow

```bash
python3 mitoannotate.py genemark \
    --prefix SAMPLE \
    --db mito_database
```


## MFannot Workflow

```bash
python3 mitoannotate.py mfannot \
    --prefix SAMPLE
```



## Full Workflow

```bash
python3 mitoannotate.py full \
    --prefix SAMPLE \
    --db mito_database
```

---

## Optional BLAST Parameters

### E-value cutoff

```bash
--evalue FLOAT
```

Default:

```text
1e-10
```

### Number of threads

```bash
--threads INT
```

Default:

```text
8
```

Example:

```bash
python3 mitoannotate.py full \
    --prefix SAMPLE \
    --db mito_database \
    --evalue 1e-20 \
    --threads 32
```

---

## Output

Results are written to:

```text
results/
```

and may include:

```text
PREFIX.gb
PREFIX_genemark.gff3
PREFIX_mfannot.gff3
PREFIX_merged.gff3
PREFIX_blastp_mito_hits.tsv
```

The final GenBank file (`PREFIX.gb`) can be uploaded directly to OGDRAW for graphical visualization of the annotated mitochondrial genome.

---

## License

MIT License

---

## Contact

This is version 1 of the pipeline, so erros and bugs are expected. If you want to use this simple tool, kindly cite the GitHub repository. Any other enquire is warmly welcome at andrea.lenti02@gmail.com

---
