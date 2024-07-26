from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional, Protocol, runtime_checkable


@runtime_checkable
class BaseBackendProtocol(Protocol):
    _default_db: Optional["BaseBackendProtocol"] = None

    async def find_model(
        self, model_uuid: str
    ) -> Dict[str, Any]: ...  # pragma: no cover

    async def delete_model(
        self, model_uuid: str
    ) -> Dict[str, Any]: ...  # pragma: no cover

    async def update_model(
        self, model_uuid: str, **kwargs: Any
    ) -> Dict[str, Any]: ...  # pragma: no cover

    @staticmethod
    @contextmanager
    def set_default(db: "BaseBackendProtocol") -> Iterator[None]:
        old_default = BaseBackendProtocol._default_db
        try:
            BaseBackendProtocol._default_db = db
            yield
        finally:
            BaseBackendProtocol._default_db = old_default

    @staticmethod
    def get_default() -> Optional["BaseBackendProtocol"]:
        return BaseBackendProtocol._default_db


@runtime_checkable
class BaseFrontendProtocol(Protocol):
    _default_db: Optional["BaseFrontendProtocol"] = None

    async def get_user(self, user_uuid: str) -> Dict[str, Any]: ...  # pragma: no cover

    @staticmethod
    @contextmanager
    def set_default(db: "BaseFrontendProtocol") -> Iterator[None]:
        old_default = BaseFrontendProtocol._default_db
        try:
            BaseFrontendProtocol._default_db = db
            yield
        finally:
            BaseFrontendProtocol._default_db = old_default

    @staticmethod
    def get_default() -> Optional["BaseFrontendProtocol"]:
        return BaseFrontendProtocol._default_db
