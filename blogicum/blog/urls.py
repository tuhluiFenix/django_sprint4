from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.MaintListView.as_view(), name="index"),# отображает все посты на главной странице

    

    path("profile/<slug:username>/", views.ProfileListView.as_view(), name="profile"),# отображение профиля
    path('profile/edit/<int:pk>/', views.EditProfileView.as_view(), name='edit_profile'),# редактирование профиля

    path("category/<slug:category_slug>/", views.PostDetailView.as_view(), name="category_posts"),# ссылка на категорию. Функция обрабатвает категорию
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),# просмотр поста
    path("posts/create/", views.PostCreateView.as_view(), name="create_post"),# создание поста автором
]
