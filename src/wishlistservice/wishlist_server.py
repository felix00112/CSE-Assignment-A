from concurrent import futures
import time

import grpc
import redis

from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
logger = getJSONLogger('wishlistservice')

class WishlistService(demo_pb2_grpc.WishlistServiceServicer):
    def get_redis_key_from(self, request):
        return request.user_id + ":" + request.name
    
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)
  
    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)
        
    def AddWishlist(self, request, context):
        return demo_pb2.Empty()

    def AddItem(self, request, context):
        try:
            redisInstance = redis.Redis(host='redis-cart', port=6379, decode_responses=True)
            wishlistKey = self.get_redis_key_from(request)
            redisInstance.rpush(wishlistKey, request.item.product_id)
            response = redisInstance.get(wishlistKey)
            return demo_pb2_grpc.WishlistResponse(message=f"Added the following: {response}")
        except redis.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Failed to connect to Redis')
            return demo_pb2_grpc.WishlistResponse(message="failed to connect to Redis")
        
    def GetWishlist(self, request, context):
        try:
            redisInstance = redis.Redis(host='redis-cart', port=6379, decode_responses=True)
            wishlistKey = self.get_redis_key_from(request)
            response = redisInstance.get(wishlistKey)
            return demo_pb2_grpc.WishlistResponse(message=f"Added the following: {response}")
        except redis.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Failed to connect to Redis')
            return demo_pb2_grpc.WishlistResponse(message="failed to connect to Redis")

    def EmptyWishlist(self, request, context):
        try:
            redisInstance = redis.Redis(host='redis-cart', port=6379, decode_responses=True)
            wishlistKey = self.get_redis_key_from(request)
            for i in range(0, redisInstance.llen(wishlistKey)):
                redisInstance.lpop(wishlistKey)
            return demo_pb2.Empty()
        except redis.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Failed to connect to Redis')
            return demo_pb2_grpc.WishlistResponse(message="failed to connect to Redis")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = WishlistService()
    demo_pb2_grpc.add_WishlistServiceServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()