FROM rust:alpine as dev

WORKDIR /app

RUN apk add musl-dev

RUN echo "fn main() {}" >> dummy.rs

COPY Cargo.toml .

RUN sed -i 's#src/main.rs#dummy.rs#' Cargo.toml

RUN cargo build

RUN sed -i 's#dummy.rs#src/main.rs#' Cargo.toml

COPY . .

RUN cargo build

CMD cargo run

FROM dev as release-builder

RUN cargo build --release

FROM alpine:latest as runner

COPY --from=release-builder /app/target/release/app .

CMD ./app
