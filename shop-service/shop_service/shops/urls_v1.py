from django.urls import path
from .views import *


urlpatterns = [
    # Shop endpoints
    path(
        'shops/', 
        ShopListAPIView.as_view(),
        name='shop-list'
    ),         
    path(
        '<slug:shop_slug>/', 
        ShopDetailAPIView.as_view(), 
        name='shop-detail'
    ),  
    path(
        'shop/create/',
        ShopCreateAPIView.as_view(), 
        name='shop-create'
    ),
    path(
        '<slug:shop_slug>/management/',
        ShopManagementAPIView.as_view(), 
        name='shop-manage'
    ),
    path(
        'user/<str:user_id>/',
        UserShopAPIView.as_view(),
        name='user-shop'
    ),
    # ShopComment endpoints
    path(
        'comments/<slug:shop_slug>/', 
        CommentListByShopAPIView.as_view(),
        name='comment-list'
    ),
    path(
        'comments/<slug:shop_slug>/create/', 
        CreateShopCommentAPIView.as_view(),
        name='create-shop-comment'
    ),
    path(
        'comments/<int:comment_id>/management/',
        CommentManagementAPIView.as_view(), 
        name='comment-manage'
    ),
    # ShopBranch endpoints
    path(
        'branches/<slug:shop_slug>/',
        ShopBranchListByShopAPIView.as_view(),
        name='branch-list'
    ),         
    path(
        'branches/<slug:shop_branch_slug>/', 
        ShopBranchDetailAPIView.as_view(), 
        name='branch-detail'
    ),  
    path(
        'branches/<slug:shop_slug>/create/',
        CreateShopBranchAPIView.as_view(), 
        name='branch-create'
    ),
    path(
        'branches/<slug:shop_branch_slug>/management/',
        ShopBranchManagementAPIView.as_view(), 
        name='branch-manage'
    ),
    # ShopSocialMedia endpoints
      path(
        'social-media/<slug:shop_slug>/',
        ShopSocialMediaListByShopAPIView.as_view(),
        name='social-media-list'
    ),
    path(
        'social-media/<int:social_media_id>/',
        ShopSocialMediaDetailAPIView.as_view(),
        name='social-media-detail'
    ),
    path(
        'social-media/<slug:shop_slug>/create/',
        CreateShopSocialMediaAPIView.as_view(),
        name='social-media-create'
    ),
    path(
        'social-media/<int:social_media_id>/management/',
        ShopSocialMediaManagementAPIView.as_view(),
        name='social-media-manage'
    ),
    # ShopMedia endpoints
     path(
        'media/<slug:shop_slug>/',
        ShopMediaByShopAPIView.as_view(),
        name='shop-media-list'
    ),
    path(
        'media/<slug:shop_slug>/create/',
        CreateShopMediaAPIView.as_view(),
        name='shop-media-create'
    ),
    path(
        'media/<int:media_id>/delete/',
        DeleteShopMediaAPIView.as_view(),
        name='shop-media-delete'
    ),           
]