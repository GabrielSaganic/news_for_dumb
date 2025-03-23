# build
build:
	echo "Building container"
	docker compose build

rebuild:
	echo "Rebuilding container"
	docker compose up --build
# up
up:
	echo "Upping container"
	docker compose up

# migrate
migrate:
	echo "Migrating"
	docker compose exec web poetry run python source/manage.py migrate

# makemigrations
makemigrations:
	echo "Making migrations"
	docker compose exec web poetry run python source/manage.py makemigrations

# scrape_n1
scrape_n1:
	echo "Running n1_latest_news.py"
	docker compose exec web poetry run python source/manage.py n1_latest_news --page=1 --country="hr"

docker_shell:
	echo "Connecting to docker shell"
	docker exec -it <container_name_or_id> /bin/bash

add_package:
	echo "Adding package"
	poetry add <package_name>
	poetry lock