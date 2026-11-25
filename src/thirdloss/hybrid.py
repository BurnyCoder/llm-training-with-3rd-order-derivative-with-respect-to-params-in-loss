"""Registered TinyStories trace/T3 schedules, common optimizer trunks and train-only probes."""

import bisect
import math
import statistics
import time

from .models import build_model, logits_of, token_loss, trainable_digest
from .objectives import probe_gradient, vector_norm
from .penalties import hessian_vector, inner, random_signs
from .records import BATCHES, CONTEXT, HORIZONS, read_json, run_name, sha256, write_json
from .width import measure_width
from .windows import TrainingWindows, generator, probe_rows


SEEDS = range(21,29)
SWITCH, RAMP_END, END = 2048, 3072, 4096
STREAMS = {"trace":827,"third":919}


def donor_seed(seed):
    """Permute adaptive schedules cyclically across all eight independent receivers."""
    return 21 + (seed - 22) % len(SEEDS)


class HybridSchedule:
    """Determine each detached coefficient from the already completed observations."""

    def __init__(self, arm, alpha, cap, delta=0., replay=()):
        self.arm, self.alpha, self.cap, self.delta = arm,alpha,cap,delta
        self.replay = list(replay)
        self.replay_steps = [row[0] for row in self.replay]
        self.q, self.nll, self.changes = [],[],[]
        self.reference, self.eligible, self.weight, self.at_zero = None,False,0.,0

    def state(self):
        """Store Python scalars/lists so the ordinary weights-only checkpoint can contain them."""
        return {key:getattr(self,key) for key in ("q","nll","changes","reference","eligible","weight","at_zero")}

    def load(self, state):
        for key in self.state():
            setattr(self,key,state[key])

    def observe(self, q, loss):
        if not (math.isfinite(q) and q>=0 and math.isfinite(loss)):
            raise FloatingPointError("Nonfinite hybrid curvature or training loss")
        self.q = (self.q+[q])[-8:]
        self.nll = (self.nll+[loss])[-8:]

    def rms(self):
        return math.sqrt(statistics.mean(self.q)) if self.q else None

    def fix_reference(self):
        if len(self.q)!=8 or not self.rms():
            raise ValueError("The branch reference requires eight measurements and positive RMS curvature")
        self.reference = self.rms()

    def coefficients(self, step):
        """Step is the number of completed updates. No current/future loss enters its rule."""
        ramp = min(1.,max(0.,(step-SWITCH)/(RAMP_END-SWITCH)))
        trace = self.alpha
        weight = 0.
        if self.arm=="always":
            weight = self.cap
        elif self.arm=="late":
            weight = self.cap*ramp
        elif self.arm=="strong":
            trace += self.delta*ramp
        elif self.arm=="adaptive" and step>=SWITCH:
            if self.reference is None:
                raise ValueError("Adaptive suffix is missing its pre-branch curvature reference")
            self.eligible |= len(self.q)==8 and statistics.mean(self.nll)<=4.
            if self.eligible:
                weight = max(self.weight,self.cap*max(0.,1.-self.rms()/self.reference))
        elif self.arm=="replay":
            ix = bisect.bisect_right(self.replay_steps,step)-1
            weight = self.replay[ix][1] if ix>=0 else 0.
        if weight!=self.weight or not self.changes:
            self.changes.append([step,weight])
        self.weight = weight
        self.at_zero += int(weight==0.)
        return {"trace":trace,"third":weight}


class HybridProtocol:
    """Couple a schedule to its checkpoints, independently addressed curvature and width probes."""

    def __init__(self, project, storage, config, replay):
        self.output = project/"results"/config["id"]
        self.train_file = storage/"data"/"stories"/"train.bin"
        self.schedule = HybridSchedule(config["method"],config["alpha"],config["cap"],config.get("delta",0.),replay)
        self.parent = storage/"checkpoints"/config["parent"]/"latest.pt" if "parent" in config else None
        self.parent_output = project/"results"/config["parent"] if self.parent else None
        self.seed = config["seed"]

    def monitor(self, model, parameters, inputs, targets, step, training_loss):
        """Estimate ||H||²_F/d on the same pair of windows with a separate random direction."""
        if (step+1)%16:
            return {}
        rows = probe_rows(self.seed,step,len(inputs))
        loss = token_loss(logits_of(model,inputs[rows]),targets[rows])
        signs = random_signs(parameters,generator(inputs.device,self.seed,step,937))
        hz = hessian_vector(loss,parameters,signs,create_graph=False)
        q = float(inner(hz,hz))/sum(p.numel() for p in parameters)
        self.schedule.observe(q,float(training_loss))
        if step+1==SWITCH:
            self.schedule.fix_reference()
        return {"curvature_q":q,"curvature_rms":self.schedule.rms(),
                "monitor_mean_nll":statistics.mean(self.schedule.nll),"reference_rms":self.schedule.reference}

    def checkpoint_width(self, model, step):
        """Write every ray and detect stale results when resuming around a width checkpoint."""
        if step not in (SWITCH,RAMP_END,END):
            return
        path = self.output/f"width-{step}.json"
        origin = self.parent_output/f"width-{step}.json" if self.parent and step==SWITCH else path
        if origin.exists():
            record = read_json(origin)
            if record["weights_sha256"]!=trainable_digest(model):
                raise ValueError("Stored width was taken on different weights")
            if origin!=path:
                write_json(path,record)
            return
        if origin!=path:
            raise FileNotFoundError("The parent trunk must complete its width measurement")
        device = next(model.parameters()).device
        inputs,targets = TrainingWindows(self.train_file,88731,8).get(0,device)
        stats = measure_width(model,lambda: token_loss(logits_of(model,inputs),targets))
        write_json(path,{"step":step,"tokens":step*CONTEXT*BATCHES["stories"],**stats})
        print(f"Width after {step} updates: {stats['width']}, {stats['censored_rays']} censored rays",flush=True)

    def finish(self, steps):
        schedule = self.schedule
        write_json(self.output/"schedule.json",{"changes":schedule.changes,"zero_steps":schedule.at_zero,
                   "steps":steps,"reference_rms":schedule.reference,"eligible":schedule.eligible,
                   "final_third_lambda":schedule.weight,"steps_at_cap":
                   sum((following[0]-current[0]) for current,following in
                       zip(schedule.changes,schedule.changes[1:]+[[steps,None]]) if current[1]==schedule.cap)})


