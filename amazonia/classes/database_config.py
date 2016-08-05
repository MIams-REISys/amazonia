class DatabaseConfig(object):
    def __init__(self, db_hdd_size, db_instance_type, db_engine, db_port, db_name,
                 db_snapshot_id):
        """
        :param db_snapshot_id: id of snapshot to restore from
        :param db_hdd_size: allocated storage size
        :param db_name: the specific name of the database to be created
        :param db_instance_type: Size of the RDS instance
        :param db_engine: DB engine type (Postgres, Oracle, MySQL, etc)
        :param db_port: Port of RDS instance
        """
        self.db_hdd_size = db_hdd_size
        self.db_instance_type = db_instance_type
        self.db_engine = db_engine
        self.db_port = db_port
        self.db_name = db_name
        self.db_snapshot_id = db_snapshot_id
