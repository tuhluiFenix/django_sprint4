from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.MaintListView.as_view(), name="index"),# отображает все посты на главной странице
    path("posts/category/<slug:category_slug>/", views.PostCategoryListView.as_view(), name="category_posts"),# ссылка на категорию. Функция обрабатвает категорию
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),# редактирование профиля
    path("profile/<str:username>/", views.ProfileListView.as_view(), name="profile"),# отображение профиля
    

    
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),# просмотр поста
    path("posts/create/", views.PostCreateView.as_view(), name="create_post"),# создание поста автором
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path(
        "posts/<int:pk>/comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:pk>/edit_comment/<int:comment_pk>/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:pk>/delete_comment/<int:comment_pk>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
]
