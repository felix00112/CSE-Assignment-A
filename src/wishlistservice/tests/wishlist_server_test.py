import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import Mock, patch
import demo_pb2
from wishlist_server import WishlistService


@pytest.fixture
def wishlist_server():
    server = WishlistService()
    server.redisInstance = Mock()
    return server

@pytest.fixture
def mock_request():
    request = Mock()
    request.user_id = "1"
    return request

@pytest.fixture
def mock_context():
    return Mock()


def test_getAllWishlists(wishlist_server, mock_request, mock_context):
    # Arrange
    redis_keys = ["1:books", "1:electronics"]
    wishlist_items1 = [demo_pb2.WishlistItem(product_id="1")]
    wishlist_items2 = [demo_pb2.WishlistItem(product_id="2")]

    wishlist_server.redisInstance.keys.return_value = redis_keys

    # Mock the get_wishlist_items method
    wishlist_server.get_wishlist_items = Mock(side_effect=[wishlist_items1, wishlist_items2])

    # Act
    response = wishlist_server.GetAllWishlists(mock_request, mock_context)

    # Assert
    assert len(response.wishlists) == 2

    assert response.wishlists[0].name == "books"
    assert response.wishlists[0].items == wishlist_items1

    assert response.wishlists[1].name == "electronics"
    assert response.wishlists[1].items == wishlist_items2

    wishlist_server.redisInstance.keys.assert_called_once_with("1:*")
    wishlist_server.get_wishlist_items.assert_any_call("1:books", mock_context)
    wishlist_server.get_wishlist_items.assert_any_call("1:electronics", mock_context)


    if __name__ == "__main__":
        pytest.main()