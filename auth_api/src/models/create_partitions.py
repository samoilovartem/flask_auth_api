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
