import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import Mock, patch, MagicMock, call, create_autospec
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
    return request


@pytest.fixture
def mock_context():
    return MagicMock()


# Unit Test for helper methods


def test_get_redis_key(wishlist_server):
    # Arrange
    request = MagicMock()
    request.user_id = "1"
    request.name = "books"

    # Act
    result = wishlist_server.get_redis_key(request)

    # Assert
    assert result == "1:books"


def test_get_wishlist_items(wishlist_server, mock_context):
    # Arrange
    wishlistKey = "user:1:wishlist:books"

    # mock for redids (contains multiple products + "empty")
    wishlist_server.redisInstance.smembers = MagicMock(
        return_value={"item1", "item2", "empty"}
    )

    # Act
    response = wishlist_server.get_wishlist_items(wishlistKey, mock_context)

    # Assert
    # Ensure that smembers is called with correct key
    wishlist_server.redisInstance.smembers.assert_called_once_with(wishlistKey)

    expected_items = {"item1", "item2"}

    returned_items = {item.product_id for item in response}

    # Check that "empty" is filtered and response-items are in the correct format
    assert len(response) == 2
    assert all(isinstance(item, demo_pb2.WishlistItem) for item in response)
    assert returned_items == expected_items


# Unit Tests for core functions


def test_get_wishlist(wishlist_server, mock_context):
    # Arrange
    mock_request = MagicMock()
    mock_request.user_id = "1"
    mock_request.name = "books"

    # mock for get_redis_key
    wishlist_server.get_redis_key = MagicMock(return_value="user:1:wishlist:books")

    # mock for get_wishlist_items
    wishlist_server.get_wishlist_items = MagicMock(
        return_value=[
            demo_pb2.WishlistItem(product_id="item1"),
            demo_pb2.WishlistItem(product_id="item2"),
        ]
    )

    # Act
    response = wishlist_server.GetWishlist(mock_request, mock_context)

    # Assert
    # Ensure that get_redis_key is called with the correct request
    wishlist_server.get_redis_key.assert_called_once_with(mock_request)

    # Ensure, that get_wishlist_items is called correctly
    wishlist_server.get_wishlist_items.assert_called_once_with(
        "user:1:wishlist:books", mock_context
    )

    # Check if result has the right format
    assert isinstance(response, demo_pb2.GetWishlistResponse)
    assert response.wishlist.name == "books"
    assert len(response.wishlist.items) == 2
    assert response.wishlist.items[0].product_id == "item1"
    assert response.wishlist.items[1].product_id == "item2"
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