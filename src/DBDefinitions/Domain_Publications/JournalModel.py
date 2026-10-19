from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.DBDefinitions.BaseModel import BaseDBModel, IDType


class JournalModel(BaseDBModel):
    __tablename__ = "journals"

    name: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Název časopisu",
    )

    short_name: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Zkrácený název časopisu",
    )

    # Každý časopis může odkazovat na svůj typ.
    journal_type_id: Mapped[IDType] = mapped_column(
        ForeignKey("journaltypes.id"),
        index=True,
        nullable=True,
        default=None,
        comment="ID typu časopisu",
    )

    issn: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="ISSN tištěného časopisu",
    )

    eissn: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="ISSN elektronického časopisu",
    )

    publisher: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Vydavatel časopisu",
    )

    website: Mapped[str] = mapped_column(
        default=None,
        nullable=True,
        comment="Webová stránka časopisu",
    )

    # Umožňuje načíst objekt typu podle journal_type_id.
    type = relationship(
        "JournalTypeModel",
        viewonly=True,
    )