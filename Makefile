conda-update:
	conda env update --prune -f environment.yml

pip-tools:
	python -m pip install pip-tools
	pip-compile requirements/base.in

# execute after pull this repo
	pip-sync requirements/base.txt

run:
	python .

watch:
	uvicorn app.app:app --reload

compose-up-files:
	docker compose -f ./app/mongodb/configs/docker-compose.yml up -d --build
	docker compose -f ./app/mongodb/shard1/docker-compose.yml up -d --build
	docker compose -f ./app/mongodb/shard2/docker-compose.yml up -d --build
	docker compose -f ./app/mongodb/docker-compose.yml up -d --build

compose-down-files:
	docker compose -f ./app/mongodb/configs/docker-compose.yml down
	docker compose -f ./app/mongodb/shard1/docker-compose.yml down
	docker compose -f ./app/mongodb/shard2/docker-compose.yml down
	docker compose -f ./app/mongodb/docker-compose.yml down