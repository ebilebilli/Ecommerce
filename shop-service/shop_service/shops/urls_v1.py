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
        'shops/<slug:shop_slug>/', 
        ShopDetailAPIView.as_view(), 
        name='shop-detail'
    ),  
    path(
        'shops/shop/create/',
        ShopCreateAPIView.as_view(), 
        name='shop-create'
    ),
    path(
        'shops/<slug:shop_slug>/management/',
        ShopManagementAPIView.as_view(), 
        name='shop-manage'
    ),
    # ShopComment endpoints
    path(
        'shops/<slug:shop_slug>/comments/', 
        CommentListByShopAPIView.as_view(),
        name='comment-list'
    ),
    path(
        'shops/<slug:shop_slug>/comment/create/', 
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
        'shops/<slug:shop_slug>/branches/',
        ShopBranchListByShopAPIView.as_view(),
        name='branch-list'
    ),         
    path(
        'branches/<slug:shop_branch_slug>/', 
        ShopBranchDetailAPIView.as_view(), 
        name='branch-detail'
    ),  
    path(
        'shops/<slug:shop_slug>/branches/create/',
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
        'shops/<slug:shop_slug>/social-media/',
        ShopSocialMediaListByShopAPIView.as_view(),
        name='social-media-list'
    ),
    path(
        'social-media/<int:social_media_id>/',
        ShopSocialMediaDetailAPIView.as_view(),
        name='social-media-detail'
    ),
    path(
        'shops/<slug:shop_slug>/social-media/create/',
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
        'shops/<slug:shop_slug>/media/',
        ShopMediaByShopAPIView.as_view(),
        name='shop-media-list'
    ),
    path(
        'shops/<slug:shop_slug>/media/create/',
        CreateShopMediaAPIView.as_view(),
        name='shop-media-create'
    ),
    path(
        'media/<int:media_id>/delete/',
        DeleteShopMediaAPIView.as_view(),
        name='shop-media-delete'
    ),             
]