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
