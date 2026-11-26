// The same read-only snapshot feeds GitHub Pages and the local training server.
// Browser APIs: https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D
"use strict";
const element = id => document.getElementById(id);
const repository = document.querySelector("a.source").href;
const runDirectory = document.querySelector("a.source").dataset.runs || repository + "/tree/main/results/";
const hubFeed = "https://huggingface.co/BurnyCoder/thirdloss-study/resolve/main/live.json";
let downloadUrl;
const local = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname) ||
  new URL(location.href).searchParams.get("live") === "1";
const metrics = {
  dev_nll: ["Development NLL", "nats / target token"], loss: ["Training NLL", "nats / target token"],
  dev_accuracy: ["Development accuracy", "% correct"], accuracy: ["Training accuracy", "% correct"],
  penalty: ["Weighted active penalty", "weighted loss contribution"],
  raw_third: ["Squared third-derivative norm estimate", "two-window squared Frobenius norm estimate"],
  raw_trace: ["Hessian trace estimate", "signed trace estimate"],
  raw_hessian_norm: ["Squared Hessian norm estimate", "squared Frobenius estimate"],
  width: ["Directional width", "Euclidean weight distance · wider is flatter"], width_probe_nll: ["Width-probe loss", "nats / target token"],
  checkpoint_rms: ["Checkpoint RMS curvature", "RMS curvature · lower means less bending"],
  checkpoint_signed_trace: ["Checkpoint signed trace / parameter", "mean signed curvature · no preferred direction"],
  score_width: ["Common score width", "RMS logit distance · wider tolerates larger score changes"],
  score_curvature: ["Common score curvature", "mean local bending under shared logit biases"],
  curvature_rms: ["Rolling RMS curvature", "RMS Hessian eigenvalue estimate"],
  third_lambda: ["Third-derivative coefficient", "coefficient"], trace_lambda: ["Trace coefficient", "coefficient"],
  gradient_norm: ["Unclipped gradient norm", "Euclidean gradient norm"],
};
const axes = {tokens: "training target tokens", train_seconds: "training seconds", step: "optimizer steps"};
const numeric = value => typeof value === "number" && Number.isFinite(value);
const number = (value, digits = 3) => numeric(value) ? value.toLocaleString("en-US", {
  minimumFractionDigits: digits, maximumFractionDigits: digits,
}) : "—";
const compact = value => numeric(value) ? new Intl.NumberFormat("en-US", {
  notation: "compact", maximumFractionDigits: 2,
}).format(value) : "—";
const isComplete = run => ["complete", "completed", "finished", "evaluated", "success"].includes(run.status);
let study = {runs: [], stages: {}, method_names: {}, colors: {}, stage_names: {}};
let filteredRuns = [];
let sampleEntries = [];
let curves = [];
let points = [];
let inspected = -1;

function node(tag, value) {
  const result = document.createElement(tag);
  if (value !== undefined) result.textContent = value;
  return result;
}

function options(select, choices, previous) {
  const entries = choices.map(([value, name]) => {
    const option = node("option", name);
    option.value = value;
    return option;
  });
  select.replaceChildren(...entries);
  if (choices.some(([key]) => key === previous)) select.value = previous;
}

function methodName(method) { return study.method_names[method] || method || "—"; }
function stageName(stage) { return study.stage_names[stage] || stage; }
function methodColor(method) { return study.colors[method] || "#56665c"; }

function rebuildFilters() {
  const stage = element("stage").value;
  const selected = study.runs.filter(run => run.stage === stage);
  const phases = [...new Set(selected.map(run => run.phase).filter(Boolean))].sort();
  options(element("phase"), [["", "All phases"], ...phases.map(p => [p, p])], element("phase").value);
  const phase = element("phase").value;
  const inPhase = phase ? selected.filter(run => run.phase === phase) : selected;
  options(element("run"), [["", "All runs"], ...inPhase.map(run => [run.id, run.id])], element("run").value);
  const id = element("run").value;
  filteredRuns = id ? inPhase.filter(run => run.id === id) : inPhase;
}

