from __future__ import annotations

from fastapi import File
from sqlmodel import SQLModel, Field, create_engine, Session, select

from typing import Optional, List

class User(SQLModel, table=True):
    """
    A class representing a user in the database.

    Attributes:
        id (Optional[int]): The user's ID.
        firstname (str): The user's firstname.
        lastname (str): The user's lastname.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    firstname: Optional[str]
    lastname: Optional[str]

    @classmethod
    def add_user(cls, session: Session, id: int) -> "User":
        """
        Adds a new user to the database.

        Args:
            session (Session): The database session.
            firstname (str): The user's firstname.
            lastname (str): The user's lastname.

        Returns:
            User: The newly created user.
        """

        user = User(id=id)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @classmethod
    def get_user(cls, session: Session, user_id: int) -> Optional["User"]:
        """
        Retrieves a user from the database.

        Args:
            session (Session): The database session.
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user with the given ID, or None if the user does not exist.
        """

        if not isinstance(user_id, int):
            raise ValueError("User ID must be an integer")

        statement = select(User).where(User.id == user_id)
        result = session.exec(statement)

        return result.first()

    @classmethod
    def delete_user(cls, session: Session, user_id: int) -> bool:
        """
        Deletes a user from the database.

        Args:
            session (Session): The database session.
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """

        if not isinstance(user_id, int):
            raise ValueError("User ID must be an integer")

        user = cls.get_user(session, user_id)

        if user:
            session.delete(user)
            session.commit()
            return True

        return False
    
    @classmethod
    def update_user(cls, session: Session, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """
        Updates a user in the database.

        Args:
            session (Session): The database session.
            user_id (int): The ID of the user to update.
            update_data (UserUpdate): The data to update.

        Returns:
            User: The updated user, or None if the user does not exist.
        """

        user = cls.get_user(session, user_id)

        if user:
            for key, value in update_data.model_dump().items():
                if value:
                    setattr(user, key, value)

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

        return None

    @classmethod
    def get_all_users(cls, session: Session) -> List[User]:
        """
        Retrieves all users from the database.

        Args:
            session (Session): The database session.

        Returns:
            List[User]: A list of all users in the database.
        """

        statement = select(User)
        result = session.exec(statement)

        return result.all()
    
    @classmethod
    def get_next_id(cls, session: Session) -> int:
        """
        Gets the next available user ID.

        Args:
            session (Session): The database session.

        Returns:
            int: The next available user ID.
        """

        statement = select(User).order_by(User.id.desc())
        result = session.exec(statement)

        last_user = result.first()

        if last_user:
            return last_user.id + 1

        return 1

    def __str__(self) -> str:
        return f"ID: {self.id}, Name: {self.firstname} {self.lastname}"

class UserUpdate(SQLModel):
    firstname: Optional[str]
    lastname: Optional[str]