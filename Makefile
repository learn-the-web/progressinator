postcss := ./node_modules/postcss-cli/bin/postcss --config ./config/postcss.config.js
terser := ./node_modules/terser/bin/terser

apppath := ./progressinator
publicdist := ./public-dist
public := ./public

install:
	brew install node fswatch yarn parallel mkcert nss pyenv pipenv pre-commit
	brew cask install postgres
	yarn install
	pipenv install --dev
	pre-commit install

build:
	mkcert --install
	mkcert progressinator.dev
	mv ./progressinator.dev-key.pem ./config/certs/progressinator.dev-key.pem
	mv ./progressinator.dev.pem ./config/certs/progressinator.dev.pem
	make build-static

start-pgsql:
	open /Applications/Postgres.app

start-server:
	heroku local --port=8000 --procfile=Procfile.dev

watch-django-templates:
	fswatch --verbose -0 --recursive $(apppath)/templates/* $(apppath)/templates/*/* $(apppath)/patterns/* $(apppath)/core/templates/* | xargs -0 -I {} cat .gunicorn.pid | xargs -n 1 -I [] kill -HUP []

start:
	parallel --ungroup ::: "make start-server" "make watch-django-templates"

test:
	pytest

copy-courses:
	cp /db/learn-the-web/www/_site/courses/web-design-1/course.json ./config/courses/web-design-1.json
	cp /db/learn-the-web/www/_site/courses/web-design-2/course.json ./config/courses/web-design-2.json
	cp /db/learn-the-web/www/_site/courses/web-dev-1/course.json ./config/courses/web-dev-1.json
	cp /db/learn-the-web/www/_site/courses/web-dev-2/course.json ./config/courses/web-dev-2.json
	cp /db/learn-the-web/www/_site/courses/web-dev-3/course.json ./config/courses/web-dev-3.json
	cp /db/learn-the-web/www/_site/courses/web-dev-4/course.json ./config/courses/web-dev-4.json
	cp /db/learn-the-web/www/_site/courses/web-dev-5/course.json ./config/courses/web-dev-5.json
	cp /db/learn-the-web/www/_site/courses/web-dev-6/course.json ./config/courses/web-dev-6.json
	cp /db/learn-the-web/www/_site/courses/javascript/course.json ./config/courses/javascript.json

build-courses:
	pipenv run python ./scripts/compile-courses.py

##################################################
# STATIC FILES
##################################################

build-css:
	$(postcss) $(apppath)/css/main.css --output $(publicdist)/main.min.css
	python ./scripts/sri_resource.py "$(publicdist)/main.min.css"

watch-build-main-css:
	$(postcss) $(apppath)/css/main.css --output $(publicdist)/main.min.css --watch

watch-css-copy-dist:
	fswatch --verbose -0 $(publicdist)/* | xargs -0 -n 1 -I {} cp {} $(public)/core/

watch-css-copy-dist-sri:
	fswatch --verbose -0 $(publicdist)/main.min.css | xargs -0 -I {} python ./scripts/sri_resource.py "$(publicdist)/main.min.css"

watch-css:
	parallel --ungroup ::: "make watch-build-main-css" "make watch-css-copy-dist" "make watch-css-copy-dist-sri"

build-js:
	cat $(apppath)/js/*.js | $(terser) --compress --mangle --output $(publicdist)/main.min.js
	python ./scripts/sri_resource.py "$(publicdist)/main.min.js"

watch-build-js-app:
	cat $(apppath)/js/*.js | $(terser) --beautify --output $(publicdist)/main.min.js
	cp $(publicdist)/main.min.js $(public)/core/

watch-js-app:
	fswatch --verbose -0 $(apppath)/js/*.js | xargs -0 -I {} make watch-build-js-app

watch-js-app-sri:
	fswatch --verbose -0 $(publicdist)/main.min.js | xargs -0 -I {} python ./scripts/sri_resource.py "$(publicdist)/main.min.js"

watch-js:
	parallel --ungroup ::: "make watch-js-app" "make watch-js-app-sri"

build-django-collectstatic:
	python manage.py collectstatic --noinput

build-all-sri:
	find $(public)/core/*.css -exec python ./scripts/sri_resource.py {} \;
	find $(public)/core/*.js -exec python ./scripts/sri_resource.py {} \;

build-static:
	make build-css build-js build-django-collectstatic build-all-sri

##################################################
# POSTGRES & DJANGO DB
##################################################

migrate:
	python manage.py makemigrations progress_core
	python manage.py migrate

dbload:
	python manage.py loaddata data/all.json

dbload-model:
	python manage.py loaddata data/$(model).json

dbload-fixtures:
	ls progressinator/core/fixtures/ | xargs -I {} python manage.py loaddata {}

dbdump:
	python manage.py dumpdata --indent=2 -o data/all.json progress_core

dbdump-model:
	python manage.py dumpdata --indent=2 -o data/$(model).json progress_core.$(model)

dbdump-fixture:
	python manage.py dumpdata --indent=2 -o $(apppath)/core/fixtures/$(model).json progress_core.$(model)

django-super-user:
	python manage.py createsuperuser

##################################################
# HEROKU
##################################################

heroku-setup:
	# https://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html
	heroku create learn-the-web-progress

	heroku git:remote -a learn-the-web-progress

	heroku buildpacks:add heroku/python
	heroku buildpacks:add heroku/nodejs

	heroku addons:create --wait heroku-postgresql:hobby-dev
	heroku pg:backups schedule --at '02:00 America/Toronto' DATABASE_URL

	heroku config:set PYTHONHASHSEED=random
	heroku config:set PYTHONIOENCODING=utf8
	heroku config:set WEB_CONCURRENCY=4
	heroku config:set DISABLE_COLLECTSTATIC=1
	heroku config:set DJANGO_DEBUG=False
	heroku config:set DJANGO_SETTINGS_MODULE=config.settings.prod
	heroku config:set DJANGO_SECRET_KEY="$(openssl rand -base64 64)"
	heroku config:set DJANGO_ALLOWED_HOST=progress.learntheweb.courses
	# heroku config:set SENTRY_DSN=

	git push heroku

	heroku ps:resize web=hobby
	heroku certs:auto:enable
	heroku domains:add progress.learntheweb.courses

heroku-migrate:
	heroku run python manage.py migrate

heroku-django-super-user:
	heroku run python manage.py createsuperuser

heroku-db-push:
	heroku pg:push postgres://localhost:5432/progressinator DATABASE_URL --app learn-the-web-progress

heroku-db-pull:
	heroku pg:pull DATABASE_URL postgres://localhost:5432/progressinator --app learn-the-web-progress

heroku-rebuild:
	git commit --allow-empty -m 'empty commit' && git push heroku master

##################################################
# FUN
##################################################

cloc:
	cloc --exclude-dir=node_modules,public,public-dist,__pycache__,data --exclude-ext=lock,json .