function showTotals() {
  element("runs-count").textContent = number(study.runs.filter(isComplete).length, 0);
  for (const [field, target] of [["tokens", "tokens-count"], ["train_seconds", "hours-count"]]) {
    const values = study.runs.filter(run => numeric(run[field])).map(run =>
      Math.max(0,run[field] - (run["inherited_" + field] || 0)));
    const total = values.reduce((a, b) => a + b, 0);
    element(target).textContent = values.length ? (field === "tokens" ? compact(total) : number(total / 3600, 2) + " h") : "—";
    if (values.length) element(target).title = number(total, 0) + (field === "tokens" ? " training tokens" : " seconds");
  }
}

function showLedger() {
  const body = element("ledger");
  body.replaceChildren();
  for (const run of filteredRuns) {
    const tr = node("tr");
    const first = node("td");
    const link = node("a", run.id);
    link.href = runDirectory + encodeURIComponent(run.id);
    first.append(link);
    tr.append(first);
    const evaluation = run.evaluation_progress;
    const status = evaluation?.targets_to_score > 0
      ? `${evaluation.split === "test" ? "scoring test" : run.status} (${number(100 * evaluation.targets_scored / evaluation.targets_to_score, 1)}%)`
      : run.status;
    for (const value of [methodName(run.method), run.seed ?? "—", number(run.ratio, 3),
      number(run.tokens, 0), number(isComplete(run) ? run.dev_nll : null, 4), number(run.test_nll, 4),
      number(run.tokens_per_sec, 0), number(run.peak_vram_mb, 0), status]) {
      tr.append(node("td", value));
    }
    body.append(tr);
  }
  element("ledger-count").textContent = "(" + filteredRuns.length + ")";
  if (!filteredRuns.length) {
    const cell = node("td", "Awaiting a run in this selection.");
    cell.colSpan = 10;
    const row = node("tr");
    row.append(cell);
    body.append(row);
  }
}

function collectCurves() {
  const metric = element("metric").value;
  const axis = element("axis").value;
  const percent = metric.endsWith("accuracy") ? 100 : 1;
  curves = filteredRuns.map(run => {
    const values = (run.events || []).filter(e => numeric(e[metric]) && numeric(e[axis]))
      .map(e => ({x: e[axis], y: e[metric] * percent, run}));
    return {run, values};
  }).filter(series => series.values.length);
  const legend = element("legend");
  legend.replaceChildren();
  for (const method of [...new Set(curves.map(s => s.run.method))]) {
    const item = node("span");
    const stroke = node("i");
    stroke.style.backgroundColor = methodColor(method);
    item.append(stroke, document.createTextNode(methodName(method)));
    legend.append(item);
  }
  inspected = -1;
  element("point").textContent = "";
  draw();
}

