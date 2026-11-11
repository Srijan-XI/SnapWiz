FROM node:22-bookworm AS node

FROM rust:1.90-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=always \
    npm_config_update_notifier=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        file \
        libayatana-appindicator3-dev \
        libgtk-3-dev \
        librsvg2-dev \
        libwebkit2gtk-4.1-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node /usr/local/ /usr/local/

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build \
    && cargo check --manifest-path src-tauri/Cargo.toml

CMD ["npm", "run", "tauri", "build"]
