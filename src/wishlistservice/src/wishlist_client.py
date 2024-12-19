import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc
import demo_pb2
import demo_pb2_grpc

def setup_grpc_client():
    channel = grpc.insecure_channel('[::]:50052')
    stub = demo_pb2_grpc.WishlistServiceStub(channel)
    return stub

if __name__ == "__main__":
    setup_grpc_client()
