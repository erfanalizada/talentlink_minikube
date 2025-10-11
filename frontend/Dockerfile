# ===============================
# Stage 1 — Build Flutter Web App
# ===============================
FROM ghcr.io/cirruslabs/flutter:latest AS build

WORKDIR /app

# Copy everything in the current folder (includes talentlink_frontend)
COPY . .

# Move into the Flutter app directory
WORKDIR /app/talentlink_frontend

# Get dependencies and build
RUN flutter pub get
RUN flutter build web --release

# ===============================
# Stage 2 — Serve via NGINX
# ===============================
FROM nginx:alpine

# Copy NGINX config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built Flutter web app
COPY --from=build /app/talentlink_frontend/build/web /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
