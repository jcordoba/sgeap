"""Audit logging service."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import ActionType


class AuditService:
    """Service for audit logging."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: ActionType,
        entity: str,
        entity_id: UUID | None = None,
        user_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log_entry = AuditLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def log_create(
        self,
        entity: str,
        entity_id: UUID,
        user_id: UUID | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Log a create action."""
        return self.log(
            action=ActionType.CREATE,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
            new_values=new_values,
            ip_address=ip_address,
        )

    def log_update(
        self,
        entity: str,
        entity_id: UUID,
        user_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Log an update action."""
        return self.log(
            action=ActionType.UPDATE,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )

    def log_delete(
        self,
        entity: str,
        entity_id: UUID,
        user_id: UUID | None = None,
        old_values: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Log a delete action."""
        return self.log(
            action=ActionType.DELETE,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
            old_values=old_values,
            ip_address=ip_address,
        )

    def get_for_expediente(self, expediente_id: UUID) -> list[AuditLog]:
        """Get audit logs for an expediente."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.entity == "Expediente", AuditLog.entity_id == expediente_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )