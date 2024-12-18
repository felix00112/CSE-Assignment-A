## Commands to run the project locally:

Start minikube:

`minikube start --cpus=4 --memory 4096 --disk-size 32g`

Start the shop locally:

`skaffold dev`

 ## Commands for testing the backend service locally:

Expose port 50052 so it can be accessed from outside the cluster:

`kubectl port-forward deployment/wishlistservice 50052:50052`

Test Service Health:

`grpcurl -plaintext -import-path . -proto protos/grpc/health/v1/health.proto -d '{"service": "wishlistservice"}' localhost:50052 grpc.health.v1.Health/Check`

Test Add Item Endpoint:

`grpcurl -plaintext -import-path protos -proto demo.proto -d '{"user_id": "1234", "name": "defaultwishlist", "item": {"product_id": "6789"}}' localhost:50052 hipstershop.WishlistService/AddItem`

## Recompile Protos file on macOS

1. go to `<replace with path to repository root>/src/wishlistservice`

### If you don't have a virtual environment with dependencies yet

2. Create a virtual environment 

`python3 -m venv venv`

3. Enter the virtual environment

`source venv/bin/activate`

4. Install dependencies

`pip install grpcio-tools`

5. Compile protos file

`./genproto.sh`

### If you already have a venv with dependencies

1. Enter the virtual environment

`source venv/bin/activate`

2. Compile protos file

`./genproto.sh`