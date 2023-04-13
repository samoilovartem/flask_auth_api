from datetime import datetime

from sqlalchemy import text


def create_partition_auth_history(target, connection, **kw) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_desktop PARTITION OF content.auth_history FOR VALUES IN (
        'desktop');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_tablet PARTITION OF content.auth_history FOR VALUES IN (
        'tablet');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_mobile PARTITION OF content.auth_history FOR VALUES IN (
        'mobile');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_other PARTITION OF content.auth_history FOR VALUES IN (
        'other');"""
    )


def create_partition_user(target, connection, **kw) -> None:
    """
    Creating partition by user creation year
    """
    current_year = datetime.now().year
    for year in range(current_year - 5, current_year + 1):
        connection.execute(
            text(
                f"""CREATE TABLE IF NOT EXISTS "users_{year}"
             PARTITION OF "users" FOR VALUES FROM ('{year}-01-01') TO ('{year}-12-31')
             WITH (DEFAULT)"""
            )
        )
