from __future__ import annotations

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
    firstname: str
    lastname: str

    @classmethod
    def add_user(cls, session: Session, firstname: str, lastname: str) -> User:
        """
        Adds a new user to the database.

        Args:
            session (Session): The database session.
            firstname (str): The user's firstname.
            lastname (str): The user's lastname.

        Returns:
            User: The newly created user.
        """

        if not firstname or not lastname or not isinstance(firstname, str) or not isinstance(lastname, str):
            raise ValueError("Firstname and lastname must be strings")

        user = User(firstname=firstname, lastname=lastname)

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
    def get_all_users(cls, session: Session) -> List["User"]:
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

    def __str__(self) -> str:
        return f"ID: {self.id}, Name: {self.firstname} {self.lastname}"