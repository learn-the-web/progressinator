postcss := ./node_modules/postcss-cli/bin/postcss --config ./config/postcss.config.js
uglifyjs := ./node_modules/uglify-js/bin/uglifyjs

apppath := ./progressinator
publicdist := ./public-dist
public := ./public

.PHONY: build-docker start stop watch-css build-css watch-build-css watch-css-copy-dist build-js watch-js watch-build-js install migrate debug django-super-user docker-shell docker-clean

build-docker:
	sudo docker-compose build

start:
	sudo docker-compose up

stop:
	sudo docker container stop progressinator_django_1 progressinator_postgres_1

copy-courses:
	cp /db/learn-the-web/www/_site/courses/web-dev-1/course.json ./config/courses/web-dev-1.json
	cp /db/learn-the-web/www/_site/courses/web-dev-2/course.json ./config/courses/web-dev-2.json
	cp /db/learn-the-web/www/_site/courses/web-dev-3/course.json ./config/courses/web-dev-3.json
	cp /db/learn-the-web/www/_site/courses/web-dev-4/course.json ./config/courses/web-dev-4.json
	cp /db/learn-the-web/www/_site/courses/web-dev-5/course.json ./config/courses/web-dev-5.json
	cp /db/learn-the-web/www/_site/courses/web-dev-6/course.json ./config/courses/web-dev-6.json
	cp /db/learn-the-web/www/_site/courses/javascript/course.json ./config/courses/javascript.json

build-courses:
	pipenv run python ./scripts/compile-courses.py

build-css:
	$(postcss) $(apppath)/css/main.css --output $(publicdist)/main.min.css

watch-css:
	parallel --ungroup ::: "make watch-build-css" "make watch-css-copy-dist"

watch-build-css:
	$(postcss) $(apppath)/css/main.css --output $(publicdist)/main.min.css --watch

watch-css-copy-dist:
	fswatch --verbose -0 $(publicdist)/* | xargs -0 -n 1 -I {} cp {} $(public)/core/

build-js:
	cat $(apppath)/js/*.js | $(uglifyjs) --compress --mangle --output $(publicdist)/main.min.js

watch-js:
	fswatch --verbose -0 $(apppath)/js/*.js | xargs -0 -n 1 make watch-build-js

watch-build-js:
	cat $(apppath)/js/*.js | $(uglifyjs) --beautify --output $(publicdist)/main.min.js
	cp $(publicdist)/main.min.js $(public)/core/

install:
	brew install node terraform fswatch yarn parallel
	brew cask install docker
	yarn install

migrate:
	sudo docker-compose exec django python manage.py makemigrations progress_core
	sudo docker-compose exec django python manage.py migrate

dbload:
	sudo docker-compose exec django python manage.py loaddata data/all.json

dbloadmodel:
	sudo docker-compose exec django python manage.py loaddata data/$(MODEL).json

dbdump:
	sudo docker-compose exec django python manage.py dumpdata --indent=2 -o data/all.json progress_core

dbdumpmodel:
	sudo docker-compose exec django python manage.py dumpdata --indent=2 -o data/$(MODEL).json progress_core.$(MODEL)

django-super-user:
	sudo docker-compose exec django python manage.py createsuperuser

debug:
	# https://blog.lucasferreira.org/howto/2017/06/03/running-pdb-with-docker-and-gunicorn.html
	# Ctrl P + Ctrl Q
	sudo docker attach progressinator_django_1

docker-shell:
	sudo docker exec -it progressinator_django_1 bash

docker-clean:
	sudo docker system prune -f
	sudo docker system prune -f --volumes

heroku:
	# https://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html
	heroku create --buildpack https://github.com/heroku/heroku-buildpack-python

	heroku buildpacks:add --index 1 heroku/nodejs
	heroku buildpacks:add --index 2 heroku/python

	heroku addons:create heroku-postgresql:hobby-dev
	heroku pg:promote DATABASE_URL

	heroku config:set PYTHONHASHSEED=random
	heroku config:set WEB_CONCURRENCY=4
	heroku config:set DJANGO_DEBUG=False
	heroku config:set DJANGO_SETTINGS_MODULE=config.settings.prod
	heroku config:set DJANGO_SECRET_KEY="$(openssl rand -base64 64)"
	heroku config:set DJANGO_ADMIN_URL="$(openssl rand -base64 4096 | tr -dc 'A-HJ-NP-Za-km-z2-9' | head -c 32)/"

heroku-migrate:
	heroku run python manage.py migrate

heroku-django-super-user:
	heroku run python manage.py createsuperuser

heroku-push-local-db:
	heroku pg:push postgres://progressinator@localhost:5432/progressinator postgresql-fluffy-48259 --app learn-the-web-progress

heroku-schedule-db-backup:
	# https://devcenter.heroku.com/articles/heroku-postgres-backups
	heroku pg:backups:schedule DATABASE_URL --at '02:00 America/Toronto' --app learn-the-web-progress
