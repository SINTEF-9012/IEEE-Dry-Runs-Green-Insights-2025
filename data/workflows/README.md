# NHRF Data Pipelines

1. base1 (`nhrf_base1.yaml`) - **conf-1**
   * Using standard biocontainers and tools.
   * Using tools in sequence
2. base2 (`nhrf_base2.yaml`) - **conf-2**
   * Using standard biocontainers and tools
   * parallelizing tool executions using tool chaining
3. optimized (`nhrf_optimized.yaml`) - **conf-3**
   * Using the best performing steps of 1. and 2.
4. optimized2 (`nhrf_optimized2.yaml`) - **conf-4**
   * Switched out `bwa` to `minimap2` tool for the alignment step
   * Use more CPU in the trimming step (increase from 4 to 6)
   * Perform indexing and create dictionary of reference genome in same step
5. conf-5 (`conf-5.yaml`) -- **conf-5**
   * Same as conf-4 but using 2 cpus for all steps
6. conf-6 (`conf-6.yaml`) -- **conf-6**
   * Same as conf-4 ( 6 cpus for trimming, alignment and BSQ)
   * Using all threads (6) for all tools in the alignment step
        * For previous configs, this was not done for the piped samtools.
   * Using all threads (6) in the mark-duplicates step


The following section is a description from Copilot on what it did for the *optimized* (base2) version of the pipeline.
## 1. Parallel Processing for Trimming
`nhrf_base1.yaml` is the base workflow. In `nhrf_optimized1.yaml` we have implemented the following optimization strategies.
Your current trimming processes samples sequentially, but with 4 CPU cores available, you can parallelize:
```bash
# Process both samples in parallel using background jobs
(
fastp -i ${TUMOR_FASTQ1} -I ${TUMOR_FASTQ2} \
        -o ${OUTDIR}/trimmed_tumor_R1.fastq.gz \
        -O ${OUTDIR}/trimmed_tumor_R2.fastq.gz \
        -h ${OUTDIR}/tumor_fastp.html \
        -j ${OUTDIR}/tumor_fastp.json \
        --thread 2
) &

(
fastp -i ${NORMAL_FASTQ1} -I ${NORMAL_FASTQ2} \
        -o ${OUTDIR}/trimmed_normal_R1.fastq.gz \
        -O ${OUTDIR}/trimmed_normal_R2.fastq.gz \
        -h ${OUTDIR}/normal_fastp.html \
        -j ${OUTDIR}/normal_fastp.json \
        --thread 2
)
```
### Note! Increase memory for parallel processing

## 2. Parallel Processing for Mark Duplicates (~50% reduction in mark-duplicates time)
Same approach as in `1.` but for the `mark-duplicates` step.


## 3. Parallel Processing for BQSR 
Same approach as in `1.` and `2.` but for the `base-quality-score` step.
## 4. Optimize BWA Alignment

```bash
# In alignment-bwa template, update the BWA commands:
# Process tumor sample with optimized threading
bwa mem -t 6 -K 100000000 -Y ${REF_GENOME_FILENAME} ${TTUMOR_FASTQ1} ${TTUMOR_FASTQ2} | \
samtools view -@ 1 -Sb - | \
samtools sort -@ 1 -m 4G -o /data/alignment_results/tumor_sorted.bam -

# Process normal sample with optimized threading  
bwa mem -t 6 -K 100000000 -Y ${REF_GENOME_FILENAME} ${TNORMAL_FASTQ1} ${TNORMAL_FASTQ2} | \
samtools view -@ 1 -Sb - | \
samtools sort -@ 1 -m 4G -o /data/alignment_results/normal_sorted.bam -
```

The Real Optimization vs Original:
Original (nhrf_base1.yaml):

-t 6 with -m 2G sort memory
Better Optimization:

-t 6 with -K 100000000 -Y flags and -m 4G sort memory
The improvement comes from the additional BWA flags and increased sort memory, not from reducing threads. The optimization should be:

Keep -t 6 (use all available CPUs)
Add -K 100000000 (memory optimization)
Add -Y (soft clipping optimization)
Increase sort memory to -m 4G
This would give you the true ~20% improvement while fully utilizing your allocated resources


## AI Estimated Total Impact of above optimizations:
Trimming: 50% reduction (from sequential to parallel)
Mark Duplicates: 50% reduction (from sequential to parallel)
BQSR: 50% reduction (from sequential to parallel)
Alignment: 20% reduction (optimized threading)
Overall pipeline CPU hour reduction: ~40-45%

Key Benefits:
Parallel processing utilizes your available 4 CPU cores effectively
Reduced memory per process but increased total memory fits your cluster capacity
Optimized for your file sizes (1.7-4.9Gi FASTQ files)
Maintains quality while accepting reasonable precision trade-offs
These optimizations are specifically tailored to your cluster's 61% CPU utilization capacity and will significantly reduce your total pipeline runtime.

### Note! Optimizations were not nearly as efficient.
The optimization approach suggested by Copilot (Claude Sonnet 4) did not lead to any particular speed-up or reduced CO2/energy consumption.
Therefore we decided to try to switch out the `bwa mem` tool with the alegedly faster `minimap2` tool in the alignment step. This is done in `optimized2`.

