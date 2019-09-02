# drone-simulation

An app to simulate time saved when sending a drone flying with
an [AED](https://en.wikipedia.org/wiki/Automated_external_defibrillator) to an
OHCA (Out of Hospital Cardiac Arrest).

## Installation

Install all requirements using `pip`:

```sh
pip install .
```

## Run

To run the app, just start the Dash server:

```sh
python index.py
```

And then you can access it at the address http://127.0.0.1:8050/apps/app1.

## Docker

If you don't want to pollute your main OS, you can also build and run inside a docker container:

```sh
docker-compose up -d
```

## Check styles

Run the linters in your editor (pycodestye and pylint), or directly in a Docker container.

```sh
docker-compose build
```
