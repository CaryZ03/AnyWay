from apps.workflow.services import WorkflowValidator, WorkflowEngine, WorkflowExecutionError


def test_validate_requires_start_and_end():
    definition = {"nodes": [{"id": "n1", "type": "start"}], "edges": []}
    errors, warnings = WorkflowValidator.validate(definition)
    assert errors  # missing end
    assert any("结束节点" in e for e in errors)


def test_validate_detects_cycle():
    definition = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "a", "type": "llm"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"source": "start", "target": "a"},
            {"source": "a", "target": "start"},  # cycle
            {"source": "a", "target": "end"},
        ],
    }
    errors, warnings = WorkflowValidator.validate(definition)
    assert any("循环" in e for e in errors)


def test_topological_order_basic():
    definition = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "end", "type": "end"},
        ],
        "edges": [
            {"source": "start", "target": "end"},
        ],
    }
    ordered = WorkflowValidator.topological_order(definition)
    ids = [n.id for n in ordered]
    assert ids[0] == "start"
    assert ids[-1] == "end"


def test_replace_variables_supports_input_and_nodes():
    engine = WorkflowEngine()
    engine.context = {
        "input": {"user": "alice"},
        "n1": {"result": "hello"},
        "n2": "raw",
    }
    text = "{input.user}:{n1.result}:{n2}"
    assert engine._replace_variables(text) == "alice:hello:raw"


def test_assert_valid_raises_on_invalid():
    definition = {"nodes": [], "edges": []}
    try:
        WorkflowValidator.assert_valid(definition)
    except WorkflowExecutionError as exc:
        assert "失败" in str(exc)
    else:
        assert False, "expected WorkflowExecutionError"