## FASTA dict file

Creating dict file from FASTA reference genome file using `gatk CreateSequenceDictionary`:
```txt
FASTA dict file created successfully. Output:
@HD     VN:1.6
@SQ     SN:chr1 LN:248956422    M5:6aef897c3d6ff0c78aff06ac189178dd     UR:file:/data/ref_genome/Homo_sapiens_assembly38.fasta
@SQ     SN:chr2 LN:242193529    M5:f98db672eb0993dcfdabafe2a882905c     UR:file:/data/ref_genome/Homo_sapiens_assembly38.fasta
@SQ     SN:chr3 LN:198295559    M5:76635a41ea913a405ded820447d067b0     UR:file:/data/ref_genome/Homo_sapiens_assembly38.fasta
@SQ     SN:chr4 LN:190214555    M5:3210fecf1eb92d5489da4346b3fddc6e     UR:file:/data/ref_genome/Homo_sapiens_assembly38.fasta
```

## BSQR USER Error

In the `BSQR`-step we have experienced a `USER ERROR`:
```txt
A USER ERROR has occurred: Input files reference and features have incompatible contigs: No overlapping contigs found.
  reference contigs = [chr1, chr2, chr3, chr4, ...]
...
features contigs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, X, Y]
...
A USER ERROR has occurred: Couldn't read file. Error was: /data/final_results/normal_recal_data.table with exception: /data/final_results/normal_recal_data.tab
le (No such file or directory)
```

Just before the `BSQR`-step `USER ERROR` occurred, this is printed in the log:
```txt
21:24:20.514 INFO  BaseRecalibrator - The Genome Analysis Toolkit (GATK) v4.5.0.0
21:24:20.515 INFO  BaseRecalibrator - For support and documentation go to https://software.broadinstitute.org/gatk/
21:24:20.516 INFO  BaseRecalibrator - Executing as root@nhrf-base2-9jw8g-base-quality-score-2849692697 on Linux v6.1.0-37-amd64 amd64
21:24:20.517 INFO  BaseRecalibrator - Java runtime: OpenJDK 64-Bit Server VM v17.0.10-internal+0-adhoc..src
21:24:20.519 INFO  BaseRecalibrator - Start Date/Time: August 4, 2025 at 9:24:20 PM GMT
21:24:20.520 INFO  BaseRecalibrator - ------------------------------------------------------------
21:24:20.521 INFO  BaseRecalibrator - ------------------------------------------------------------
21:24:20.523 INFO  BaseRecalibrator - HTSJDK Version: 4.1.0
21:24:20.524 INFO  BaseRecalibrator - Picard Version: 3.1.1
21:24:20.524 INFO  BaseRecalibrator - Built for Spark Version: 3.5.0
21:24:20.525 INFO  BaseRecalibrator - HTSJDK Defaults.COMPRESSION_LEVEL : 2
21:24:20.526 INFO  BaseRecalibrator - HTSJDK Defaults.USE_ASYNC_IO_READ_FOR_SAMTOOLS : false
21:24:20.527 INFO  BaseRecalibrator - HTSJDK Defaults.USE_ASYNC_IO_WRITE_FOR_SAMTOOLS : true
21:24:20.528 INFO  BaseRecalibrator - HTSJDK Defaults.USE_ASYNC_IO_WRITE_FOR_TRIBBLE : false
21:24:20.529 INFO  BaseRecalibrator - Deflater: IntelDeflater
21:24:20.529 INFO  BaseRecalibrator - Inflater: IntelInflater
21:24:20.530 INFO  BaseRecalibrator - GCS max retries/reopens: 20
21:24:20.530 INFO  BaseRecalibrator - Requester pays: disabled
21:24:20.532 INFO  BaseRecalibrator - Initializing engine
WARNING: BAM index file /data/mark_duplicates/normal_dedup.bai is older than BAM /data/mark_duplicates/normal_dedup.bam
WARNING: BAM index file /data/mark_duplicates/tumor_dedup.bai is older than BAM /data/mark_duplicates/tumor_dedup.bam
21:24:21.809 INFO  FeatureManager - Using codec VCFCodec to read file file:///data/known_sites/00-common_all.vcf.gz
21:24:21.907 INFO  FeatureManager - Using codec VCFCodec to read file file:///data/known_sites/00-common_all.vcf.gz
21:24:22.247 WARN  IndexUtils - Feature file "file:///data/known_sites/00-common_all.vcf.gz" appears to contain no sequence dictionary. Attempting to retrieve
a sequence dictionary from the associated index file
21:24:22.288 WARN  IndexUtils - Feature file "file:///data/known_sites/00-common_all.vcf.gz" appears to contain no sequence dictionary. Attempting to retrieve
a sequence dictionary from the associated index file
21:24:22.414 INFO  BaseRecalibrator - Shutting down engine
[August 4, 2025 at 9:24:22 PM GMT] org.broadinstitute.hellbender.tools.walkers.bqsr.BaseRecalibrator done. Elapsed time: 0.04 minutes.
```
