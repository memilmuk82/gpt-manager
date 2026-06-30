from app.config import BASE_DIR, normalize_database_url


def test_relative_sqlite_database_url_is_rooted_at_project_data_dir():
    database_url = normalize_database_url("sqlite:///data/app.db")

    assert database_url == f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"


def test_memory_sqlite_database_url_is_unchanged():
    assert normalize_database_url("sqlite:///:memory:") == "sqlite:///:memory:"
