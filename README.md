# 🚀 PySQL

This repository provides utilities to simplify working with **SQLModel** in Python. It aims to streamline database interaction, especially with **PostgreSQL**, but also supports **SQLite** and **MySQL**.

---

## 👨‍💻 Author

Created by Christian Carballo Cano.  
🔗 [LinkedIn](https://www.linkedin.com/in/cano2908/)

---

## 🛠️ PostgreSQL Connection Configuration

You can connect to a PostgreSQL database using either a direct URL or by defining individual environment variables:

| Variable     | Description                                                                 |
|--------------|------------------------------------------------------------------------------|
| `URL`        | (Optional) Full connection string. If used, other variables are not required. |
| `SGDB`       | Database engine: `sqlite`, `mysql`, or `postgresql`                         |
| `USER_DB`    | Database user                                                               |
| `PASS_DB`    | Database password                                                           |
| `HOST_DB`    | Host or IP address                                                          |
| `PORT_DB`    | Port number                                                                 |
| `NAME_DB`    | Database name                                                               |

> ⚠️ If you don’t provide a `URL`, make sure to set the other variables before using any utilities.

---

## 📦 Installation

```bash
pip install git+https://github.com/Cano2908/pysql.git@v0.1.0
```

## Usage Example: Models, DAO, Manager and Router

Below is a complete example workflow for creating models, a generic DAO, a manager, and a FastAPI router using SQLModel.

### 1. Model Definition

```python
import uuid
from typing import Optional
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    name: str
    email: str

# This class defines the main users table in the database.
# Tip: It is recommended to define all tables and relationships in a separate file (e.g., `models.py`)
# to keep your code organized and maintainable.

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class UserCreate(UserBase): ...

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserRead(UserBase):
    id: uuid.UUID
```

### 2. Specific DAO
You can add custom methods in the `UserDAO` class to perform specific queries, such as searching for users by email, name, or other relevant fields. This allows you to extend the basic functionality of the DAO according to your application's needs.

```python
from sqlmodel import Session, select
from pysql import BaseModelDAO, SQLConnection

class UserDAO(BaseModelDAO[User, UserCreate, UserUpdate]):
    # You can add custom methods here
    async def get_by_email(self, email: str):
        with Session(SQLConnection().get_engine()) as session:
            statement = select(User).where(User.email == email)
            result = session.exec(statement)
            return result.first()

class UserDAO(BaseModelDAO[User, UserCreate, UserUpdate]): ...
```

### 3. Manager

```python
from typing import Sequence

class UserManager:
    def __init__(self) -> None:
        self._user_dao = UserDAO()

    async def get_all_users(self) -> Sequence[User]:
        return await self._user_dao.get_all()

    async def create_user(self, user_create: UserCreate) -> User:
        return await self._user_dao.create(user_create)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._user_dao.get_by_id(user_id)
```

### 4. FastAPI Router

```python
from fastapi import APIRouter, Body
from typing import List

user_router = APIRouter()
user_manager = UserManager()

@user_router.get("/users/", response_model=List[UserRead])
async def get_all_users():
    return await user_manager.get_all_users()

@user_router.post("/users/", response_model=UserRead)
async def create_user(user_create: UserCreate = Body(...)):
    return await user_manager.create_user(user_create)
```

These examples show how to structure your application using PySQL and SQLModel to keep your code clean, reusable, and easy to maintain.