function draw() {
  const canvas = element("chart");
  const bounds = canvas.getBoundingClientRect();
  const w = Math.max(100, bounds.width);
  const h = Math.max(100, bounds.height);
  const scale = Math.min(window.devicePixelRatio || 1, 3);
  canvas.width = Math.round(w * scale);
  canvas.height = Math.round(h * scale);
  const ctx = canvas.getContext("2d");
  ctx.scale(scale, scale);
  const frame = {left: w < 480 ? 49 : 62, right: w - 13, top: 28, bottom: h - 49};
  const all = curves.flatMap(s => s.values);
  points = [];
  element("chart-empty").hidden = all.length > 0;
  element("chart-empty").textContent = "The selected measurement will appear after its first logged observation.";
  if (!all.length) return;
  const metric = element("metric").value;
  const axis = element("axis").value;
  let low = Infinity, high = -Infinity, maxX = 0;
  for (const point of all) {
    low = Math.min(low, point.y);
    high = Math.max(high, point.y);
    maxX = Math.max(maxX, point.x);
  }
  if (metric.endsWith("accuracy")) {
    low = 0; high = 100;
  } else {
    const pad = (high - low || Math.abs(high) * .1 || .01) * .09;
    low -= pad; high += pad;
    if (["dev_nll", "loss", "raw_third", "raw_hessian_norm"].includes(metric)) low = Math.max(0, low);
  }
  maxX = maxX || 1;
  const positionX = value => frame.left + (frame.right - frame.left) * value / maxX;
  const positionY = value => frame.bottom - (frame.bottom - frame.top) * (value - low) / (high - low);
  const tick = value => Math.abs(value) >= 10000 || (value !== 0 && Math.abs(value) < .001) ?
    value.toExponential(1) : Number(value.toPrecision(4)).toLocaleString("en-US");
  ctx.font = "11px system-ui, sans-serif";
  ctx.lineWidth = 1;
  ctx.fillStyle = "#52635c";
  ctx.textAlign = "left";
  ctx.fillText(metrics[metric][1], frame.left, 13);
  for (let i = 0; i <= 4; i++) {
    const yValue = low + (high - low) * i / 4;
    const y = positionY(yValue);
    ctx.strokeStyle = "#dce6de";
    ctx.beginPath(); ctx.moveTo(frame.left, y); ctx.lineTo(frame.right, y); ctx.stroke();
    ctx.textAlign = "right";
    ctx.fillText(tick(yValue), frame.left - 7, y + 3);
    const xValue = maxX * i / 4;
    ctx.textAlign = i === 4 ? "right" : i === 0 ? "left" : "center";
    ctx.fillText(compact(xValue), positionX(xValue), frame.bottom + 18);
  }
  ctx.textAlign = "center";
  ctx.fillText(axes[axis], (frame.left + frame.right) / 2, h - 6);
  for (const series of curves) {
    const color = methodColor(series.run.method);
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 1.65;
    ctx.globalAlpha = curves.length > 10 ? .58 : .92;
    ctx.beginPath();
    series.values.forEach((value, i) => {
      const px = positionX(value.x), py = positionY(value.y);
      points.push({...value, px, py});
      if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py);
    });
    ctx.stroke();
    if (series.values.length <= 60) {
      for (const value of series.values) {
        ctx.beginPath(); ctx.arc(positionX(value.x), positionY(value.y), 2.4, 0, Math.PI * 2); ctx.fill();
      }
    }
  }
  ctx.globalAlpha = 1;
  if (inspected >= 0 && points[inspected]) {
    const p = points[inspected];
    ctx.fillStyle = "white"; ctx.strokeStyle = methodColor(p.run.method); ctx.lineWidth = 2.3;
    ctx.beginPath(); ctx.arc(p.px, p.py, 4.7, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    element("point").textContent = p.run.id + " · " + number(p.x, axis === "train_seconds" ? 1 : 0) +
      " " + axes[axis] + " · " + (p.y !== 0 && Math.abs(p.y)<.0001 ? p.y.toExponential(4) : number(p.y, 4)) + " " + metrics[metric][1];
  }
}

function table(headers, rows) {
  const wrapper = node("div");
  wrapper.className = "table-wrap";
  const result = node("table");
  const head = node("thead"), top = node("tr"), body = node("tbody");
  headers.forEach(title => top.append(node("th", title)));
  head.append(top); result.append(head);
  for (const values of rows) {
    const row = node("tr");
    values.forEach(value => row.append(node("td", value)));
    body.append(row);
  }
  result.append(body); wrapper.append(result);
  return wrapper;
}

