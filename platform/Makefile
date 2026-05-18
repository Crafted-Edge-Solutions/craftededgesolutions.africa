PYTHON = .venv/bin/python
MANAGE = $(PYTHON) manage.py

.PHONY: install dev migrate makemigrations superuser shell collectstatic

install:
	uv sync

dev:
	$(MANAGE) runserver 0.0.0.0:8001

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

superuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

collectstatic:
	$(MANAGE) collectstatic --noinput

setup: install migrate superuser
