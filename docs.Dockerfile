FROM nginx:alpine

RUN apk add openssh git --no-cache --update && \
    mkdir -p /srv/www/doc ~/.ssh && \
    git clone --depth 1  https://github.com/jaysnm/dremio-arrow.git --branch gh-pages --single-branch /srv/www/docs

COPY docs-site.conf /etc/nginx/conf.d/default.conf
