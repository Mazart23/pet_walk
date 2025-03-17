FROM postgres:15-alpine

RUN apk add --no-cache postgis

ENV POSTGRES_USER petwalk
ENV POSTGRES_PASSWORD petwalk_password
ENV POSTGRES_DB petwalk_db

EXPOSE 5432

COPY init.sql /docker-entrypoint-initdb.d/

CMD ["postgres"]