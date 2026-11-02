from django.urls import path
from .views import ProductList, ProductDetail
urlpatterns = [path("products/", ProductList.as_view()), path("products/<slug:slug>/", ProductDetail.as_view())]

from .collection_views import CollectionList, CollectionProducts
urlpatterns += [
    path("collections/", CollectionList.as_view(), name="collection-list"),
    path("collections/<slug:slug>/products/", CollectionProducts.as_view(), name="collection-products"),
]