function showSchedule() {
  const plan = study.run_inventory;
  if (!plan) return;
  const byId = new Map(study.runs.map(run => [run.id, run]));
  const frozen = new Set(study.frozen_stages || []);
  for (const run of study.runs) if (run.freeze_id) frozen.add(run.stage);
  const jobs = plan.fits.map(item => {
    const r = byId.get(item.id);
    if (!r) return {...item, active: false};
    const progress = r.evaluation_progress;
    const fitting = !isComplete(r) && !["planned","queued","failed","paused"].includes(r.status);
    const testing = progress?.split === "test" && !numeric(r.test_nll);
    const fit = isComplete(r) ? "Complete" : progress?.split === "dev" ? "Scoring development" : r.status;
    const test = item.phase !== "confirm" ? "—" : numeric(r.test_nll) && frozen.has(item.stage) ? "Complete"
      : testing ? "Scoring test" : frozen.has(item.stage) ? "Queued" : "Awaiting freeze";
    const geometry = r.score_flatness && (r.flatness || item.method === "unigram") ? "Complete"
      : r.score_flatness || r.flatness ? "Partial" : "Pending";
    let activity = "";
    if (fitting || testing) {
      const count = progress ? number(progress.targets_scored, 0) + "/" + number(progress.targets_to_score, 0) + " scored"
        : number(r.tokens || 0, 0) + "/" + number(item.targets, 0) + " training targets";
      activity = item.title + " · " + (testing ? test : fit) + " · " + count;
    }
    return {...item, fit, test, geometry, active: fitting || testing, activity};
  });
  const groups = plan.groups.map(g => {
    const done = g.members.filter(i => jobs[i][g.field] === "Complete").length;
    return [g.label, done, g.total - done, g.total];
  });
  const completed = groups.reduce((sum, group) => sum + group[1], 0);
  element("milestone-count").textContent = completed + "/" + plan.total + " experimental milestones";
  element("milestone-table").replaceChildren(table(["Experiment", "Completed", "Remaining", "Planned"], groups));
  const active = jobs.filter(j => j.active);
  const paused = jobs.some(j => j.fit.toLowerCase() === "paused");
  element("current-activity").textContent = active.length ? "Recorded activity · " + active.map(j => j.activity).join(" / ")
    : paused ? "Experiments paused by request. The remaining runs have no scheduled start date." : "Between recorded training and scoring updates.";
  const next = plan.order.find(([i, action]) => jobs[i][action] !== "Complete" && !jobs[i].active);
  const pending = next ? jobs[next[0]].title + (next[1] === "test" ? " · frozen test" : "") : plan.next;
  element("next-job").textContent = (paused ? "First run on resumption · " : "Next scheduled work · ") + pending + ". Seed sensitivity is the final stage.";
  const choice = element("queue-filter").value;
  const visible = jobs.filter(j => choice === "all" || (choice === "active" && j.active)
    || (choice === "complete" && j.fit === "Complete")
    || (choice === "pending" && (j.fit !== "Complete" || j.geometry !== "Complete" || !["—","Complete"].includes(j.test))));
  const rows = visible.map(j => [stageName(j.stage), j.phase, j.seed, methodName(j.method), number(j.targets, 0), j.fit, j.test, j.geometry]);
  element("scheduled-table").replaceChildren(rows.length ?
    table(["Model","Phase","Seed","Arm","Training targets","Training and development","Frozen test","Flatness"], rows)
    : node("p", "No runs match this filter at the recorded time."));
  const geometry = (study.headline_flatness || []).map(row => row.map(cell => String(cell).replaceAll("<br>", " · ")));
  element("geometry-headlines").replaceChildren(geometry.length ?
    table(["Model and paired cohort","Flatness statistic","AdamW","Hessian trace","Third order"], geometry)
    : node("p", "Awaiting comparable checkpoint measurements."));
}

