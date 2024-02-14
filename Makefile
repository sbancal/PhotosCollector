install:
	poetry install
	npm install

lint:
	poetry run pre-commit run -a
