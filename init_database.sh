#! /usr/bin/env sh

python3 manage.py recreate_db
python3 manage.py setup_dev
python3 manage.py add_fake_data