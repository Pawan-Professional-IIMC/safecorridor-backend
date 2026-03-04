from sqlalchemy import inspect, text
from .database import engine


def ensure_airport_columns() -> None:
    inspector = inspect(engine)
    dialect = engine.dialect.name
    try:
        cols = {c["name"] for c in inspector.get_columns("airports")}
    except Exception:
        return

    statements: list[str] = []
    if "airport_status" not in cols:
        statements.append("ALTER TABLE airports ADD COLUMN airport_status VARCHAR(20) DEFAULT 'UNKNOWN'")
    if "airspace_status" not in cols:
        statements.append("ALTER TABLE airports ADD COLUMN airspace_status VARCHAR(20) DEFAULT 'UNKNOWN'")
    if "airline_operations" not in cols:
        statements.append("ALTER TABLE airports ADD COLUMN airline_operations VARCHAR(20) DEFAULT 'UNKNOWN'")
    if "status_source_name" not in cols:
        statements.append("ALTER TABLE airports ADD COLUMN status_source_name VARCHAR")
    if "last_verified_utc" not in cols:
        if dialect == "sqlite":
            statements.append("ALTER TABLE airports ADD COLUMN last_verified_utc DATETIME")
        else:
            statements.append("ALTER TABLE airports ADD COLUMN last_verified_utc TIMESTAMP WITH TIME ZONE")

    if not statements:
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.execute(
            text(
                """
                UPDATE airports
                SET airport_status = COALESCE(airport_status, CAST(status AS TEXT), 'UNKNOWN')
                """
            )
        )
        conn.execute(
            text(
                """
                UPDATE airports
                SET airspace_status = COALESCE(
                    airspace_status,
                    CASE CAST(status AS TEXT)
                        WHEN 'CLOSED' THEN 'CLOSED'
                        WHEN 'RESTRICTED' THEN 'RESTRICTED'
                        WHEN 'OPEN' THEN 'OPEN'
                        ELSE 'UNKNOWN'
                    END
                )
                """
            )
        )
        conn.execute(
            text(
                """
                UPDATE airports
                SET airline_operations = COALESCE(
                    airline_operations,
                    CASE CAST(status AS TEXT)
                        WHEN 'CLOSED' THEN 'SUSPENDED'
                        WHEN 'RESTRICTED' THEN 'LIMITED'
                        WHEN 'OPEN' THEN 'NORMAL'
                        ELSE 'UNKNOWN'
                    END
                )
                """
            )
        )
        conn.execute(text("UPDATE airports SET last_verified_utc = COALESCE(last_verified_utc, status_last_updated)"))
