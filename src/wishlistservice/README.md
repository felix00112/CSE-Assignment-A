# CSE Assignment

For our assignment we have implemented a wishlist into the Google microservices demo project shop. This directory contains the microservice code which is written in python as well as the tests and other files necessary for building etc. . The wishlist data is persistet in the already existing Redis instance. Most of the logic in `wishlist_server` is pretty straightforward as its mostly generating redis keys from the incoming requests and then interacting with Redis. The microservice communicates only communicates with the frontend. This is done with grpc. We added the endpoints, request structure etc. of the wishlist microservice to the existing `demo.protos` file. The names of the dependencies are stored in the `requirements.txt` file so the Dockerfile isn't as crowded. Dependencies are mainly for testing and code coverage.

## Core functionality

Enables the user to create wishlists with a name. Once a wishlist has been created, the user can add products to it. A user can view their wishlists and the products they contain on the wishlist page. Products can be removed from wishlists, moved to other wishlists and be added to the shopping cart. Finally, users can empty and remove wishlists as well as rename them.

## How to run the project locally

1. Install Docker
2. Install Minikube
3. Install Skaffold
4. Start minikube:

`minikube start --cpus=4 --memory 4096 --disk-size 32g`

5. Start the project locally:

`skaffold dev`

## Commands for testing the wishlist microservice locally

1. Expose port 50052 so it can be accessed from outside the cluster:

`kubectl port-forward deployment/wishlistservice 50052:50052`

2. If you intend on using the following commands to test the service locally you need to install grpcurl via Homebrew, Chocolatey or whichever way you prefer e.g

`homebrew install grpcurl`

Test Service Health:

`grpcurl -plaintext -import-path . -proto protos/grpc/health/v1/health.proto -d '{"service": "wishlistservice"}' localhost:50052 grpc.health.v1.Health/Check`

Test Add Item Endpoint:

`grpcurl -plaintext -import-path protos -proto demo.proto -d '{"user_id": "1234", "name": "defaultwishlist", "item": {"product_id": "6789"}}' localhost:50052 hipstershop.WishlistService/AddItem`

## Commands for testing with Pytest
Change directory to `src/wishlistservice`
- Running all Unit Test written for the Wishlist Service:
  `pytest`
- Getting Code Coverage in Terminal:
    `pytest --cov=src --cov-report=term-missing`
- Creating html Coverage Report:
  `pytest --cov=src --cov-report=html`

## How to recompile the Protos file on macOS

1. go to `<replace with path to repository root>/src/wishlistservice`

### If you don't have a python virtual environment with dependencies yet

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
