from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.DBDefinitions.BaseModel import BaseDBModel, IDType


class JournalTypeModel(BaseDBModel):
    # Společné údaje, například id, přebíráme z BaseDBModel.
    __tablename__ = "journaltypes"

    name: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Interní název typu časopisu",
    )

    label: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Zobrazovaný název typu časopisu",
    )

    description: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Popis typu časopisu",
    )

    # Odkaz na nadřazený typ. Kořenový typ nemá rodiče.
    parent_id: Mapped[IDType] = mapped_column(
        ForeignKey("journaltypes.id"),
        index=True,
        nullable=True,
        default=None,
        comment="ID nadřazeného typu časopisu",
    )

    parent = relationship(
        "JournalTypeModel",
        viewonly=True,
        remote_side="JournalTypeModel.id",
        uselist=False,
    )

    # Podtypy patřící pod tento typ.
    children = relationship(
        "JournalTypeModel",
        back_populates="parent",
        uselist=True,
        init=True,
        cascade="save-update",
    )