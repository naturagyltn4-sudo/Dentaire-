FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl nginx unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY dentiste_source.zip /build/dentiste_source.zip
RUN unzip -q /build/dentiste_source.zip \
    && mv /build/dentiste_enterprise_v4/api-server /app \
    && mv /build/dentiste_enterprise_v4/public-gateway /gateway \
    && rm -rf /build/dentiste_enterprise_v4 /build/dentiste_source.zip

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY public-nginx.conf.template /etc/nginx/templates/public.conf.template
COPY start-public.sh /usr/local/bin/start-public.sh
COPY seed_public_demo.py /app/railway_seed_public_demo.py
RUN chmod 755 /usr/local/bin/start-public.sh \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

EXPOSE 8000
CMD ["/usr/local/bin/start-public.sh"]
