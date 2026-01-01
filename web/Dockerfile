# ---- Build stage ----
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# 👇 accept build arg
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ---- Production stage ----
FROM nginx:alpine

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config (optional but recommended)
 COPY nginx.conf /etc/nginx/conf.d/default.conf

 # Make nginx writable paths accessible for non-root
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx

# Run as non-root user provided by the image
USER nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
