import unittest
from gamepp.patterns.singleton import Singleton


class DatabaseConnection(Singleton):
    def __init__(self, connection_string="default_connection"):
        # This __init__ will only be called the first time DatabaseConnection() is invoked.
        # Using a flag to check if init was called, as print statements are hard to check in tests directly.
        self.initialized_with = connection_string
        self.connection_string = connection_string
        self.connection_id = id(self)

    def connect(self):
        # In a real scenario, this would establish a connection.
        # For tests, we can just return a status or a property.
        return f"Connected with {self.connection_string} (ID: {self.connection_id})"

    def __str__(self):
        return f"DatabaseConnection(connection_string='{self.connection_string}', id={self.connection_id})"


class Logger(Singleton):
    def __init__(self, level="INFO"):
        self.initialized_with_level = level
        self.level = level
        self.logs = []

    def log(self, message):
        log_entry = f"[{self.level}] {message}"
        self.logs.append(log_entry)
        return log_entry  # Return for potential assertion

    def __str__(self):
        return f"Logger(level='{self.level}', logs_count={len(self.logs)})"


class TestSingletonPattern(unittest.TestCase):
    def setUp(self):
        """Ensure a clean state for Singleton instances before each test."""
        # Reset the _instances dictionary in SingletonMeta for isolated tests.
        # This is a common practice for testing singletons, though it accesses a "private" member.
        if hasattr(Singleton, "_instances"):
            Singleton._instances = {}
        if hasattr(
            DatabaseConnection, "_instances"
        ):  # Also reset for specific classes if they were accessed
            DatabaseConnection._instances = {}
        if hasattr(Logger, "_instances"):
            Logger._instances = {}

    def test_database_connection_is_singleton(self):
        db1_conn_str = "mysql://user:pass@host1/db"
        db1 = DatabaseConnection(db1_conn_str)
        self.assertEqual(db1.connection_string, db1_conn_str)
        self.assertEqual(db1.initialized_with, db1_conn_str)

        db2_conn_str = "postgresql://user:pass@host2/db"  # This arg should be ignored
        db2 = DatabaseConnection(db2_conn_str)

        self.assertIs(
            db1, db2, "DatabaseConnection instances should be the same object."
        )
        self.assertEqual(
            db2.connection_string,
            db1_conn_str,
            "Second instance should retain the original connection string.",
        )
        # Check that __init__ was not called again with new params
        self.assertEqual(
            db2.initialized_with,
            db1_conn_str,
            "__init__ should not have been re-run with new parameters for db2.",
        )
        self.assertEqual(
            db1.connect(), f"Connected with {db1_conn_str} (ID: {id(db1)})"
        )
        self.assertEqual(
            db2.connect(), f"Connected with {db1_conn_str} (ID: {id(db1)})"
        )  # db2 uses db1's string

    def test_logger_is_singleton(self):
        logger_a_level = "DEBUG"
        logger_a = Logger(logger_a_level)
        self.assertEqual(logger_a.level, logger_a_level)
        self.assertEqual(logger_a.initialized_with_level, logger_a_level)
        logger_a.log("Debug message.")

        logger_b_level = "WARNING"  # This arg should be ignored
        logger_b = Logger(logger_b_level)

        self.assertIs(logger_a, logger_b, "Logger instances should be the same object.")
        self.assertEqual(
            logger_b.level,
            logger_a_level,
            "Second logger instance should retain the original level.",
        )
        self.assertEqual(
            logger_b.initialized_with_level,
            logger_a_level,
            "__init__ should not have been re-run with new parameters for logger_b.",
        )

        logger_b.log("Another message.")
        self.assertEqual(
            len(logger_a.logs), 2, "Both log messages should be in logger_a's logs."
        )
        self.assertEqual(
            len(logger_b.logs),
            2,
            "Both log messages should be in logger_b's logs as it is logger_a.",
        )
        self.assertIn("[DEBUG] Debug message.", logger_a.logs)
        self.assertIn("[DEBUG] Another message.", logger_a.logs)

    def test_singleton_init_called_once_per_class(self):
        # Clear instances to ensure clean test for __init__ calls
        Singleton._instances = {}
        DatabaseConnection._instances = {}
        Logger._instances = {}

        db_conn = DatabaseConnection("first_init_db")
        self.assertEqual(db_conn.initialized_with, "first_init_db")
        # Attempt to create again, __init__ should not re-run with new args
        db_conn_again = DatabaseConnection("second_init_db_ignored")
        self.assertEqual(db_conn_again.initialized_with, "first_init_db")
        self.assertIs(db_conn, db_conn_again)

        log_conn = Logger("first_init_log")
        self.assertEqual(log_conn.initialized_with_level, "first_init_log")
        # Attempt to create again
        log_conn_again = Logger("second_init_log_ignored")
        self.assertEqual(log_conn_again.initialized_with_level, "first_init_log")
        self.assertIs(log_conn, log_conn_again)


if __name__ == "__main__":
    unittest.main()
