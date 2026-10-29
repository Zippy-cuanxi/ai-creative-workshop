from django.contrib import admin
from django.urls import include, path, re_path

from core.spa import spa_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    # 其余路径交给 Vue Router（资源文件由 WhiteNoise 直接返回）
    re_path(r"^(?!(?:api|admin|static)(?:/|$)).*$", spa_index),
]
