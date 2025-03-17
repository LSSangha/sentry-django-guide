## Table of Contents
- [Installing Dependencies](#installing-dependencies)
- [Configuring Sentry](#configuring-sentry)
- [Running The Demo](#running-the-demo)
- [Cleaning Up](#cleaning-up)


## Installing Dependencies
This project uses Django 2.2 that requires Python 3

1. Install Python:
```bash
brew install python
```

2. Create virtual environment
```bash
python -m venv .venv
```

3. Activate virtual environment
```bash
source .venv/bin/activate
```

3. Install Sentry's command line tool to use release tracking and Github integration for commit data:
```bash
python -m pip install "sentry-cli"
```


## Configuring Sentry

The Sentry client library requires a [DSN generated from Sentry](https://docs.sentry.io/quickstart/#configure-the-dsn) which specifies the project events will be sent to. Add the import and configuration code to `settings.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://yourdsn@sentry.io/1234567"
)
```

Further details on configuring Sentry [here](https://docs.sentry.io/platforms/python/django/).


## Running The Demo

Run `deploy` target in `Makefile`. This will install relevant python libraries and run Django server.

```bash
make deploy
```


### Demo Specs

This demo uses Django's rest-framework package and offers 3 API endpoints:
1. http://localhost:8000/handled - generates a runtime error explicitly reported to Sentry though the SDK's `captureException`
2. http://localhost:8000/unhandled - generates an unhandled runtime error reported
3. http://localhost:8000/checkout - can be used with the [Sentry REACT demo store front demo](https://github.com/sentry-demos/react)
    This endpoint can also be used with directly through the Django REST Framework web UI. To generate an error paste the following JSON payload in the POST payload text area:


```json
    {
    "cart": [
        {"id": "wrench", "name": "Wrench", "price": 500},
        {"id": "wrench", "name": "Wrench", "price": 500}
    ],
    "email": "user@email.com"
    }
```

![Alt Text](django_demo_setup.gif)


## Cleaning Up

Pressing Ctrl-C once in each terminal window should stop Django's development server.

To deactivate the virtual environment:
```bash
deactivate
```

To remove the virtual environment: 
```bash
rm -rf .venv/
```
