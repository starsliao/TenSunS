FROM node:14-alpine AS builder
ADD . /vue
WORKDIR /vue
RUN npm install --registry=https://registry.npm.taobao.org && npm run build:prod

FROM nginx:stable-alpine
WORKDIR /www
COPY --from=builder /vue/http-ops.conf /etc/nginx/conf.d/
COPY --from=builder /vue/dist dist/
