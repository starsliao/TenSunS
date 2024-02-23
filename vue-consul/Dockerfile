FROM node:14-alpine AS builder
ADD . /vue
WORKDIR /vue
RUN npm install --registry=https://registry.npmmirror.com && npm run build:prod

FROM nginx:1.24.0-alpine
WORKDIR /www
COPY --from=builder /vue/http-ops.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /vue/dist dist/
