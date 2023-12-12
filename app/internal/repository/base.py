import abc
from typing import Any, Optional

from sqlalchemy import delete, func, select, update, asc, desc


class AbstractRepositoryBase(abc.ABC):
    """Абстрактный репозиторий."""

    @abc.abstractmethod
    def add(self, obj: Any) -> Any:
        """Добавляет сущность."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, obj: Any, update_data: dict) -> list:
        """Изменяет сущность."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, obj_id: int) -> Any | None:
        """Возвращает сущность по id."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list_by_ids(self, obj_ids: list[int] | tuple[int]) -> tuple:
        """Возвращает список сущностей с поиском по id."""
        raise NotImplementedError

    @abc.abstractmethod
    async def hard_delete(self, obj: Any) -> None:
        """Удаляет сущность из БД."""
        raise NotImplementedError

    @abc.abstractmethod
    async def soft_delete(self, obj: Any) -> None:
        """Устанавливает флаг deleted=True у модели."""
        raise NotImplementedError

    async def get_count_by_ids(self, obj_ids: list[int]) -> int:
        raise NotImplementedError


class SqlAlchemyRepositoryBase(AbstractRepositoryBase):
    def __init__(self, session, model_class) -> None:
        self.session = session
        self.model_class = model_class

    def _get_all_by_fields_query(self, fields_mapping: dict, with_deleted: bool = False,
                                 order_by_field: Optional[str] = None, order_type: Optional[str] = 'ASC') -> 'Select':
        """Получает все записи по полям. Поддерживает сортировку и фильтрацию по удаленным"""
        q = []
        for field_name, field_values in fields_mapping.items():
            q.append(getattr(self.model_class, field_name).in_(field_values))
        if order_by_field:
            if order_type == 'ASC':
                stmp = select(self.model_class).where(*q).order_by(asc(order_by_field))
            else:
                stmp = select(self.model_class).where(*q).order_by(desc(order_by_field))
        else:
            stmp = select(self.model_class).where(*q)
        return stmp

    def _get_latest_version_by_field_query(self, q) -> 'Select':
        stmp = select(self.model_class).where(*q).where(
            self.model_class.version == select(func.max(self.model_class.version)).where(*q).scalar_subquery())
        return stmp

    async def get(self, obj_id: int) -> Any | None:
        q = [self.model_class.id == obj_id]
        stmp = select(self.model_class).where(*q)
        return (await self.session.execute(stmp)).scalars().first()

    async def get_by_uuid(self, obj_uuid: str) -> Any | None:
        q = [self.model_class.uuid == obj_uuid]
        stmp = select(self.model_class).where(*q)
        return (await self.session.execute(stmp)).scalars().first()

    async def get_first_by_field(self, field_name: str, field_value: str | int) -> Any | None:
        q = [getattr(self.model_class, field_name) == field_value]
        stmp = select(self.model_class).where(*q)
        return (await self.session.execute(stmp)).scalars().first()

    async def get_ids_by_field(self, field_name: str, field_value) -> tuple:
        q = [getattr(self.model_class, field_name) == field_value]
        stmp = select(self.model_class.id).where(*q)
        return (await self.session.execute(stmp)).scalars().all()

    async def get_all_by_field(self, field_name: str, field_values: list | tuple, with_deleted: bool = False,
                               order_by: Any = None
                               ) -> tuple:
        q = [getattr(self.model_class, field_name).in_(field_values)]
        stmp = select(self.model_class).where(*q)
        if order_by is not None:
            stmp = stmp.order_by(order_by)
        return (await self.session.execute(stmp)).scalars().all()

    async def get_all_by_fields(self, fields_mapping: dict, with_deleted: bool = False) -> tuple:
        """Фильтрует по набору полей и их значений"""
        stmp = self._get_all_by_fields_query(fields_mapping, with_deleted)
        return (await self.session.execute(stmp)).scalars().all()

    async def get_all_ids(self) -> tuple:
        stmp = select(self.model_class.id)
        return (await self.session.execute(stmp)).scalars().all()

    async def get_list_by_ids(self, obj_ids: list[int] | tuple[int]) -> tuple:
        stmp = select(self.model_class).where(*q)
        return (await self.session.execute(stmp)).scalars().all()

    async def get_all_active(self) -> tuple:
        """Получение всех неудаленных записей"""
        stmp = select(self.model_class).where(*q)
        return (await self.session.execute(stmp)).scalars().unique().all()

    async def get_all(self) -> tuple:
        """Получение всех записей"""
        stmp = select(self.model_class)
        return (await self.session.execute(stmp)).scalars().unique().all()

    def add(self, obj: Any) -> None:
        self.session.add(obj)

    def add_list(self, obj_list: list | tuple) -> Any:
        return self.session.add_all(obj_list)

    def update(self, obj, update_data: dict, add_session: bool = True) -> list:
        changes_fields = []
        for field, new_value in update_data.items():
            if hasattr(obj, field) and getattr(obj, field) != new_value:
                setattr(obj, field, new_value)
                changes_fields.append(field)
        if add_session and changes_fields:
            self.session.add(obj)
        return changes_fields

    async def hard_delete(self, model: Any) -> None:
        await self.session.delete(model)

    def soft_delete(self, model: Any) -> None:
        model.deleted = True
        self.session.add(model)
