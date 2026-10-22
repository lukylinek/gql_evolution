"""Databázové testy časopisů přes učitelovy CRUD funkce."""

import json
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema

from src.DBDefinitions import (
    BaseDBModel, ComposeConnectionString, JournalModel, JournalTypeModel,
)
from src.DBDefinitions.main import (
    op_create, op_get, op_list, op_update, op_delete,
)
from src.DBDefinitions.seed import init_database_data


ROOT = Path(__file__).resolve().parents[2]


@pytest_asyncio.fixture
async def publication_sessions():
    # Každý test má vlastní schéma. Tabulek v public se nedotýkáme.
    schema = "test_publications_" + uuid.uuid4().hex
    engine = create_async_engine(
        ComposeConnectionString(),
        execution_options={"schema_translate_map": {None: schema}},
    )
    created = False
    try:
        async with engine.begin() as connection:
            await connection.execute(CreateSchema(schema))
            await connection.run_sync(BaseDBModel.metadata.create_all)
        created = True
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        if created:
            async with engine.begin() as connection:
                await connection.execute(DropSchema(schema, cascade=True))
        await engine.dispose()


@pytest.mark.parametrize("model", [JournalTypeModel, JournalModel])
async def test_create_read_update_delete(publication_sessions, model):
    async with publication_sessions() as session:
        created = await op_create(session, model, {"name": "Původní název"})
        record_id = created["id"]
        assert isinstance(record_id, uuid.UUID)
        assert created["created"] is not None

    # Nové spojení ověřuje, že se záznam opravdu uložil.
    async with publication_sessions() as session:
        loaded = await op_get(session, model, {"id": record_id})
        assert loaded["name"] == "Původní název"
        await op_update(session, model, {"id": record_id, "name": "Nový název"})

    async with publication_sessions() as session:
        rows = await op_list(session, model, {"where": {"id": {"_eq": record_id}}})
        assert len(rows) == 1
        assert rows[0]["name"] == "Nový název"
        assert (await op_delete(session, model, {"id": record_id}))["ok"] is True

    async with publication_sessions() as session:
        assert (await op_get(session, model, {"id": record_id}))["error"] == "not_found"


@pytest.mark.parametrize("model", [JournalTypeModel, JournalModel])
@pytest.mark.parametrize("operation", [op_get, op_update, op_delete])
async def test_missing_record(publication_sessions, model, operation):
    async with publication_sessions() as session:
        result = await operation(session, model, {"id": uuid.uuid4()})
        assert result["ok"] is False
        assert result["error"] == "not_found"


async def test_journal_type_relationship(publication_sessions):
    async with publication_sessions() as session:
        first = await op_create(session, JournalTypeModel, {"name": "scientific"})
        second = await op_create(session, JournalTypeModel, {"name": "professional"})
        journal = await op_create(session, JournalModel, {
            "name": "Zkušební časopis", "journal_type_id": first["id"],
            "short_name": "ZČ", "issn": "1234-5679", "eissn": None,
            "publisher": "Zkušební vydavatel", "website": "https://example.org",
        })

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"], "include": ["type"]})
        assert loaded["type"]["name"] == "scientific"
        assert loaded["issn"] == "1234-5679"
        assert loaded["eissn"] is None
        await op_update(session, JournalModel, {"id": journal["id"], "journal_type_id": second["id"]})

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"], "include": ["type"]})
        assert loaded["type"]["name"] == "professional"


async def test_type_tree(publication_sessions):
    async with publication_sessions() as session:
        root = await op_create(session, JournalTypeModel, {
            "name": "scientific", "children": [{"name": "technical"}],
        })

    async with publication_sessions() as session:
        root = await op_get(session, JournalTypeModel, {"id": root["id"], "include": ["children"]})
        assert root["parent_id"] is None
        assert len(root["children"]) == 1
        child = root["children"][0]
        assert child["parent_id"] == root["id"]
        loaded = await op_get(session, JournalTypeModel, {"id": child["id"], "include": ["parent"]})
        assert loaded["parent"]["id"] == root["id"]


@pytest.mark.parametrize("model, field", [
    (JournalModel, "journal_type_id"), (JournalTypeModel, "parent_id"),
])
async def test_unknown_foreign_key(publication_sessions, model, field):
    async with publication_sessions() as session:
        with pytest.raises(IntegrityError):
            await op_create(session, model, {"name": "Neplatný odkaz", field: uuid.uuid4()})
        await session.rollback()
        assert await op_list(session, model, {}) == []


@pytest.mark.parametrize("dependent_model, field", [
    (JournalModel, "journal_type_id"), (JournalTypeModel, "parent_id"),
])
@pytest.mark.parametrize("load_children", [False, True])
async def test_used_type_cannot_be_deleted(publication_sessions, dependent_model, field, load_children):
    async with publication_sessions() as session:
        parent = await op_create(session, JournalTypeModel, {"name": "Používaný typ"})
        dependent = await op_create(session, dependent_model, {"name": "Navázaný záznam", field: parent["id"]})

    async with publication_sessions() as session:
        if load_children:
            loaded_parent = await session.get(JournalTypeModel, parent["id"])
            await op_get(session, JournalTypeModel, {"id": parent["id"], "include": ["children"]})
            assert len(loaded_parent.children) == (1 if dependent_model is JournalTypeModel else 0)
        with pytest.raises(IntegrityError):
            await op_delete(session, JournalTypeModel, {"id": parent["id"]})
        await session.rollback()

    async with publication_sessions() as session:
        loaded = await op_get(session, dependent_model, {"id": dependent["id"]})
        assert loaded[field] == parent["id"]
        await op_delete(session, dependent_model, {"id": dependent["id"]})
        assert (await op_delete(session, JournalTypeModel, {"id": parent["id"]}))["ok"] is True


async def test_failed_update_keeps_original_data(publication_sessions):
    async with publication_sessions() as session:
        journal_type = await op_create(session, JournalTypeModel, {"name": "scientific"})
        journal = await op_create(session, JournalModel, {
            "name": "Původní název", "journal_type_id": journal_type["id"],
        })
        with pytest.raises(IntegrityError):
            await op_update(session, JournalModel, {
                "id": journal["id"], "name": "Neuložená změna", "journal_type_id": uuid.uuid4(),
            })
        await session.rollback()

    async with publication_sessions() as session:
        loaded = await op_get(session, JournalModel, {"id": journal["id"]})
        assert loaded["name"] == "Původní název"
        assert loaded["journal_type_id"] == journal_type["id"]


async def test_demo_import_is_repeatable(publication_sessions, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("DEMODATA", "True")
    data = json.loads((ROOT / "systemdata.json").read_text(encoding="utf-8"))
    for _ in range(2):
        async with publication_sessions() as session:
            await init_database_data(session)

    async with publication_sessions() as session:
        types = await op_list(session, JournalTypeModel, {})
        journals = await op_list(session, JournalModel, {"include": ["type"]})
        assert len(types) == len(data["journaltypes"]) > 1
        assert len(journals) == len(data["journals"]) > 0
        assert journals[0]["type"]["id"] == journals[0]["journal_type_id"]
        root_id = uuid.UUID(data["journaltypes"][0]["id"])
        root = await op_get(session, JournalTypeModel, {"id": root_id, "include": ["children"]})
        assert len(root["children"]) == 1


async def test_catalog_import_without_demo_journals(publication_sessions, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv("DEMODATA", raising=False)
    async with publication_sessions() as session:
        await init_database_data(session)
    async with publication_sessions() as session:
        assert len(await op_list(session, JournalTypeModel, {})) > 1
        assert await op_list(session, JournalModel, {}) == []
