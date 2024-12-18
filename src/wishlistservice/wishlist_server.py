from concurrent import futures
import time

import grpc
import redis
from redis import ConnectionPool

from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
logger = getJSONLogger('wishlistservice')

def handle_redis_connection_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        except redis.ConnectionError:
            context.set_details('Failed to connect to Redis')
            context.set_code(grpc.StatusCode.INTERNAL)
            return demo_pb2.Empty()
    return wrapper

def check_all_wishlist_keys_exist(func):
    def wrapper(self, request, context):
        for field, value in request.ListFields():
            attributeDescriptor = field.name
            if "name" in attributeDescriptor:
                wishlistKey = self.get_redis_key(request, attributeDescriptor)
                if not self.redisInstance.exists(wishlistKey):
                    context.set_details(f'Wishlist with key "{wishlistKey}" does not exist')
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return demo_pb2.Empty()
        return func(self, request, context)
    return wrapper

class WishlistService(demo_pb2_grpc.WishlistServiceServicer):
    def __init__(self):
        pool = ConnectionPool(host='redis-cart', port=6379, decode_responses=True)
        self.redisInstance = redis.Redis(connection_pool=pool)
    
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)
  
    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)
        
    @handle_redis_connection_error
    def AddWishlist(self, request, context):
        wishlistKey = self.get_redis_key(request)
        # push a placeholder since redis keys need to have value
        self.redisInstance.sadd(wishlistKey, "empty")
        return demo_pb2.Empty()

    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def AddItem(self, request, context):
        wishlistKey = self.get_redis_key(request)
        self.redisInstance.sadd(wishlistKey, request.item.product_id)
        return demo_pb2.Empty()
        
    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def GetWishlist(self, request, context):
        wishlistKey = self.get_redis_key(request)
        wishlistItems = self.get_wishlist_items(wishlistKey, context)
        wishlist = demo_pb2.Wishlist(
            name=request.name,
            items=wishlistItems)
        response = demo_pb2.GetWishlistResponse(wishlist=wishlist)
        return response
        
    @handle_redis_connection_error
    def GetAllWishlists(self, request, context):
        user_id = request.user_id
        # get all wishlist keys for the user
        keys_pattern = f"{user_id}:*"
        wishlist_keys = self.redisInstance.keys(keys_pattern)
    
        # retrieve all wishlists of the user from redis
        wishlists = []
        for key in wishlist_keys:
            wishlistItems = self.get_wishlist_items(key, context)
            wishlist_name = key.split(":", 1)[1]
            wishlist = demo_pb2.Wishlist(
                name=wishlist_name,
                items=wishlistItems
        )
            wishlists.append(wishlist)

        response = demo_pb2.GetAllWishlistsResponse(
            wishlists=wishlists
        )
        return response
    
    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def RemoveItem(self, request, context):
        wishlistKey = self.get_redis_key(request)
        self.redisInstance.srem(wishlistKey, request.item.product_id)
        return demo_pb2.Empty()
    
    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def EmptyWishlist(self, request, context):
        wishlistKey = self.get_redis_key(request)
        wishlistItems = self.redisInstance.smembers(wishlistKey)
        for item in wishlistItems:
            if item != "empty":
                self.redisInstance.srem(wishlistKey, item)
        return demo_pb2.Empty()
    
    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def DeleteWishlist(self, request, context):
        wishlistKey = self.get_redis_key(request)
        self.redisInstance.delete(wishlistKey)
        return demo_pb2.Empty()
    
    @handle_redis_connection_error
    # TODO make sure to only check that the old key exists
    def RenameWishlist(self, request, context):
        old_wishlistKey = self.get_redis_key(request, 'old_name')
        new_wishlistKey = self.get_redis_key(request, 'new_name')
        self.redisInstance.rename(old_wishlistKey, new_wishlistKey)
        return demo_pb2.Empty()
    
    @handle_redis_connection_error
    @check_all_wishlist_keys_exist
    def MoveWishlistItem(self, request, context):
        source_wishlistKey = self.get_redis_key(request, 'source_wishlist_name')
        target_wishlistKey = self.get_redis_key(request, 'target_wishlist_name')
        self.redisInstance.smove(source_wishlistKey, target_wishlistKey, request.item.product_id)
        return demo_pb2.Empty()
    
    # helper method to get all items in a wishlist in grpc format
    @handle_redis_connection_error
    def get_wishlist_items(self, wishlistKey, context):
        wishlistItems = self.redisInstance.smembers(wishlistKey)
        # filter out the placeholder empty item
        filtered_items = [item for item in wishlistItems if item != "empty"]
        return [demo_pb2.WishlistItem(product_id=item) for item in filtered_items]
    
    # helper method to get the redis key for a wishlist in the proper format
    def get_redis_key(self, request, name_attr='name'):
        user_id = request.user_id
        name = getattr(request, name_attr)
        return f"{user_id}:{name}"
        
def serve():
    logger.info("Initializing wishlistservice")
    
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