#!/bin/bash
set -e

GITHUB_USER="erfanalizada"
IMAGE_PREFIX="ghcr.io/$GITHUB_USER/talentlink_minikube"

declare -A SERVICES=(
  ["auth-service"]="backend/auth-service"
  ["cv-service"]="backend/cv-service"
  ["job-service"]="backend/job-service"
  # ["keycloak"]="k8s/keycloak"
  ["matching-service"]="backend/matching-service"
  ["notification-service"]="backend/notification-service"
  ["user-service"]="backend/user-service"
  ["frontend"]="frontend"
)

for SERVICE in "${!SERVICES[@]}"; do
    DIR="${SERVICES[$SERVICE]}"
    IMAGE="$IMAGE_PREFIX-$SERVICE:latest"

    echo "============================================"
    echo " Building $SERVICE -> $IMAGE"
    echo "============================================"

    docker build -t "$IMAGE" "$DIR"
    echo " Pushing $IMAGE"
    docker push "$IMAGE"

    echo " Done: $IMAGE"
    echo
done

echo "🚀 All images built & pushed!"
