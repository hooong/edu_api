up:
	docker compose up -d
	docker compose exec app alembic upgrade head

down:
	docker compose down

create-seed-data: up
	docker compose exec app python ./scripts/create_seed_data.py

test:
	docker compose exec app python -m pytest tests -v
