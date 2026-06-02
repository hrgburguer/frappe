FROM frappe/build:v16.20.0 AS builder

USER frappe

RUN bench init \
      --verbose \
      --no-backups \
      --no-procfile \
      --skip-redis-config-generation \
      --frappe-path=https://github.com/frappe/frappe \
      --frappe-branch=v16.19.0 \
      /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

RUN echo '{"socketio_port": 9000}' > sites/common_site_config.json

RUN corepack prepare pnpm@10 --activate

RUN bench get-app --resolve-deps --branch v16.19.1 erpnext
RUN bench get-app --branch v16.7.1 hrms
RUN bench get-app --resolve-deps --branch v2.54.2 lms
RUN bench get-app --resolve-deps --branch v3.9.11 insights
RUN bench get-app --resolve-deps --branch v1.72.0 crm
RUN bench get-app --resolve-deps --branch v1.24.1 helpdesk
RUN bench get-app --branch v1.5.4 lending
RUN bench get-app --resolve-deps gameplan
RUN bench get-app --resolve-deps --branch v0.3.0 drive
RUN bench get-app --resolve-deps --skip-assets --branch python-314 press

RUN find apps -mindepth 1 -path "*/.git" | xargs rm -fr

FROM frappe/base:v16.18.3 AS backend

USER frappe

COPY --from=builder --chown=frappe:frappe /home/frappe/frappe-bench /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

VOLUME [ \
  "/home/frappe/frappe-bench/sites", \
  "/home/frappe/frappe-bench/sites/assets", \
  "/home/frappe/frappe-bench/logs" \
]

CMD [ \
  "/home/frappe/frappe-bench/env/bin/gunicorn", \
  "--chdir=/home/frappe/frappe-bench/sites", \
  "--bind=0.0.0.0:8000", \
  "--threads=4", \
  "--workers=2", \
  "--worker-class=gthread", \
  "--worker-tmp-dir=/dev/shm", \
  "--timeout=120", \
  "--preload", \
  "frappe.app:application" \
]