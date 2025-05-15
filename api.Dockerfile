FROM python:3.12-alpine3.21
WORKDIR /code
RUN mkdir "/code/configs"

RUN apk update && apk upgrade
RUN apk add curl

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app
COPY ./configs/api.yaml /code/configs/api.yaml

CMD ["fastapi", "run", "app/oidc_provider.py", "--host", "0.0.0.0", "--port", "8000"]