from autocv.server.events import Event


def test_event_to_dict_round_trips():
    e = Event(kind="stage", stage="train", payload={"status": "running"})
    assert e.to_dict() == {
        "kind": "stage",
        "stage": "train",
        "payload": {"status": "running"},
    }


def test_event_kinds_constant():
    from autocv.server.events import KINDS

    assert {"stage", "log", "metric", "await_confirm", "result", "done"} <= set(KINDS)


import time

from autocv.server.runner import GATED, PipelineRunner, Stage


def _wait(r, timeout=2.0):
    deadline = time.time() + timeout
    while r.status not in ("done", "error") and time.time() < deadline:
        time.sleep(0.05)


def test_runner_runs_stages_in_order_and_emits_done():
    calls = []
    r = PipelineRunner(
        [
            Stage("data", lambda emit: calls.append("data")),
            Stage("split", lambda emit: calls.append("split")),
        ]
    )
    r.start()
    _wait(r)
    drained = list(r.events.queue)
    assert calls == ["data", "split"]
    triples = [(e.kind, e.stage, e.payload.get("status")) for e in drained]
    assert ("stage", "data", "running") in triples
    assert ("stage", "data", "done") in triples
    assert drained[-1].kind == "done" and drained[-1].payload["ok"] is True


def test_runner_gate_blocks_until_confirm():
    ran = []
    r = PipelineRunner(
        [Stage("train", lambda emit: ran.append("train"), estimate=lambda: 3.0)]
    )
    r.start()
    time.sleep(0.25)
    assert ran == []
    awaits = [e for e in list(r.events.queue) if e.kind == "await_confirm"]
    assert awaits and awaits[0].payload["estimate_min"] == 3.0
    r.confirm()
    _wait(r)
    assert ran == ["train"] and r.status == "done"


def test_runner_error_emits_error_event():
    def boom(emit):
        raise RuntimeError("x")

    r = PipelineRunner([Stage("data", boom)])
    r.start()
    _wait(r)
    assert r.status == "error"
    assert list(r.events.queue)[-1].payload["ok"] is False


def test_gated_constant():
    assert "train" in GATED and "optimize" in GATED


def test_build_real_stages_shape():
    from pathlib import Path

    from autocv.config import load_config
    from autocv.server.real_stages import build_stages

    cfg = load_config(Path("configs/wafer.yaml"))
    names = [s.name for s in build_stages(cfg, Path.cwd(), optimize=False)]
    assert names == ["data", "split", "train", "infer"]
    opt = [s.name for s in build_stages(cfg, Path.cwd(), optimize=True)]
    assert opt == ["data", "split", "optimize", "infer"]
    train = next(
        s for s in build_stages(cfg, Path.cwd(), optimize=False) if s.name == "train"
    )
    assert train.estimate is not None
