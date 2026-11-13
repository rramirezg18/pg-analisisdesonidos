#!/usr/bin/env bash
# Construye y publica las imágenes que usa k8s/kustomization.yaml.
#   ./k8s/build-push.sh 1.0.0
# Requisito (una vez): echo <TOKEN> | docker login ghcr.io -u rramirezg18 --password-stdin
#   (token de GitHub con permiso write:packages). Luego marca los paquetes como
#   "Public" en GitHub > Packages, o crea un imagePullSecret.
set -euo pipefail

TAG="${1:-1.0.0}"
REGISTRY="${REGISTRY:-ghcr.io/rramirezg18}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"

# El clúster k3s corre en linux/amd64.
docker build --platform linux/amd64 -t "$REGISTRY/motorscan-backend:$TAG" "$RAIZ/backend"
docker build --platform linux/amd64 -t "$REGISTRY/motorscan-frontend:$TAG" "$RAIZ/frontend"

docker push "$REGISTRY/motorscan-backend:$TAG"
docker push "$REGISTRY/motorscan-frontend:$TAG"

echo "Listo. Si el tag no es el de kustomization.yaml, cámbialo en 'images:' y aplica:"
echo "  kubectl apply -k k8s/"