function showEvidence() {
  const stage = element("stage").value;
  const outcome = study.stages[stage] || {};
  element("evidence-stage").textContent = stageName(stage);
  const verdicts = {
    confirmed: "The third-order objective beat both baselines under the registered rule.",
    inconclusive: "The completed stage did not establish superiority over both baselines.",
    adverse: "A median paired interval favors at least one baseline.",
    invalid: "The registered analysis flagged incompatible run records.",
  };
  element("verdict").textContent = verdicts[outcome.status] ||
    "Awaiting paired test results. Full-horizon training triplets: " +
    (outcome.n_complete_seeds || 0) + " of " + (outcome.n_expected_seeds || 8) + ".";
  const target = element("stats");
  target.replaceChildren();
  const audit = study.scientific_audit || {};
  if (audit[stage]) target.append(node("p", audit[stage]));
  const fixed = study.hybrid?.attainability?.late;
  if (stage === "stories" && fixed?.best_raw_p > .05) {
    target.append(node("p", "Adaptive had a narrower measured width gain than the fixed ramp in " +
      fixed.narrower + " resolved pairs. Even if every remaining pair favors adaptive, the raw p-value is at least " +
      number(fixed.best_raw_p, 8) + ". The registered joint width criterion is unreachable. The replay pairs share donor randomness."));
  }
  const pilots = (study.pilot_comparisons || {})[stage] || [];
  if (pilots.length) {
    const heading = node("details");
    heading.append(node("summary", "Single-seed development comparisons"));
    heading.append(table(["Comparator", "Training tokens", "Third-order dev NLL", "Comparator dev NLL", "ΔNLL", "Strengths"],
      pilots.map(p => [methodName(p.method), number(p.tokens, 0), number(p.third_nll, 5),
        number(p.baseline_nll, 5), number(p.delta, 5), p.strength_basis])));
    target.append(heading);
  }
  const entries = Object.entries(outcome.comparisons || {});
  if (entries.length) {
    target.append(table(["Comparator", "Wins / ties / losses", "Median ΔNLL", "Marginal median interval", "Coverage", "Holm p"],
      entries.map(([baseline, s]) => [methodName(baseline), [s.wins, s.ties, s.losses].join(" / "),
        number(s.median_delta, 5), (s.median_ci || []).map(x => number(x, 5)).join(" to "),
        number(s.ci_coverage * 100, 2) + "%", number(s.p_holm, 5)])));
    const details = node("details");
    details.append(node("summary", "Individual paired differences"));
    details.append(table(["Comparator", "Seed", "Third-order NLL", "Comparator NLL", "ΔNLL"],
      entries.flatMap(([baseline, s]) => s.pairs.map(p => [methodName(baseline), p.seed,
        number(p.third_nll, 5), number(p.baseline_nll, 5), number(p.delta, 5)]))));
    target.append(details);
  }
  if ((outcome.matched_time || []).length) {
    const details = node("details");
    details.append(node("summary", "Development loss at matched training time"));
    details.append(table(["Seed", "Cutoff (s)", "Method", "Checkpoint (s)", "Training tokens", "Dev NLL"],
      outcome.matched_time.flatMap(t => Object.entries(t.by_method || {}).filter(([, m]) => m)
        .map(([name, m]) => [t.seed, number(t.cutoff_seconds, 1), methodName(name),
          number(m.train_seconds, 1), number(m.tokens, 0), number(m.dev_nll, 5)]))));
    target.append(details);
  }
  if ((outcome.matched_nonhost_time || []).length) {
    const details = node("details");
    details.append(node("summary", "Development loss after subtracting host derivative calls"));
    details.append(table(["Seed", "Cutoff (s)", "Method", "Checkpoint (s)", "Training tokens", "Dev NLL"],
      outcome.matched_nonhost_time.flatMap(t => Object.entries(t.by_method).map(([name, m]) =>
        [t.seed, number(t.cutoff_seconds, 1), methodName(name), number(m.clock_seconds, 1),
          number(m.tokens, 0), number(m.dev_nll, 5)]))));
    target.append(details);
  }
}

function showSample() {
  const entry = sampleEntries.find(s => s.id === element("sample").value);
  element("sample-view").hidden = !entry;
  if (!entry) return;
  const s = entry.sample;
  element("prompt-text").textContent = s.prompt ?? "";
  element("reference-text").textContent = s.reference ?? "No reference continuation was recorded for this prompt.";
  element("generated-text").textContent = s.continuation ?? "";
  element("raw-sample").href = runDirectory.replace("/tree/main/", "/blob/main/") + encodeURIComponent(entry.run.id) + "/samples.jsonl";
}

