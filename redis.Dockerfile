FROM redis:8.0-rc1-alpine3.21
RUN mkdir "/usr/local/etc/redis"
COPY configs/redis.conf /usr/local/etc/redis/redis.conf
COPY configs/users.acl /usr/local/etc/redis/users.acl
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]

