"""Format the dated independent audit from its machine-readable calculations."""


def audit_readout(record):
    """Keep archived observations visibly scoped to the audited revision on later releases."""
    if not record:
        return {}
    passages = record.get("passages")
    readout = {"revision": record["evidence_revision"]}
    if passages:
        pool = passages["pool"]
        counts = [r["documents"] for r in passages["by_seed"].values()]
        total = record["corpora"]["stories"]["splits"]["test"]["documents"]
        readout["stories"] = (
            f"The post-hoc copy check found exact passages of at least {passages['minimum']} tokens in "
            f"{pool['documents']:,} of {total:,} test stories. At the registered training horizon, "
            f"the sampled windows contained such passages from {min(counts)}–{max(counts)} test stories "
            "per seed. The archived test losses cover the whole split. Their sensitivity to removing "
            "these stories is unknown.")
    bench = record["scoring_benchmark"]
    readout["abstracts"] = (
        f"On {bench['targets']:,} training targets the batch-size benchmark recorded "
        f"{bench['reference_correct']:,} correct at batch {bench['reference_batch']} and "
        f"{bench['selected_correct']:,} at batch {bench['selected_batch']}. The aggregate counts "
        "leave token-by-token prediction agreement undetermined.")
    return readout


def findings(record):
    """Report exact tests, corpus exposure and verification coverage with their actual units."""
    scope = audit_readout(record)
    evidence = record["evidence_revision"]
    lines = [f"Audited run and measurement records through Git `{evidence}`. "
             "[Machine-readable calculations, checkpoint and split fingerprints](../../results/analysis/scientific-audit.json)",
             "### Frozen predictive endpoints",
             "| Corpus and comparator | Seed wins / ties / losses | Median ΔNLL | Marginal median interval | Coverage | Raw p | Holm p |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for stage, result in record["primary"].items():
        for comparator, s in result["comparisons"].items():
            lo, hi = s["median_ci"]
            lines.append(f"| {stage} · {comparator} | {s['wins']} / {s['ties']} / {s['losses']} | "
                         f"{s['median_delta']:+.9f} | [{lo:+.9f}, {hi:+.9f}] | {100*s['coverage']:.5f}% | "
                         f"{s['p_raw']:.8f} | {s['p_holm']:.8f} |")
    for stage, result in record["primary"].items():
        checkpoints = len(result["completed_triplets"])
        lines += ["", f"**{stage.capitalize()}** has {checkpoints} completed full-budget training triplets "
                  f"and {result['scores']} final test scores in this snapshot."]
        if result.get("freeze_commit"):
            lines[-1] += (f" The freeze commit contained their final weights' digests and unscored summaries. "
                          f"The paired arms used {result['unique_initializations']} distinct initializations across seeds. "
                          f"The released stream supplies {result['test_targets']:,} next-token targets. "
                          f"[Committed freeze](../../results/freeze/{stage}.json)")
    if "stories" in scope:
        p = record["passages"]
        lines += ["", "### Passage overlap and actual training exposure", "", scope["stories"], "",
                  f"Across the prepared training pool, {p['maximal_pairs']} maximal matching span pairs cover "
                  f"{p['pool']['positions']:,} distinct positions in the test stream, with "
                  f"{p['distinct_test_starts']} distinct starts of matching {p['minimum']}-token windows. The longest spans "
                  f"{p['longest']} tokens. Positions count token IDs on either side of the within-window "
                  "next-token shift. Repeated matches contribute once to the union.", "",
                  "| Seed | Distinct test token positions in qualifying training windows | Affected test stories |",
                  "|---:|---:|---:|"]
        lines += [f"| {seed} | {v['positions']:,} | {v['documents']} |" for seed,v in p["by_seed"].items()]
    from .hybrid_results import hybrid_bound_text
    hybrid = record["hybrid"]
    lines += ["", "### Width, numerical checks and coverage", "", hybrid_bound_text(hybrid), "",
              "An interval below zero establishes a narrower measured width gain over the comparator. "
              "An interval crossing zero leaves the sign unresolved at the stored search precision.", "",
              "| Seed | Shared-trunk comparator | Midpoint Δwidth gain | Bounds from ray search | Sign |",
              "|---:|---|---:|---:|---|"]
    for row in hybrid["pairs"]:
        if row["comparator"] in {"late","replay"}:
            def bound(key):
                return "open" if row[key] is None else f"{row[key]:+.9f}"
            lines.append(f"| {row['seed']} | {row['comparator']} | {bound('delta')} | "
                         f"[{bound('delta_lower')}, {bound('delta_upper')}] | {row['sign']} |")
    precision = record["precision"]
    counts = record["secondary"]["counts"]
    for pause in record["pauses"]:
        lines += ["",f"The incomplete run `{pause['run']}` has a saved restart at update {pause['checkpoint_step']} "
                  f"({pause['checkpoint_targets']:,} targets). The last logged update was {pause['last_logged_step']}. "
                  f"[Archived restart receipt]({pause['hub_checkpoint']['url']})"]
    lines += ["", scope["abstracts"] + f" The selected-minus-reference NLL difference was "
              f"{record['scoring_benchmark']['delta_nll']:+.9g} nats per target.", "",
              f"Recomputing the difference from the two archived FP64 derivative arrays gives relative L2 "
              f"error {precision['relative_gradient_difference']:.7g} and cosine {precision['cosine']:.12f} "
              "on the numerical reference case.", "",
              f"Reconciled {len(record['secondary']['runs'])} completed summaries, {counts.get('checkpoint_files',0)} "
              f"fitted weight files, {counts.get('full_dev_logs',0)} terminal full-development log entries and "
              f"{counts.get('full_test_coverage_logs',0)} test coverage logs. Also reconstructed "
              f"{counts.get('hybrid_width_files',0)} follow-up width files, {counts.get('flatness.json',0)} "
              f"checkpoint weight-space records and {counts.get('score-flatness.json',0)} score-space records "
              f"from their directional data. [Run-level evidence](../../results/analysis/scientific-audit.json)"]
    return "\n".join(lines)