function showOutputs() {
  sampleEntries = filteredRuns.flatMap(run => (run.samples || []).map((sample, index) => ({
    id: run.id + "/" + index, name: run.id + " · sample " + (index + 1), sample, run,
  })));
  const menu = element("sample");
  options(menu, sampleEntries.map(s => [s.id, s.name]), menu.value);
  element("sample-controls").hidden = !sampleEntries.length;
  element("samples-empty").hidden = sampleEntries.length > 0;
  element("samples-empty").textContent = "Awaiting an archived continuation in the selected runs.";
  showSample();
}

function render() {
  rebuildFilters(); showTotals(); showSchedule(); showLedger(); collectCurves(); showEvidence(); showOutputs();
}

async function getData(url) {
  const response = await fetch(url, {cache: "no-store"});
  if (!response.ok) throw new Error("HTTP " + response.status);
  const result = await response.json();
  if (!Array.isArray(result.runs) || !result.stages) throw new Error("Unrecognized study record");
  return result;
}

async function refresh() {
  let live = false;
  const status = element("feed-status");
  try {
    if (local) {
      const release = await getData("study.json");
      try { study = {...release, ...await getData("/live.json")}; live = true; }
      catch { study = release; }
    } else {
      study = await getData("study.json");
      try {
        const update = await getData(hubFeed + "?minute=" + Math.floor(Date.now() / 60000));
        if (Date.parse(update.generated_at) > Date.parse(study.generated_at)) {
          const byId = new Map(study.runs.map(run => [run.id, run]));
          for (const run of update.runs) byId.set(run.id, run);
          study = {...study, ...update, runs: [...byId.values()].sort((a,b) => a.id.localeCompare(b.id))};
          live = update.active && Date.now() - Date.parse(update.generated_at) < 300000;
        }
      } catch { /* The full published study stays available between live updates. */ }
    }
    render();
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    downloadUrl = URL.createObjectURL(new Blob([JSON.stringify(study)], {type:"application/json"}));
    element("download-records").href = downloadUrl;
    const stamp = new Date(study.generated_at);
    const asOf = Number.isNaN(stamp.valueOf()) ? "time unavailable" :
      stamp.toLocaleString(undefined, {dateStyle: "medium", timeStyle: "medium"});
    status.textContent = (live ? (local ? "Live local metrics" : "Live training metrics") : "Published results") + " · Updated " + asOf;
    status.classList.toggle("live", live);
  } catch (error) {
    status.classList.remove("live");
    status.textContent = "Ledger temporarily unavailable. " + error.message + ". Retrying automatically.";
    if (!study.runs.length) render();
  } finally { window.setTimeout(refresh, local ? 10000 : 60000); }
}

for (const id of ["stage", "phase", "run"]) element(id).addEventListener("change", render);
element("queue-filter").addEventListener("change", showSchedule);
for (const id of ["axis", "metric"]) element(id).addEventListener("change", collectCurves);
element("sample").addEventListener("change", showSample);
const canvas = element("chart");
new ResizeObserver(draw).observe(element("chart").parentElement);
canvas.addEventListener("pointermove", e => {
  const box = canvas.getBoundingClientRect();
  const x = e.clientX - box.left, y = e.clientY - box.top;
  let nearest = -1, distance = 25 * 25;
  points.forEach((point, i) => {
    const d = (point.px - x) ** 2 + (point.py - y) ** 2;
    if (d < distance) { nearest = i; distance = d; }
  });
  if (nearest !== inspected) {
    inspected = nearest;
    if (nearest < 0) element("point").textContent = "";
    draw();
  }
});
canvas.addEventListener("keydown", e => {
  if (points.length && ["ArrowRight", "ArrowLeft"].includes(e.key)) {
    e.preventDefault();
    inspected = (Math.max(0, inspected + (e.key === "ArrowRight" ? 1 : -1))) % points.length;
    draw();
  }
});
refresh();