def match_stronger_trace(project,storage,trunk,cap,device):
    """Match the median per-draw unscaled gradient magnitude at the common checkpoint."""
    from safetensors.torch import load_file
    from .study import weights_file
    seed = trunk["seed"]
    path = project/"results"/"hybrid"/"calibration"/f"seed-{seed}.json"
    if path.exists():
        existing = read_json(path)
        if existing["parent_weights_sha256"]!=trunk["weights_sha256"] or existing["cap"]!=cap:
            raise ValueError("Stronger-trace calibration used different weights or cap")
        return existing["delta"]
    started = time.perf_counter()
    model = build_model("stories",seed,device,storage)
    model.load_state_dict(load_file(str(weights_file(storage,trunk))),strict=True)
    params = tuple(model.parameters())
    windows = TrainingWindows(storage/"data"/"stories"/"train.bin",188701+seed,BATCHES["stories"])
    draws = []
    for step in range(16):
        x,y = windows.get(step,device)
        norms = {}
        for kind in ("trace","third"):
            _,gradient = probe_gradient(model,params,x,y,kind,188701+seed,step,stream=STREAMS[kind])
            norms[kind] = float(vector_norm(gradient))
            del gradient
        if any(not (0<n<float("inf")) for n in norms.values()):
            raise FloatingPointError("Nonpositive or nonfinite branch calibration norm")
        draws.append({"draw":step,**norms,"ratio":norms["third"]/norms["trace"]})
    delta = cap*statistics.median(r["ratio"] for r in draws)
    write_json(path,{"parent_weights_sha256":trunk["weights_sha256"],"seed":seed,"cap":cap,
                     "draws":draws,"delta":delta,"calibration_seconds":time.perf_counter()-started})
    return delta


def run_hybrids(project,storage,device,publish):
    """Run each trunk once; delay seed 21 replay until seed 28 has published its schedule."""
    from .study import milestone, parent_restart_file
    from .train import run_config
    selected = read_json(project/"results"/"selection"/"stories.json")["ratios"]
    if any(selected[k]!=.01 for k in STREAMS):
        raise ValueError("Hybrid protocol requires the registered TinyStories 1% selection")
    weights = {k:selected[k]*read_json(project/"results"/"calibration"/f"stories-{k}.json")["unit_lambda"]
               for k in STREAMS}
    def run(seed,arm):
        phase = "branch" if arm=="trunk" else "hybrid"
        name = lambda s,m,p: run_name("stories",m,p,s,.01)
        config = {"stage":"stories","phase":phase,"id":name(seed,arm,phase),"method":arm,"seed":seed,
                  "ratio":.01,"token_budget":HORIZONS["stories"]//2 if arm=="trunk" else HORIZONS["stories"],
                  "batch_windows":BATCHES["stories"],"context":CONTEXT,"schedule_steps":END,
                  "protocol":"hybrid-v1","alpha":weights["trace"],"cap":weights["third"]}
        replay = []
        if arm not in {"trunk","always"}:
            parent = name(seed,"trunk","branch")
            trunk = read_json(project/"results"/parent/"summary.json")
            if trunk["steps"]!=SWITCH or trunk["seed"]!=seed:
                raise ValueError("Incomplete or unmatched branching checkpoint")
            config.update(parent=parent,parent_weights_sha256=trunk["weights_sha256"],
                          inherited_tokens=trunk["tokens"],inherited_train_seconds=trunk["train_seconds"],
                          parent_restart_sha256=sha256(parent_restart_file(storage,trunk)))
            if arm=="strong":
                config["delta"] = match_stronger_trace(project,storage,trunk,config["cap"],device)
            if arm=="replay":
                donor = name(donor_seed(seed),"adaptive","hybrid")
                path = project/"results"/donor/"schedule.json"
                if read_json(project/"results"/donor/"summary.json")["steps"]!=END:
                    raise ValueError("The entire donor schedule must be available before replay")
                config.update(donor=donor,donor_schedule_sha256=sha256(path))
                replay = read_json(path)["changes"]
        row = run_config(project,storage,config,device,protocol=HybridProtocol(project,storage,config,replay))
        milestone(project,storage,row,publish)
    for seed in SEEDS:
        for arm in ("trunk","adaptive","late","trace","strong","always"):
            run(seed,arm)
        if seed!=SEEDS.start:
            run(seed,"replay")
    run(SEEDS.start,"replay")
