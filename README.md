# SMS APIs

## Installation requirements
- pip install -r requirements.txt 
## Create a symmetric key for JWT encryption
- Open terminal
- `python`
- `from jwcrypto import jwk`
- `key = jwk.JWK(generate='oct', size=256)`
- `key.export()`
- Copy value and use as `JWT_KEY`

## Quick Start 🚀
- Open terminal in project root
- Run server: `command: sh -c "sleep 3s"`

## Docker Steps
- Build docker image.
- `docker build -t sms-api:latest .`
- Run container with network access.
- `docker run -d -p 8000:8000 sms-api`
- View container id.
- `docker ps`
- Stop container.
- `docker stop container_id`

## Data Migrations
- To create new migrations from model changes
- `alembic revision --autogenerate -m "Comment"`
- To update database with new changes
- `alembic upgrade head`

## SQL server
- Remove `only_full_group_by` from `sql_mode` variable.
