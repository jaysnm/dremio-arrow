FROM nginx:alpine

RUN apk add openssh git --no-cache --update && \
    mkdir -p /srv/www/doc ~/.ssh && \
    echo '-----BEGIN OPENSSH PRIVATE KEY-----' >> ~/.ssh/id_ed25519 && \
	echo 'b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW' >> ~/.ssh/id_ed25519 && \
	echo 'QyNTUxOQAAACB6mnJeRY0PfZdDfKGQrdCupfKvl8yLqW0gRYj+bn6IBwAAAJi0o7MytKOz' >> ~/.ssh/id_ed25519 && \
	echo 'MgAAAAtzc2gtZWQyNTUxOQAAACB6mnJeRY0PfZdDfKGQrdCupfKvl8yLqW0gRYj+bn6IBw' >> ~/.ssh/id_ed25519 && \
	echo 'AAAEC1Nvx8tuUVv7XWJzWtf4vGzFA6H7H1Bu7lJI13H5/u+3qacl5FjQ99l0N8oZCt0K6l' >> ~/.ssh/id_ed25519 && \
	echo '8q+XzIupbSBFiP5ufogHAAAAEmRhc2hib2FyZHNAc3BhY2lhbAECAw==' >> ~/.ssh/id_ed25519 && \
	echo '-----END OPENSSH PRIVATE KEY-----' >> ~/.ssh/id_ed25519 && \
	chmod 0600 ~/.ssh/id_ed25519  && \
	ssh-keyscan github.com >> ~/.ssh/known_hosts && \
	git clone --depth 1  git@github.com:gsl-icraf/dremio-arrow.git --branch gh-pages --single-branch /srv/www/docs

COPY docs-site.conf /etc/nginx/conf.d/default.conf
