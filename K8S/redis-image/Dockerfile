#Images that we are using
FROM alpine
# cmd install commands

RUN apk add --update gcc && \   
    apk add --update redis
#what to execute when the container run
CMD ["redis-server"]