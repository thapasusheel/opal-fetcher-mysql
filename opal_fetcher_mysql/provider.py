from typing import List, Dict, Optional, Any

import aiomysql
from aiomysql.sa.transaction import Transaction
from pydantic import BaseModel, Field

from opal_common.fetcher.fetch_provider import BaseFetchProvider
from opal_common.fetcher.events import FetcherConfig, FetchEvent
from opal_common.logger import logger


class MySQLConnectionParams(BaseModel):
    database: Optional[str] = Field(None, description="The name of the database")
    user: Optional[str] = Field(None, description="User name used to authenticate")
    password: Optional[str] = Field(None, description="Password used to authenticate")
    host: Optional[str] = Field(
        None, description="Database host address (defaults to UNIX socket if not provided)"
    )
    port: Optional[int] = Field(None, description="Connection port number (defaults to 3306 if not provided)")


class MySQLFetcherConfig(FetcherConfig):
    fetcher: str = "MySQLFetchProvider"
    connection_params: Optional[MySQLConnectionParams] = Field(
        None, description="These params can override or complement parts of the DSN (connection string)"
    )
    query: str = Field(..., description="The query to run against MySQL to fetch the data")
    fetch_one: bool = Field(False, description="Whether to fetch only one row from the results of the SELECT query")


class MySQLFetchEvent(FetchEvent):
    fetcher: str = "MySQLFetchProvider"
    config: MySQLFetcherConfig = None


class MySQLFetchProvider(BaseFetchProvider):
    def __init__(self, event: MySQLFetchEvent) -> None:
        super().__init__(event)
        self._connection: Optional[aiomysql.Connection] = None
        self._transaction: Optional[Transaction] = None

    def parse_event(self, event: FetchEvent) -> MySQLFetchEvent:
        return MySQLFetchEvent(**event.dict(exclude={"config"}), config=event.config)

    async def __aenter__(self):
        self._event: MySQLFetchEvent
        connection_params = {} if self._event.config.connection_params is None else self._event.config.connection_params.dict(exclude_none=True)

        try:
            logger.debug(f"Connecting to database with params: {connection_params}")
            self._connection: aiomysql.Connection = await aiomysql.connect(
                host=connection_params.get('host'),
                port=connection_params.get('port', 3306),
                user=connection_params.get('user'),
                password=connection_params.get('password'),
                db=connection_params.get('database')
            )

            self._transaction: Transaction = self._connection.begin()
            await self._transaction.__aenter__()

            logger.debug("Connected to database")
            return self
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    async def __aexit__(self, exc_type=None, exc_val=None, tb=None):
        if self._transaction is not None:
            if exc_type is not None:
                await self._transaction.rollback()
            else:
                await self._transaction.commit()
            await self._transaction.__aexit__(exc_type, exc_val, tb)

        if self._connection is not None:
            self._connection.close()
            logger.debug("Connection to database closed")

    async def _fetch_(self) -> List[Dict[str, Any]]:
        self._event: MySQLFetchEvent
        try:
            async with self._connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(self._event.config.query)

                if self._event.config.fetch_one:
                    row = await cursor.fetchone()
                    return [row] if row else []
                else:
                    rows = await cursor.fetchall()
                    return rows
        except Exception as e:
            logger.error(f"Error fetching data from database: {e}")
            raise

    async def _process_(self, records: List[Dict[str, Any]]) -> Any:
        self._event: MySQLFetchEvent

        if self._event.config.fetch_one:
            return records[0] if records else {}

        if self._event.config.fetch_key is None:
            return records
        else:
            res_dict = {record[self._event.config.fetch_key]: record for record in records if self._event.config.fetch_key in record}
            return res_dict
