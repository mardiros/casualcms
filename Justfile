package := 'casualcms'
default_test_suite := 'tests/unittests'

doc:
    cd docs && poetry run make html
    xdg-open docs/build/html/index.html

cleandoc:
    cd docs && poetry run make clean

clean_frontend:
    rm -rf src/casualcms/admin/*.*

prettier:
    npx prettier --write src/frontend  tests

lint:
    poetry run flake8 && echo "$(tput setaf 10)Success: no lint issue$(tput setaf 7)"

test: lint mypy unittest jstest functest

unittest test_suite=default_test_suite:
    poetry run pytest -sxv {{test_suite}}

jstest:
    NODE_ENV=dev npm run test

watch:
    NODE_ENV=dev npm run watch

lf:
    poetry run pytest -sxvvv --lf

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    poetry run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

functest: build_dev_frontend
    poetry run behave --no-capture tests/functionals/

servetest:
    poetry run python tests/functionals/fixtures.py

mypy:
    poetry run mypy src/ tests/

black:
    poetry run isort .
    poetry run black .

install:
    npm ci
    poetry install

build_dev_frontend: clean_frontend
    NODE_ENV=dev npm run build_dev

build_frontend: clean_frontend
    npm run build

release major_minor_patch: test && changelog
    poetry version {{major_minor_patch}}
    poetry install

changelog:
    poetry run python scripts/write_changelog.py
    cat CHANGELOG.rst >> CHANGELOG.rst.new
    rm CHANGELOG.rst
    mv CHANGELOG.rst.new CHANGELOG.rst
    $EDITOR CHANGELOG.rst

publish:
    git commit -am "Release $(poetry run python scripts/show_release.py)"
    poetry build
    poetry publish
    git push
    git tag "$(poetry run python scripts/show_release.py)"
    git push origin "$(poetry run python scripts/show_release.py)"
