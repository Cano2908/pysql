import os

from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

load_dotenv()


class SQLConnection:
    def __init__(self) -> None:
        self._url: str | None = os.getenv("URL")
        self._user_db: str | None = os.getenv("USER_DB")
        self._pass_db: str | None = os.getenv("PASS_DB")
        self._host_db: str | None = os.getenv("HOST_DB")
        self._port_db: str | None = os.getenv("PORT_DB")
        self._name_db: str | None = os.getenv("NAME_DB")
        self._sgdb: str | None = os.getenv("SGDB")

    def get_engine(self, view_logs: bool = False) -> Engine:
        if self._url is not None:
            database_url = self._url
        else:
            missing_vars = [
                var_name
                for var_name, value in [
                    ("USER_DB", self._user_db),
                    ("PASS_DB", self._pass_db),
                    ("HOST_DB", self._host_db),
                    ("PORT_DB", self._port_db),
                    ("NAME_DB", self._name_db),
                ]
                if value is None
            ]

            if missing_vars:
                raise ValueError(
                    f"Database connection parameters not set in environment variables: {', '.join(missing_vars)}"
                )

            if self._sgdb is None:
                raise ValueError("SGDB is not set in environment variables.")

            if self._sgdb.lower() == "sqlite":
                database_url = f"sqlite:///{self._name_db}.db"
            elif self._sgdb.lower() == "postgres":
                database_url = f"postgresql://{self._user_db}:{self._pass_db}@{self._host_db}:{self._port_db}/{self._name_db}"
            elif self._sgdb.lower() == "mysql":
                database_url = f"mysql+mysqlconnector://{self._user_db}:{self._pass_db}@{self._host_db}:{self._port_db}/{self._name_db}"
            else:
                raise ValueError(f"Unsupported SGDB: {self._sgdb}")

        return create_engine(database_url, echo=view_logs)

    def create_db(self, view_logs: bool = False) -> None:
        SQLModel.metadata.create_all(self.get_engine(view_logs=view_logs))
