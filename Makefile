SENTRY_AUTH_TOKEN=<your_auth_token>
SENTRY_ORG=<YOUR ORG NAME>
SENTRY_PROJECT=<YOUR PROJECT NAME>
VERSION=`sentry-cli releases propose-version`

deploy: install create_release associate_commits run_django

install:
	pip install -r ./requirements.txt

create_release:
	sentry-cli releases -o $(SENTRY_ORG) new -p $(SENTRY_PROJECT) $(VERSION)

associate_commits:
	sentry-cli releases -o $(SENTRY_ORG) -p $(SENTRY_PROJECT) \
		set-commits $(VERSION) --auto

run_django:
	VERSION=$(VERSION) python manage.py runserver
