web: gunicorn manage:app
worker: sh -c "python -u manage.py run_worker & python -u manage.py run_scheduler"
