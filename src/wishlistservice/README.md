Commands to run this monstrosity locally:

minikube start --cpus=4 --memory 4096 --disk-size 32g

skaffold dev

kubectl port-forward deployment/wishlistservice 50052:50052

Test Service Health:
grpcurl -plaintext -import-path . -proto protos/grpc/health/v1/health.proto -d '{"service": "wishlistservice"}' localhost:50052 grpc.health.v1.Health/Check

Test Add Item Endpoint:
grpcurl -plaintext -import-path protos -proto demo.proto -d '{"user_id": "user124", "name": "wishlist2", "item": {"product_id": "product456"}}' localhost:50052 hipstershop.WishlistService/AddItem