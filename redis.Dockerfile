FROM redis:8.0-rc1-alpine3.21
RUN mkdir "/configs"
COPY configs/redis.conf /configs/redis.conf
COPY configs/users.acl /configs/users.acl
CMD [ "redis-server", "/configs/redis.conf" ]

