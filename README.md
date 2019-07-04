# BUSCOMP: BUSCO Compiler and Comparison tool

BUSCOMP is designed to overcome some of the non-deterministic limitations of BUSCO to:

1. compile a non-redundant maximal set of complete BUSCOs from a set of assemblies, and
2. use this set to provide a "true" comparison of completeness between different assemblies of the same genome
with predictable behaviour.

Full documentation is available in the [BUSCOMP.md](./BUSCOMP.md) file included in this repository. For a better rendering and navigation of this document, please download and open [`./docs/buscomp.docs.html`](./docs/buscomp.docs.html). This documentation can also be generated by running BUSCOMP with the `dochtml=T` option. (R and pandoc must be installed - see docs.) 

For a quick start guide with example data, see [QUICKSTART.md](./QUICKSTART.md). You will need [Minimap2](https://github.com/lh3/minimap2) installed. Example BUSCO runs are provided, but for real life use you will also want to install [BUSCO](https://busco.ezlab.org/).

If you just want to look at example output, please see the [`./example/run/yeast.N3L20ID0U.html`](https://github.com/slimsuite/buscomp/blob/master/example/run/yeast.N3L20ID0U.html) and [`./example/run/yeast.N3L20ID0U.full.html`](https://github.com/slimsuite/buscomp/blob/master/example/run/yeast.N3L20ID0U.full.html). (Results for a full example run are available in the [`./example/run/`](./example/run/) directory.)

## Citing BUSCOMP

BUSCOMP is not yet published, but the paper is in preparation. If you want to use BUSCOMP in a publication in the meantime, please cite the GSA2019 presentation on F1000Research:

* **<u>Edwards RJ</u> (2019):** BUSCOMP: BUSCO compilation and comparison – Assessing completeness in multiple genome assemblies [version 1; not peer reviewed]. _F1000Research_ **8:**995 (slides) (doi: [10.7490/f1000research.1116972.1](https://f1000research.com/slides/8-995))

---

<small>&copy; 2019 Richard Edwards | richard.edwards@unsw.edu.au</small>
