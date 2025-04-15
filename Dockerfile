
#######################
#        BASE         #
#######################


FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	POETRY_VERSION=1.8.1 \
	POETRY_CACHE_DIR=/tmp/poetry_cache \
	WORKDIR_PATH=/usr/src/app/backend

WORKDIR $WORKDIR_PATH



#######################
#        BUILD        #
#######################


FROM base AS build

COPY pyproject.toml poetry.lock .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
	pip install --no-cache-dir "poetry==$POETRY_VERSION" \
	&& poetry config virtualenvs.in-project true \
	&& pip install --upgrade pip \
	&& poetry install --no-root

COPY . .


#######################
#       RUNTIME       #
#######################


FROM base AS runtime

ENV PATH=$WORKDIR_PATH/.venv/Scripts:$WORKDIR_PATH/.venv/bin:$PATH \
	VIRTUAL_ENV=$WORKDIR_PATH/.venv

COPY --from=build --chown=1000:1000 --chmod=500 $WORKDIR_PATH .

RUN adduser app -h /app -u 1000 -G 1000 -DH \
    && chown 1000:1000 .

USER 1000
