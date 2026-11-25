"""User-facing commands for one arm, the full research pipeline, and a live local explorer."""

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .records import HORIZONS, METHODS, storage_root


def dashboard(project, port):
    """Serve the same Pages application locally with a live view of atomically recorded events."""
    from .report_records import study_snapshot

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?",1)[0] == "/live.json":
                data = json.dumps(study_snapshot(project),ensure_ascii=False,allow_nan=False).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json; charset=utf-8")
                self.send_header("Cache-Control","no-store")
                self.send_header("Content-Length",str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                super().do_GET()
    server = ThreadingHTTPServer(("127.0.0.1",port),partial(Handler,directory=str(project/"docs")))
    print(f"Live study dashboard http://127.0.0.1:{port}/",flush=True)
    server.serve_forever()


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",type=Path,default=Path.cwd())
    parsers = p.add_subparsers(dest="action",required=True)
    for action in ("prepare","train","study","freeze","evaluate","report","dashboard","publish","progress","verify"):
        sub = parsers.add_parser(action)
        if action in {"prepare","study"}:
            sub.add_argument("--stage",choices=(*HORIZONS,"both"),default="both")
        if action in {"train","freeze"}:
            sub.add_argument("--stage",choices=HORIZONS,required=True)
        if action in {"train","study","evaluate"}:
            sub.add_argument("--device",default="cuda")
        if action=="train":
            sub.add_argument("--method",choices=(*METHODS,"unigram","initial"),required=True)
            sub.add_argument("--phase",choices=("pilot","control","confirm","smoke"),default="pilot")
            sub.add_argument("--seed",type=int,default=0)
            sub.add_argument("--ratio",type=float,default=0.03)
            sub.add_argument("--microbatch",type=int)
        if action in {"train","study","evaluate"}:
            sub.add_argument("--publish",action="store_true",help="Publish results to the configured project accounts")
        if action=="evaluate":
            sub.add_argument("run_id")
        if action=="dashboard":
            sub.add_argument("--port",type=int,default=8765)
        if action=="publish":
            sub.add_argument("--message",default="Update third-derivative study records")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    project = args.project.resolve()
    storage = storage_root(project)
    if args.action=="verify":
        from .verification import verify
        return verify(project)
    if args.action=="dashboard":
        return dashboard(project,args.port)
    if args.action in {"report","progress","publish"}:
        from .progress import progress
        if args.action == "progress":
            print(progress(project))
            return
        from .reporting import build_report
        build_report(project)
        progress(project)
        if args.action == "publish":
            from .release import publish_snapshot
            print(publish_snapshot(project,args.message))
        return
    from .study import evaluate_one,freeze,milestone,prepare_stage,run_study
    if args.action=="freeze":
        print(freeze(project,storage,args.stage)["freeze_id"])
        return
    stages = list(HORIZONS) if getattr(args,"stage",None)=="both" else [getattr(args,"stage",None)]
    if args.action=="prepare":
        for stage in stages:
            prepare_stage(project,storage,stage)
        return
    from .records import setup_device
    device = setup_device(args.device)
    if args.action=="study":
        run_study(project,storage,stages,device,args.publish)
        return
    if args.action=="evaluate":
        summary = evaluate_one(project,storage,args.run_id,device)
    else:
        from .train import run_one
        summary = run_one(project,storage,args.stage,args.method,args.phase,args.seed,args.ratio,device,args.microbatch)
    milestone(project,storage,summary,args.publish)


if __name__=="__main__":
    main()
