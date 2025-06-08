import uuid
from typing import Generic, Sequence, TypeVar, Union, get_args, get_origin

from sqlmodel import Session, SQLModel, select

from pysql import SQLConnection

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateType = TypeVar("CreateType", bound=SQLModel)
UpdateType = TypeVar("UpdateType", bound=SQLModel)


class BaseModelDAO(Generic[ModelType, CreateType, UpdateType]):
    """
    A generic repository class for performing CRUD operations on a SQLModel.
    This repository is designed to work seamlessly with SQLModel and FastAPI, providing a solid foundation for building APIs and database interactions.

    This implementation utilizes the models and concepts outlined in the SQLModel documentation, in conjunction with FastAPI for building high-performance asynchronous APIs.

    https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/#avoid-duplication-keep-it-simple

    Attributes:
        model (Type[ModelType]): The SQLModel class to perform operations on.

    Methods:
        get_all() -> List[ModelType]:
            Asynchronously retrieves all records of the model from the database.

        get_by_id(obj_id: uuid.UUID or int) -> Optional[ModelType]:
            Asynchronously retrieves a single record by its UUID from the database.

        create(obj_create: CreateType) -> ModelType:
            Asynchronously creates a new record in the database.

        update(obj_id: uuid.UUID or int, obj_update: UpdateType) -> Optional[ModelType]:
            Asynchronously updates an existing record in the database.

        delete(obj_id: uuid.UUID or int) -> Optional[ModelType]:
            Asynchronously deletes a record from the database.

    Example of instantiating the ModelRepository from a UserDAO file inheriting from ModelRepository.
    This allows you to add custom functions for more elaborate queries using SQLModel.

    ```python
    class UserDAO(BaseModelDAO[User, UserCreate, UserUpdate]):

        # Example of a custom query
        async def get_users_by_role(self, role: RoleUser):
            statement = select(User).where(User.role == role)
            result = await self.session.execute(statement)
            return result.scalars().all()

    class UserManager:
        def __init__(self) -> None:
            self._user_dao = UserDAO()

        async def get_all_users(self) -> Sequence[User]:
            return await self._user_dao.get_all()
    ```

    SQLModel and FastAPI
    This repository pattern aligns well with FastAPI's dependency injection system,
    making it easy to integrate with endpoints. Here’s an example of a FastAPI route using this repository:

    ```python
    from fastapi import APIRouter

    user_router = APIRouter()

    user_manager = UserManager()

    @user_router.get("/users/", response_model=List[UserRead])
    async def get_all_users():
        return await user_manager.get_all_users()

    @user_router.post("/users/", response_model=UserRead)
    async def create_user(user_create: UserCreate = Body(...)):
        return await user_manager.create_user(user_create)
    ```
    """

    def __init__(self) -> None:
        """
        Initialize the ModelRepository with the given model type.

        Args:
            model (Type[ModelType]): The model class to be used by the repository.
        """

        for base in getattr(self.__class__, "__orig_bases__", []):
            origin = get_origin(base)

            if origin is BaseModelDAO:
                args = get_args(base)

                if len(args) != 3:
                    raise TypeError("BaseModelDAO requires 3 type arguments")

                self.model = args[0]

                break
        else:
            raise TypeError(
                f"Could not determine ModelType for {self.__class__.__name__}"
            )

        self._sql_connection = SQLConnection()

    async def get_all(self) -> Sequence[ModelType]:
        """
        Retrieve all records of the model from the database.

        This asynchronous method opens a new session with the database engine,
        executes a SELECT statement to fetch all records of the specified model,
        and returns the result as a list.

        Returns:
            List[Model]: A list of all records of the model from the database.
        """

        with Session(self._sql_connection.get_engine()) as session:
            return session.exec(select(self.model)).all()

    async def get_by_id(self, obj_id: Union[int, uuid.UUID]) -> ModelType | None:
        """
        Retrieve an object by its ID.

        Args:
            obj_id (Union[int, uuid.UUID]): The ID of the object to retrieve.
                It can be an integer or a UUID.

        Returns:
            The object with the specified ID, or None if no such object exists.
        """

        with Session(self._sql_connection.get_engine()) as session:
            return session.get(self.model, obj_id)

    async def create(self, obj_create: CreateType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            obj_create (CreateType): The data required to create a new record.

        Returns:
            The newly created database object.
        """

        with Session(self._sql_connection.get_engine()) as session:
            db_obj = self.model.model_validate(obj_create)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

            return db_obj

    async def update(
        self, obj_id: Union[int, uuid.UUID], obj_update: UpdateType
    ) -> None | ModelType:
        """
        Update an existing object in the database.
        Args:
            obj_id (Union[int, uuid.UUID]): The ID of the object to update. Can be an integer or a UUID.
            obj_update (UpdateType): An object containing the updated data.
        Returns:
            The updated object if found and updated, otherwise None.
        """

        with Session(self._sql_connection.get_engine()) as session:
            db_obj = session.get(self.model, obj_id)

            if not db_obj:
                return None

            update_data = obj_update.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(db_obj, key, value)

            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)

            return db_obj

    async def delete(self, obj_id: Union[int, uuid.UUID]):
        """
        Deletes an object from the database by its ID.
        Args:
            obj_id (Union[int, uuid.UUID]): The ID of the object to delete. Can be an integer or a UUID.
        Returns:
            The deleted object if it was found and deleted, otherwise None.
        """

        with Session(self._sql_connection.get_engine()) as session:
            db_obj = session.get(self.model, obj_id)

            if not db_obj:
                return None

            session.delete(db_obj)
            session.commit()

            return True
