FROM public.ecr.aws/nginx/nginx:perl

COPY index.html /usr/share/nginx/html
RUN chmod +r /usr/share/nginx/html/index.html

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;"]