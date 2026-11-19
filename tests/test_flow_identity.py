"""Check 5, flow identity: (label, compartment, sub_compartment, unit) is unique per
source release, except for the flows a release lists as known duplicates."""

import pytest
from tests.conftest import EF, FLOWS, KG

from sentier_vocab import flow_identity
from sentier_vocab.layers import load_relations, load_terms, write_relations, write_terms
from sentier_vocab.validate import validate

AIR = {"compartment": "air", "sub_compartment": "Emissions to air, unspecified"}
KEY = ("Ammonia", "air", "Emissions to air, unspecified", KG)


def _flow(code, label="Ammonia", **attributes):
    return {
        "iri": FLOWS + code,
        "type": "elementary-flow",
        "pref_label": label,
        "source": EF,
        "status": "draft",
        "attributes": attributes or dict(AIR),
    }


def _unit(code, unit=KG):
    return {"subject": FLOWS + code, "predicate": "qudt:hasUnit", "object": unit, "source": EF}


def _source_term():
    return {"iri": EF, "type": "source", "pref_label": "EF 3.1", "source": EF}


@pytest.fixture
def tree(tmp_path):
    """Write an ef-3.1 release from shards of flows; returns the three directories."""
    terms, relations = tmp_path / "terms", tmp_path / "relations"
    known = tmp_path / "schemas" / "known-duplicate-flows"

    def write(*shards, units=None, listed=None):
        codes = [row["iri"].rsplit("/", 1)[1] for shard in shards for row in shard]
        for index, shard in enumerate(shards, start=1):
            rows = shard + ([_source_term()] if index == 1 else [])
            write_terms(rows, terms, f"ef-3.1-{index:02d}")
        edges = units if units is not None else [_unit(code) for code in codes]
        write_relations(edges, relations, "ef-3.1")
        if listed is not None:
            known.mkdir(parents=True, exist_ok=True)
            lines = ["# a comment", "", *(FLOWS + code for code in listed)]
            (known / "ef-3.1.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return terms, relations, known

    return write


def _identity_errors(layout):
    return [e for e in validate(*layout) if "flow identity" in e or "known duplicate" in e]


def test_distinct_identities_pass(tree):
    layout = tree([_flow("a"), _flow("b", "Benzene")])
    assert validate(*layout) == []


def test_a_collision_across_two_files_of_one_release_is_found(tree):
    (error,) = _identity_errors(tree([_flow("a")], [_flow("b")]))
    assert error.startswith("ef-3.1: flow identity")
    assert repr(KEY) in error
    assert FLOWS + "a" in error and FLOWS + "b" in error


def test_one_line_per_identity_names_every_flow_that_shares_it(tree):
    (error,) = _identity_errors(tree([_flow("a"), _flow("b")], [_flow("c")]))
    assert all(FLOWS + code in error for code in "abc")


def test_releases_do_not_collide_with_each_other(layout):
    terms, relations = layout  # sentier-core and a one-flow ef-3.1
    other = "https://vocab.sentier.dev/sources/other-1"
    rows = [
        {"iri": other, "type": "source", "pref_label": "Other", "source": other},
        {**_flow("x", "Isosorbide", compartment="air"), "source": other},
    ]
    write_terms(rows, terms, "other-1")
    edges = [{**_unit("x"), "source": other}]
    write_relations(edges, relations, "other-1")
    write_relations([_unit("0000b186")], relations, "ef-3.1")
    assert validate(terms, relations) == []


def test_sub_compartment_and_unit_tell_flows_apart(tree):
    water = _flow("b", compartment="air", sub_compartment="Emissions to air, indoor")
    layout = tree(
        [_flow("a"), water, _flow("c")], units=[_unit("a"), _unit("b"), _unit("c", KG[:-6] + "M3")]
    )
    assert validate(*layout) == []


def test_flows_without_a_unit_are_not_checked(tree):
    assert validate(*tree([_flow("a"), _flow("b")], units=[_unit("a")])) == []


def test_a_group_listed_whole_is_accepted(tree):
    assert validate(*tree([_flow("a")], [_flow("b")], listed=["a", "b"])) == []


def test_a_group_listed_in_part_is_still_a_violation_naming_the_unlisted_flows(tree):
    (error,) = _identity_errors(tree([_flow("a"), _flow("b"), _flow("c")], listed=["a", "b"]))
    assert "flow identity" in error
    assert error.endswith(f"not listed as known duplicates: {FLOWS}c")


def test_a_listed_flow_that_is_not_a_flow_of_the_release_is_an_error(tree):
    errors = _identity_errors(tree([_flow("a")], [_flow("b")], listed=["a", "b", "gone"]))
    assert errors == [
        f"ef-3.1.txt: known duplicate {FLOWS}gone is not an elementary flow of release ef-3.1"
    ]


def test_a_listed_flow_that_collides_with_nothing_is_an_error(tree):
    layout = tree([_flow("a"), _flow("b"), _flow("c", "Benzene")], listed=["a", "b", "c"])
    assert _identity_errors(layout) == [
        f"ef-3.1.txt: known duplicate {FLOWS}c shares its identity with no other flow "
        "of release ef-3.1"
    ]


def test_a_flow_listed_twice_is_an_error(tree):
    errors = _identity_errors(tree([_flow("a"), _flow("b")], listed=["a", "b", "a"]))
    assert errors == [f"ef-3.1.txt: known duplicate {FLOWS}a is listed more than once"]


def test_a_list_for_a_release_without_terms_is_an_error(tree):
    terms, relations, known = tree([_flow("a"), _flow("b", "Benzene")])
    known.mkdir(parents=True)
    (known / "nowhere-1.txt").write_text(FLOWS + "a\n", encoding="utf-8")
    assert _identity_errors((terms, relations, known)) == [
        f"nowhere-1.txt: known duplicate {FLOWS}a is not an elementary flow of release nowhere-1"
    ]


def test_the_list_beside_the_terms_is_read_by_default(tree):
    terms, relations, known = tree([_flow("a")], [_flow("b")], listed=["a", "b"])
    assert known == terms.parent / "schemas" / "known-duplicate-flows"
    assert validate(terms, relations) == []
    assert _identity_errors((terms, relations, terms.parent / "elsewhere")) != []


def test_groups_and_render_round_trip_through_the_list_file(tree):
    terms, relations, known = tree(
        [_flow("b"), _flow("z", "Zinc"), _flow("y", "Zinc", compartment="soil")],
        [_flow("a"), _flow("x", "Lead")],
    )
    groups = flow_identity.colliding_groups(load_terms(terms), load_relations(relations))
    assert groups == {"ef-3.1": {KEY: [FLOWS + "a", FLOWS + "b"]}}
    text = flow_identity.render("ef-3.1", groups["ef-3.1"])
    assert text.startswith("# Known duplicate flows of the release ef-3.1")
    assert "python -m sentier_vocab duplicate-flows ef-3.1" in text
    assert "# 1 identities shared by 2 flows" in text
    assert f"# {KEY[0]} | {KEY[1]} | {KEY[2]} | {KEY[3]}\n{FLOWS}a\n{FLOWS}b\n" in text
    known.mkdir(parents=True)
    (known / "ef-3.1.txt").write_text(text, encoding="utf-8")
    assert flow_identity.read_known(known)["ef-3.1"][1] == [FLOWS + "a", FLOWS + "b"]
    assert validate(terms, relations, known) == []


def test_a_missing_sub_compartment_is_shown_as_a_dash(tree):
    terms, relations, _ = tree([_flow("a", compartment="air"), _flow("b", compartment="air")])
    groups = flow_identity.colliding_groups(load_terms(terms), load_relations(relations))
    assert f"# Ammonia | air | - | {KG}\n" in flow_identity.render("ef-3.1", groups["ef-3.1"])
