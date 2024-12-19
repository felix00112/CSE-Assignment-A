# File: src/wishlistservice/tests/test_wishlist_server.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
from unittest.mock import patch, MagicMock
import grpc
import demo_pb2_grpc
from wishlist_client import setup_grpc_client


def test_grpc_client_setup():
    # Arrange
    channel_mock = MagicMock()
    stub_mock = MagicMock()

    # Mock gRPC channel und WishlistServiceStub
    with patch('grpc.insecure_channel', return_value=channel_mock) as mock_insecure_channel, \
            patch('demo_pb2_grpc.WishlistServiceStub', return_value=stub_mock) as mock_wishlist_stub:
        # Act
        channel = grpc.insecure_channel('[::]:50052')
        stub = demo_pb2_grpc.WishlistServiceStub(channel)

        # Assert
        # Verify that the channel was created with the correct address
        mock_insecure_channel.assert_called_once_with('[::]:50052')

        # Verify that the stub was initialized with the created channel
        mock_wishlist_stub.assert_called_once_with(channel)

        # Ensure that the returned stub is correct
        assert stub == stub_mock

def test_main_grpc_client_setup():
    channel_mock = MagicMock()
    stub_mock = MagicMock()

    with patch('grpc.insecure_channel', return_value=channel_mock) as mock_insecure_channel, \
            patch('demo_pb2_grpc.WishlistServiceStub', return_value=stub_mock) as mock_wishlist_stub:
        stub = setup_grpc_client()

        mock_insecure_channel.assert_called_once_with('[::]:50052')
        mock_wishlist_stub.assert_called_once_with(channel_mock)
        assert stub == stub_mock

