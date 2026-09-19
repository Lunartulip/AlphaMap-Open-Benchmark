# Research release model

AlphaMap separates three versioned objects: the reusable open benchmark, study-specific Research Note releases and the institutional production feed. They share a semantic contract but do not share an implied coverage claim.

## Release classes

| Release class | Public role | Versioning rule |
| --- | --- | --- |
| Open Benchmark | Data contract, bounded audit sample, conformance tests and reference implementation | Semantic versions and immutable manifests |
| Research Note | Frozen evidence and code supporting one stated research question | Independent study ID and study-release version |
| Institutional Data/API | Licensed point-in-time history and production delivery | Private release IDs, replayable snapshots and contractually defined change control |

The open benchmark is not a reduced copy of every Research Note dataset, and a Research Note is not a representation of the full institutional feed.

## Immutability and corrections

- `data/sample/v1` remains fixed after release. A larger study panel does not silently add rows to that directory.
- A material correction creates a new release, manifest and changelog entry. Prior artifacts remain available for reconstruction.
- Every released study data artifact is covered by a manifest and checksum. Restricted source material is represented by provenance metadata and a data-availability statement rather than redistributed without rights.
- Research results remain tied to the exact dataset release, code commit and protocol used to produce them.

## Required metadata for each Research Note

Each completed study release should register:

1. Study ID, title, research question, authorship and release status.
2. Protocol or pre-registration identifier and the date analysis rules were frozen.
3. Sampling frame, inclusion rules, evidence window and knowledge cutoff.
4. Dataset release ID, schema version, file manifest and SHA-256 checksums.
5. Code commit, environment lock file and deterministic execution instructions.
6. Canonical website URL, repository release URL and data-availability statement.
7. DOI, publication version and correction or supersession links when available.
8. SSRN URL or submission status when a working paper is distributed there.

No registry entry should imply that an unfinished study has a DOI, SSRN posting or completed empirical result.

## Publication workflow

1. Freeze the protocol and define the sampling frame.
2. Build a study-specific snapshot without modifying the released benchmark sample.
3. Validate temporal integrity, lineage, coverage, manifests and research code.
4. Produce the Research Note and data-availability statement.
5. Create a GitHub Release from a signed, version-specific tag; record the commit SHA, manifest and SHA-256 checksums. When repository settings support immutable releases, enable them before publication.
6. Archive the appropriate software, paper or permitted data bundle in Zenodo and record its DOI.
7. Publish the canonical research page and, when useful, submit the working paper PDF to SSRN with links to the DOI and repository release.
8. Issue corrections as new versions; do not overwrite a cited artifact.

Zenodo can archive enabled GitHub releases and mint a DOI for the archived release. A DOI may also be reserved before publication. When an artifact already has a DOI, that DOI should be supplied rather than minting an unintended duplicate for the same object.

## Recommended public topology

- **AlphaMap website:** canonical narrative, methods, figures and current publication status.
- **This repository:** open contract, audit sample, conformance tests, reference code and the index of Research Note releases.
- **GitHub release:** version-specific code tag, study metadata, configuration and checksums; an immutable release is described as such only when GitHub's immutable-release protection is enabled.
- **Zenodo record:** durable DOI-bearing preservation of the permitted paper, software or data bundle.
- **SSRN record:** discoverable working paper whose PDF and metadata reference the DOI-bearing artifact and canonical project page.
- **Institutional delivery:** private bulk snapshots and incremental API or object-store channels rather than distribution through GitHub.

Official workflow references:

- [GitHub: immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
- [Zenodo: GitHub integration](https://help.zenodo.org/docs/github/)
- [Zenodo: enable a repository](https://help.zenodo.org/docs/github/enable-repository/)
- [Zenodo: archive a GitHub release](https://help.zenodo.org/docs/github/archive-software/github-upload/)
- [Zenodo: reserve a DOI](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)
- [SSRN submission overview](https://blog.ssrn.com/2022/09/02/want-to-submit-to-ssrn/)

## Applying the model to Research Note #1

Research Note #1 should be registered only when its exact sampling frame and artifact metadata are frozen. If it contains more issuers or observations than the open benchmark, that difference is stated as study scope—not backfilled into `data/sample/v1`. Its result remains citable through its own release version and DOI, while this repository supplies the stable contract and reference implementation.
