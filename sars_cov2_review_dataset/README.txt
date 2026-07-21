SARS-CoV-2 review dataset

Prepared from the uploaded FASTA files for a qualitative review of genomic analysis tools.

Contents:
- reference/: normalized single-record FASTA for Wuhan-Hu-1 reference.
- samples/: normalized single-record FASTA files for six sample genomes.
- combined/sars_cov2_reference_plus_6_samples.fasta: multi-FASTA with reference + samples, suitable for MSA/BLAST/QUAST-style exploratory checks.
- combined/sars_cov2_samples_only.fasta: samples only, recommended for Nextclade input because Nextclade uses its own dataset reference.
- metadata/sars_cov2_fasta_qc_summary.csv: basic FASTA QC summary.

Important notes:
- sample_4, sample_5, and sample_6 headers do not include confirmed Pango/WHO variant labels. Confirm them with Nextclade/Pangolin or NCBI Virus metadata before calling them Omicron/XBB/etc. in the thesis.
- sample_5 has a relatively high number of ambiguous bases and should either be replaced with a cleaner sequence or intentionally used as a low-quality/QC-demonstration sample.
- Bowtie requires reads (FASTQ) and a reference index; these complete genome FASTA files are not read files.
