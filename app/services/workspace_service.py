from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

from app.models.workspace import (
    Workspace
)

from app.models.workspace_version import (
    WorkspaceVersion
)

from app.services.cache_service import (
    CacheService
)

from app.logging.audit import (
    log_action
)


class WorkspaceService:

    @staticmethod
    def create_workspace(

        owner_id,

        name,

        slug,

        description=""

    ):

        workspace = Workspace(

            owner_id=owner_id,

            name=name,

            slug=slug,

            description=description,

            sheet_data={},

            version=1

        )

        db.session.add(workspace)

        db.session.commit()

        log_action(

            user=owner_id,

            action="workspace_created",

            metadata={
                "workspace_id":
                workspace.id
            }

        )

        CacheService.set_workspace_cache(

            workspace.id,

            workspace.to_dict()

        )

        return workspace

    @staticmethod
    def get_workspace(

        workspace_id

    ):

        cached_workspace = (
            CacheService
            .get_workspace_cache(
                workspace_id
            )
        )

        if cached_workspace:

            return cached_workspace

        workspace = Workspace.query.get(
            workspace_id
        )

        if not workspace:

            return None

        workspace_data = (
            workspace.to_dict()
        )

        CacheService.set_workspace_cache(

            workspace_id,

            workspace_data

        )

        return workspace_data

    @staticmethod
    def save_workspace(

        workspace,

        sheet_data,

        updated_by

    ):

        try:

            workspace.version += 1

            workspace.sheet_data = (
                sheet_data
            )

            version_snapshot = (
                WorkspaceVersion(

                    workspace_id=workspace.id,

                    version_number=(
                        workspace.version
                    ),

                    snapshot=sheet_data,

                    created_by=updated_by

                )
            )

            db.session.add(
                version_snapshot
            )

            db.session.commit()

            CacheService.invalidate_workspace_cache(
                workspace.id
            )

            CacheService.set_workspace_cache(

                workspace.id,

                workspace.to_dict()

            )

            log_action(

                user=updated_by,

                action="workspace_saved",

                metadata={
                    "workspace_id":
                    workspace.id,

                    "version":
                    workspace.version
                }

            )

            return workspace

        except SQLAlchemyError:

            db.session.rollback()

            raise

    @staticmethod
    def rollback_workspace(

        workspace,

        version_number

    ):

        version = (
            WorkspaceVersion.query
            .filter_by(

                workspace_id=workspace.id,

                version_number=version_number

            )
            .first()
        )

        if not version:

            return None

        workspace.sheet_data = (
            version.snapshot
        )

        workspace.version += 1

        db.session.commit()

        CacheService.invalidate_workspace_cache(
            workspace.id
        )

        CacheService.set_workspace_cache(

            workspace.id,

            workspace.to_dict()

        )

        log_action(

            user=workspace.owner_id,

            action="workspace_rollback",

            metadata={
                "workspace_id":
                workspace.id,

                "rollback_version":
                version_number
            }

        )

        return workspace