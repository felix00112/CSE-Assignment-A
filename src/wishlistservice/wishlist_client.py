import grpc
import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
logger = getJSONLogger('wishlistservice-server')

if __name__ == "__main__":
    channel = grpc.insecure_channel('[::]:50052')
    stub = demo_pb2_grpc.WishlistServiceStub(channel)