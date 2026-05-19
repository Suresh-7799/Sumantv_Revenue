from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class Workspace(db.Model):

    __tablename__ = "workspaces"

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    owner_id = db.Column(

        db.Integer,

        db.ForeignKey("users.id"),

        nullable=False,

        index=True

    )

    name = db.Column(

        db.String(255),

        nullable=False

    )

    slug = db.Column(

        db.String(255),

        unique=True,

        nullable=False,

        index=True

    )

    description = db.Column(

        db.Text,

        nullable=True

    )

    sheet_data = db.Column(

        JSONB,

        nullable=False,

        default=dict

    )

    version = db.Column(

        db.Integer,

        nullable=False,

        default=1

    )

    is_archived = db.Column(

        db.Boolean,

        default=False

    )

    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

    updated_at = db.Column(

        db.DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow

    )

    versions = db.relationship(

        "WorkspaceVersion",

        backref="workspace",

        lazy=True,

        cascade="all, delete-orphan"

    )

    def to_dict(self):

        return {

            "id": self.id,

            "owner_id": self.owner_id,

            "name": self.name,

            "slug": self.slug,

            "description": self.description,

            "sheet_data": self.sheet_data,

            "version": self.version,

            "is_archived": self.is_archived,

            "created_at": (
                self.created_at.isoformat()
            ),

            "updated_at": (
                self.updated_at.isoformat()
            )

        }