"""Tool replies reach the client as compact JSON, not FastMCP's indent=2."""

import json

from mcp.server.fastmcp.utilities import func_metadata

from mcp_okn import compact_output
from mcp_okn.server import mcp


def _texts(result):
    # FastMCP.call_tool returns content blocks, or (blocks, structured) on newer SDKs.
    blocks = result[0] if isinstance(result, tuple) else result
    return [b.text for b in blocks if getattr(b, "type", None) == "text"]


def test_override_installed():
    assert getattr(func_metadata._convert_to_content, "__wrapped__", None)
    assert compact_output.install() is True  # idempotent


def test_dict_serialized_compactly():
    [block] = func_metadata._convert_to_content({"a": [1, 2], "b": {"c": "d"}})
    assert block.text == '{"a":[1,2],"b":{"c":"d"}}'


def test_strings_pass_through():
    [block] = func_metadata._convert_to_content("line one\n  indented")
    assert block.text == "line one\n  indented"


def test_list_of_dicts_is_one_compact_block():
    blocks = func_metadata._convert_to_content([{"a": 1}, {"b": 2}])
    assert len(blocks) == 1
    assert blocks[0].text == '[{"a":1},{"b":2}]'


async def test_real_tool_reply_has_no_indentation():
    result = await mcp.call_tool("get_join_strategy", {"kg_a": "prokn", "kg_b": "rdkg"})
    [text] = _texts(result)
    assert "\n  " not in text
    assert json.loads(text)  # still valid JSON


async def test_tool_descriptions_are_dedented():
    from mcp_okn.server import mcp

    tools = await mcp.list_tools()
    sparql = next(t for t in tools if t.name == "sparql_query")
    head = (sparql.description or "").splitlines()[:6]
    assert head and not any(line.startswith(" ") for line in head)
    assert all(not (t.description or "").startswith(" ") for t in tools)
