"""把 autocv 五階段包成 Stage，捕捉 stdout 成 log 事件，train/optimize 提供預估。"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

from autocv.config import Config
from autocv.server.events import Event
from autocv.server.runner import Stage


def _logged(fn, emit) -> object:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn()
    for line in buf.getvalue().splitlines():
        if line.strip():
            emit(Event("log", payload={"line": line}))
    return result


def build_stages(cfg: Config, root: Path, optimize: bool) -> list[Stage]:
    from autocv.data import download
    from autocv.infer import infer
    from autocv.split import split

    def data_run(emit):
        _logged(lambda: download(cfg, root), emit)

    def split_run(emit):
        _logged(lambda: split(cfg, root), emit)

    def train_run(emit):
        from autocv.train import train

        _logged(lambda: train(cfg, root, yes=True), emit)

    def opt_run(emit):
        from autocv.optimize import optimize as do_opt

        _logged(lambda: do_opt(cfg, root, yes=True), emit)

    def infer_run(emit):
        out_dir = _logged(lambda: infer(cfg, root), emit)
        if out_dir:
            pngs = sorted(Path(out_dir).glob("pred_*.png"))
            emit(
                Event(
                    "result",
                    "infer",
                    {"images": [f"/artifacts/{p.name}" for p in pngs]},
                )
            )

    def train_estimate() -> float:
        from autocv.train import _count_train_imgs, _estimate_minutes

        n = _count_train_imgs(root / cfg.paths.processed)
        return round(_estimate_minutes(n, cfg.train.epochs, cfg.train.batch), 1)

    mid = (
        Stage("optimize", opt_run, estimate=lambda: float(cfg.optimize.iterations))
        if optimize
        else Stage("train", train_run, estimate=train_estimate)
    )
    return [
        Stage("data", data_run),
        Stage("split", split_run),
        mid,
        Stage("infer", infer_run),
    ]
