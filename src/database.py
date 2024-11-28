import sqlite3
import aiosqlite
import logging
from src.config import get_config
from src.exceptions import DatabaseConnectionError, QueryExecutionError, CacheError

# Load configuration
config = get_config()
debug_mode = config.get("debug", False)
console_log = config.get("console_log", True)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO if console_log else logging.WARNING)

class DatabaseConnection:
    """
    Manages synchronous and asynchronous SQLite database connections with optional query caching.
    """

    def __init__(self, db_url: str = None):
        """
        Initialize the DatabaseConnection instance.

        :param db_url: Path to the SQLite database file. Defaults to the value in the config.
        """
        self.db_url = db_url or config.get("database_path", "example.db")
        self.sync_conn = None
        self.async_conn = None
        self.cache = {}

    def connect_sync(self):
        """
        Establish a synchronous connection to the database.

        :return: Synchronous SQLite connection.
        """
        if not self.sync_conn:
            try:
                self.sync_conn = sqlite3.connect(self.db_url)
                if console_log:
                    logger.info(f"Synchronous connection established to {self.db_url}.")
            except sqlite3.Error as e:
                message = f"Error establishing synchronous connection: {e}"
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise DatabaseConnectionError(message) from e
        return self.sync_conn

    async def connect_async(self):
        """
        Establish an asynchronous connection to the database.

        :return: Asynchronous SQLite connection.
        """
        if not self.async_conn:
            try:
                self.async_conn = await aiosqlite.connect(self.db_url)
                if console_log:
                    logger.info(f"Asynchronous connection established to {self.db_url}.")
            except sqlite3.Error as e:
                message = f"Error establishing asynchronous connection: {e}"
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise DatabaseConnectionError(message) from e
        return self.async_conn

    def close_sync(self):
        """
        Close the synchronous database connection.
        """
        if self.sync_conn:
            try:
                self.sync_conn.close()
                if console_log:
                    logger.info("Synchronous connection closed.")
            except sqlite3.Error as e:
                message = f"Error closing synchronous connection: {e}"
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise DatabaseConnectionError(message) from e
            finally:
                self.sync_conn = None

    async def close_async(self):
        """
        Close the asynchronous database connection.
        """
        if self.async_conn:
            try:
                await self.async_conn.close()
                if console_log:
                    logger.info("Asynchronous connection closed.")
            except sqlite3.Error as e:
                message = f"Error closing asynchronous connection: {e}"
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise DatabaseConnectionError(message) from e
            finally:
                self.async_conn = None

    def execute_with_cache(self, query, params=None):
        """
        Execute a query and cache the results to improve performance on repeat queries.

        :param query: SQL query string.
        :param params: Parameters for the query.
        :return: Results of the query.
        """
        params = params or ()
        cache_key = (query, tuple(params))

        if cache_key in self.cache:
            if console_log:
                logger.info(f"Cache hit for query: {query}")
            return self.cache[cache_key]

        try:
            connection = self.connect_sync()
            cursor = connection.execute(query, params)
            results = cursor.fetchall()
            self.cache[cache_key] = results
            if console_log:
                logger.info(f"Cache miss for query: {query}")
            return results
        except sqlite3.Error as e:
            message = f"Error executing cached query: {query} with params: {params}. Error: {e}"
            if console_log:
                logger.error(message)
            if debug_mode:
                raise QueryExecutionError(query, message) from e

    def invalidate_cache(self):
        """
        Invalidate all cached queries.
        """
        self.cache.clear()
        if console_log:
            logger.info("Cache cleared.")

    def execute_sync(self, query, params=None):
        """
        Execute a query without caching.

        :param query: SQL query string.
        :param params: Parameters for the query.
        :return: Results of the query.
        """
        params = params or ()
        try:
            connection = self.connect_sync()
            cursor = connection.execute(query, params)
            results = cursor.fetchall()
            if console_log:
                logger.info(f"Query executed: {query}")
            return results
        except sqlite3.Error as e:
            message = f"Error executing query: {query} with params: {params}. Error: {e}"
            if console_log:
                logger.error(message)
            if debug_mode:
                raise QueryExecutionError(query, message) from e

    async def execute_async(self, query, params=None):
        """
        Execute a query asynchronously.

        :param query: SQL query string.
        :param params: Parameters for the query.
        :return: Results of the query.
        """
        params = params or ()
        try:
            connection = await self.connect_async()
            async with connection.execute(query, params) as cursor:
                results = await cursor.fetchall()
                if console_log:
                    logger.info(f"Async query executed: {query}")
                return results
        except sqlite3.Error as e:
            message = f"Error executing async query: {query} with params: {params}. Error: {e}"
            if console_log:
                logger.error(message)
            if debug_mode:
                raise QueryExecutionError(query, message) from e
