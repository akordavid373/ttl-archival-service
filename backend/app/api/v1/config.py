from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.app.core.config.manager import config_manager, ConfigValidationError
from backend.app.core.config.audit import AuditEntry, write_audit_entry

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])

SECRET_TOKENS = {"SECRET", "KEY", "PASSWORD", "TOKEN"}


class ConfigPatchRequest(BaseModel):
    updates: Dict[str, Any]


class ConfigResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None


def is_secret_field(key: str) -> bool:
    return any(token in key.upper() for token in SECRET_TOKENS)


@router.get("", response_model=ConfigResponse)
async def get_config():
    """Return the current non-secret configuration."""
    config = config_manager.get_public_settings()
    return ConfigResponse(success=True, data={"config": config})


@router.patch("", response_model=ConfigResponse)
async def patch_config(
    payload: ConfigPatchRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Apply runtime configuration updates and log audit entries."""
    if not payload.updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided",
        )

    bad_keys = [key for key in payload.updates if is_secret_field(key)]
    if bad_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Updates not allowed for secret fields: {bad_keys}",
        )

    changed_by = request.headers.get("x-user-id", "system")
    try:
        old_settings = config_manager.get_settings().model_dump()
        new_settings = config_manager.apply_updates(payload.updates)

        audit_tasks = []
        for key, new_value in payload.updates.items():
            audit_entry = AuditEntry(
                field=key,
                old_value=old_settings.get(key),
                new_value=new_value,
                changed_by=changed_by,
            )
            audit_tasks.append(write_audit_entry(audit_entry))

        await _run_audit_tasks(audit_tasks)

        return ConfigResponse(
            success=True,
            data={"config": config_manager.get_public_settings()},
            message="Configuration updated successfully",
        )

    except ConfigValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": exc.errors},
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


async def _run_audit_tasks(tasks: List[Any]) -> None:
    for task in tasks:
        await task
