from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class WorkspaceVersion(db.Model):

    __tablename__ = "workspace_versions"

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    workspace_id = db.Column(

        db.Integer,

        db.ForeignKey("workspaces.id"),

        nullable=False,

        index=True

    )

    version_number = db.Column(

        db.Integer,

        nullable=False

    )

    snapshot = db.Column(

        JSONB,

        nullable=False

    )

    created_by = db.Column(

        db.Integer,

        db.ForeignKey("users.id"),

        nullable=False

    )

    created_at = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

    rollback_label = db.Column(

        db.String(255),

        nullable=True

    )

    def to_dict(self):

        return {

            "id": self.id,

            "workspace_id": self.workspace_id,

            "version_number": self.version_number,

            "snapshot": self.snapshot,

            "created_by": self.created_by,

            "rollback_label": self.rollback_label,

            "created_at": (
                self.created_at.isoformat()
            )

        }