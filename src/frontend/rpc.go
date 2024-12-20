// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"context"
	"time"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"

	"github.com/pkg/errors"
)

const (
	avoidNoopCurrencyConversionRPC = false
)

func (fe *frontendServer) getCurrencies(ctx context.Context) ([]string, error) {
	currs, err := pb.NewCurrencyServiceClient(fe.currencySvcConn).
		GetSupportedCurrencies(ctx, &pb.Empty{})
	if err != nil {
		return nil, err
	}
	var out []string
	for _, c := range currs.CurrencyCodes {
		if _, ok := whitelistedCurrencies[c]; ok {
			out = append(out, c)
		}
	}
	return out, nil
}

func (fe *frontendServer) getProducts(ctx context.Context) ([]*pb.Product, error) {
	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		ListProducts(ctx, &pb.Empty{})
	return resp.GetProducts(), err
}

func (fe *frontendServer) getProduct(ctx context.Context, id string) (*pb.Product, error) {
	resp, err := pb.NewProductCatalogServiceClient(fe.productCatalogSvcConn).
		GetProduct(ctx, &pb.GetProductRequest{Id: id})
	return resp, err
}

func (fe *frontendServer) getCart(ctx context.Context, userID string) ([]*pb.CartItem, error) {
	resp, err := pb.NewCartServiceClient(fe.cartSvcConn).GetCart(ctx, &pb.GetCartRequest{UserId: userID})
	return resp.GetItems(), err
}

func (fe *frontendServer) emptyCart(ctx context.Context, userID string) error {
	_, err := pb.NewCartServiceClient(fe.cartSvcConn).EmptyCart(ctx, &pb.EmptyCartRequest{UserId: userID})
	return err
}

func (fe *frontendServer) insertCart(ctx context.Context, userID, productID string, quantity int32) error {
	_, err := pb.NewCartServiceClient(fe.cartSvcConn).AddItem(ctx, &pb.AddItemRequest{
		UserId: userID,
		Item: &pb.CartItem{
			ProductId: productID,
			Quantity:  quantity},
	})
	return err
}

func (fe *frontendServer) convertCurrency(ctx context.Context, money *pb.Money, currency string) (*pb.Money, error) {
	if avoidNoopCurrencyConversionRPC && money.GetCurrencyCode() == currency {
		return money, nil
	}
	return pb.NewCurrencyServiceClient(fe.currencySvcConn).
		Convert(ctx, &pb.CurrencyConversionRequest{
			From:   money,
			ToCode: currency})
}

func (fe *frontendServer) getShippingQuote(ctx context.Context, items []*pb.CartItem, currency string) (*pb.Money, error) {
	quote, err := pb.NewShippingServiceClient(fe.shippingSvcConn).GetQuote(ctx,
		&pb.GetQuoteRequest{
			Address: nil,
			Items:   items})
	if err != nil {
		return nil, err
	}
	localized, err := fe.convertCurrency(ctx, quote.GetCostUsd(), currency)
	return localized, errors.Wrap(err, "failed to convert currency for shipping cost")
}

func (fe *frontendServer) getRecommendations(ctx context.Context, userID string, productIDs []string) ([]*pb.Product, error) {
	resp, err := pb.NewRecommendationServiceClient(fe.recommendationSvcConn).ListRecommendations(ctx,
		&pb.ListRecommendationsRequest{UserId: userID, ProductIds: productIDs})
	if err != nil {
		return nil, err
	}
	out := make([]*pb.Product, len(resp.GetProductIds()))
	for i, v := range resp.GetProductIds() {
		p, err := fe.getProduct(ctx, v)
		if err != nil {
			return nil, errors.Wrapf(err, "failed to get recommended product info (#%s)", v)
		}
		out[i] = p
	}
	if len(out) > 4 {
		out = out[:4] // take only first four to fit the UI
	}
	return out, err
}

func (fe *frontendServer) getAd(ctx context.Context, ctxKeys []string) ([]*pb.Ad, error) {
	ctx, cancel := context.WithTimeout(ctx, time.Millisecond*100)
	defer cancel()

	resp, err := pb.NewAdServiceClient(fe.adSvcConn).GetAds(ctx, &pb.AdRequest{
		ContextKeys: ctxKeys,
	})
	return resp.GetAds(), errors.Wrap(err, "failed to get ads")
}

func (fe *frontendServer) addWishlist(ctx context.Context, userID string, wishlistName string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).AddWishlist(ctx, &pb.AddWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
	})
	return err
}

func (fe *frontendServer) addItem(ctx context.Context, userID string, wishlistName string, productID string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).AddItem(ctx, &pb.AddToWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
		Item: &pb.WishlistItem{
			ProductId: productID,
		},
	})
	return err
}

func (fe *frontendServer) getWishlist(ctx context.Context, userID string, wishlistName string) (*pb.Wishlist, error) {
	resp, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).GetWishlist(ctx, &pb.GetWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
	})
	if err != nil {
		return nil, err
	}
	return resp.GetWishlist(), nil
}

func (fe *frontendServer) getAllWishlists(ctx context.Context, userID string) ([]*pb.Wishlist, error) {
	resp, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).GetAllWishlists(ctx, &pb.GetAllWishlistsRequest{UserId: userID})
	if err != nil {
		return nil, err
	}
	return resp.GetWishlists(), nil
}

func (fe *frontendServer) removeItem(ctx context.Context, userID string, wishlistName string, productID string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).RemoveItem(ctx, &pb.RemoveFromWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
		Item: &pb.WishlistItem{
			ProductId: productID,
		},
	})
	return err
}

func (fe *frontendServer) emptyWishlist(ctx context.Context, userID string, wishlistName string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).EmptyWishlist(ctx, &pb.EmptyWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
	})
	return err
}

func (fe *frontendServer) deleteWishlist(ctx context.Context, userID string, wishlistName string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).DeleteWishlist(ctx, &pb.DeleteWishlistRequest{
		UserId: userID,
		Name:   wishlistName,
	})
	return err
}

func (fe *frontendServer) renameWishlist(ctx context.Context, userID string, oldName string, newName string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).RenameWishlist(ctx, &pb.RenameWishlistRequest{
		UserId:  userID,
		OldName: oldName,
		NewName: newName,
	})
	return err
}

func (fe *frontendServer) moveWishlistItem(ctx context.Context, userID string, sourceWishlistName string, targetWishlistName string, productID string) error {
	_, err := pb.NewWishlistServiceClient(fe.wishlistSvcConn).MoveWishlistItem(ctx, &pb.MoveWishlistItemRequest{
		UserId:             userID,
		SourceWishlistName: sourceWishlistName,
		TargetWishlistName: targetWishlistName,
		Item: &pb.WishlistItem{
			ProductId: productID,
		},
	})
	return err
}
