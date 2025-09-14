from datetime import datetime, timezone

from sqlalchemy import and_, func, desc, case
from sqlalchemy.orm import Session

from edu_register_api.enums import ItemType, ItemStatusFilter, ItemSortType
from edu_register_api.models import Item, Registration
from edu_register_api.repositories import BaseRepository


class ItemRepository(BaseRepository[Item]):
    def __init__(self, session: Session):
        super().__init__(session, Item)

    def get_by_id_and_item_type(self, id: int, item_type: ItemType) -> Item | None:
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.id == id,
                    self.model.item_type == item_type,
                    self.model.deleted_at.is_(None),
                )
            )
            .first()
        )

    def get_items_with_pagination(
        self,
        user_id: int,
        item_type: ItemType,
        page: int = 1,
        size: int = 10,
        status_filter: ItemStatusFilter | None = None,
        sort: ItemSortType = ItemSortType.CREATED,
    ) -> tuple[list[Item], int]:
        registration_count_subquery = (
            self.session.query(
                Registration.item_id,
                func.count(Registration.id).label("registration_count"),
            )
            .filter(Registration.deleted_at.is_(None))
            .group_by(Registration.item_id)
            .subquery()
        )

        user_registration_subquery = (
            self.session.query(Registration.item_id)
            .filter(
                and_(
                    Registration.user_id == user_id,
                    Registration.deleted_at.is_(None),
                )
            )
            .subquery()
        )

        query = (
            self.session.query(
                self.model,
                func.coalesce(
                    registration_count_subquery.c.registration_count, 0
                ).label("registration_count"),
                case(
                    (user_registration_subquery.c.item_id.is_not(None), True),
                    else_=False,
                ).label("is_registered"),
            )
            .outerjoin(
                registration_count_subquery,
                self.model.id == registration_count_subquery.c.item_id,
            )
            .outerjoin(
                user_registration_subquery,
                self.model.id == user_registration_subquery.c.item_id,
            )
            .filter(
                and_(
                    self.model.item_type == item_type,
                    self.model.deleted_at.is_(None),
                )
            )
        )

        if status_filter == ItemStatusFilter.AVAILABLE:
            current_time = datetime.now(timezone.utc)
            query = query.filter(
                and_(
                    self.model.start_at <= current_time,
                    self.model.end_at >= current_time,
                    user_registration_subquery.c.item_id.is_(None),
                )
            )

        if sort == ItemSortType.POPULAR:
            query = query.order_by(
                desc("registration_count"), desc(self.model.created_at)
            )
        else:
            query = query.order_by(desc(self.model.created_at))

        total = query.count()

        results = query.offset((page - 1) * size).limit(size).all()

        items = []
        for item, reg_count, is_registered in results:
            item.registration_count = reg_count
            item.is_registered = is_registered
            items.append(item)

        return items, total
