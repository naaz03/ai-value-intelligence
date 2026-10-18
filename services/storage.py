"""Portable table I/O: JSON (primary for Streamlit Cloud), Parquet optional, DuckDB optional."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import SETTINGS

try:
    import duckdb as _duckdb
except Exception:  # pragma: no cover - optional on Streamlit Cloud
    _duckdb = None


def duckdb_available() -> bool:
    return _duckdb is not None


def get_duckdb():
    if _duckdb is None:
        raise RuntimeError("DuckDB is not installed in this environment.")
    return _duckdb


def table_paths(name: str, root: Path | None = None) -> dict[str, Path]:
    base = root or SETTINGS.generated_dir
    return {
        "parquet": base / f"{name}.parquet",
        "json_gz": base / f"{name}.json.gz",
        "json": base / f"{name}.json",
    }


def table_exists(name: str, root: Path | None = None) -> bool:
    paths = table_paths(name, root)
    return any(path.exists() for path in paths.values())


def write_table(name: str, frame: pd.DataFrame, root: Path | None = None) -> None:
    base = root or SETTINGS.generated_dir
    base.mkdir(parents=True, exist_ok=True)
    paths = table_paths(name, base)

    # JSON.gz is the portable Cloud-safe format (no DuckDB / no Parquet engine required).
    with gzip.open(paths["json_gz"], "wt", encoding="utf-8") as handle:
        frame.to_json(handle, orient="records", date_format="iso")

    try:
        frame.to_parquet(paths["parquet"], index=False)
    except Exception:
        # Parquet is optional; JSON.gz is enough for the app to run.
        pass


def read_table_frame(name: str, root: Path | None = None) -> pd.DataFrame:
    paths = table_paths(name, root)
    if paths["parquet"].exists():
        try:
            return pd.read_parquet(paths["parquet"])
        except Exception:
            pass
    if paths["json_gz"].exists():
        with gzip.open(paths["json_gz"], "rt", encoding="utf-8") as handle:
            return pd.read_json(handle, orient="records")
    if paths["json"].exists():
        return pd.read_json(paths["json"], orient="records")
    raise FileNotFoundError(f"Missing generated table {name} under {paths['json_gz'].parent}")


def write_duckdb_if_available(table_names: list[str], root: Path | None = None) -> Path | None:
    if not duckdb_available():
        return None
    base = root or SETTINGS.generated_dir
    db_path = SETTINGS.duckdb_path
    if db_path.exists():
        db_path.unlink()
    wal = Path(str(db_path) + ".wal")
    if wal.exists():
        wal.unlink()

    duckdb = get_duckdb()
    con = duckdb.connect(str(db_path))
    try:
        for name in table_names:
            paths = table_paths(name, base)
            if paths["parquet"].exists():
                con.execute(
                    f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{paths['parquet'].as_posix()}')"
                )
            elif paths["json_gz"].exists():
                frame = read_table_frame(name, base)
                con.register(f"_tmp_{name}", frame)
                con.execute(f"CREATE TABLE {name} AS SELECT * FROM _tmp_{name}")
                con.unregister(f"_tmp_{name}")
            else:
                raise FileNotFoundError(f"Cannot load {name} into DuckDB")
    finally:
        con.close()
    return db_path


def write_manifest(tables: dict[str, pd.DataFrame], root: Path | None = None, extra: dict[str, Any] | None = None) -> Path:
    base = root or SETTINGS.generated_dir
    summary = {
        name: {"rows": int(len(frame)), "columns": list(frame.columns)} for name, frame in tables.items()
    }
    payload = {
        "storage": {
            "primary": "json.gz",
            "parquet": "optional",
            "duckdb": "optional",
        },
        "tables": summary,
    }
    if extra:
        payload.update(extra)
    path = base / "manifest.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
