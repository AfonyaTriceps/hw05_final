from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()

POST_ID = 1


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='TestUser')
        cls.author = mixer.blend(User, username='author')

        cls.anon = Client()
        cls.authorized_client = Client()
        cls.author_client = Client()

        cls.authorized_client.force_login(cls.user)
        cls.author_client.force_login(cls.author)

        cls.group = mixer.blend('posts.Group', title='Тестовая группа')
        cls.post = mixer.blend('posts.Post', author=cls.author)
        cls.follow = mixer.blend(
            'posts.Follow',
            user=cls.user,
            author=cls.author,
        )

        cls.urls = {
            'add_comment': reverse('posts:add_comment', args=(cls.post.id,)),
            'follow_index': reverse('posts:follow_index'),
            'group_list': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse('posts:post_detail', args=(cls.post.id,)),
            'post_edit': reverse('posts:post_edit', args=(cls.post.id,)),
            'profile': reverse('posts:profile', args=(cls.author,)),
            'profile_follow': reverse(
                'posts:profile_follow',
                args=(cls.author,),
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                args=(cls.author,),
            ),
        }

    def test_http_statuses(self):
        """Проверка статусов разными пользователями"""
        httpstatuses = (
            (self.urls.get('add_comment'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('add_comment'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('follow_index'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('group_list'), HTTPStatus.OK, self.anon),
            (self.urls.get('index'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('post_edit'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (self.urls.get('post_edit'), HTTPStatus.OK, self.author_client),
            (self.urls.get('profile'), HTTPStatus.OK, self.anon),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.author_client,
            ),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.anon),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.FOUND,
                self.author_client,
            ),
        )
        for url, status, client in httpstatuses:
            with self.subTest(url=url, status=status):
                self.assertEqual(client.post(url).status_code, status)

    def test_redirects(self):
        """Тест редиректов"""
        redirects = (
            (
                self.urls.get('add_comment'),
                f'/posts/{self.post.id}/',
                self.authorized_client,
            ),
            (
                self.urls.get('post_create'),
                '/auth/login/?next=/create/',
                self.anon,
            ),
            (
                self.urls.get('post_edit'),
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
                self.anon,
            ),
            (
                self.urls.get('profile_follow'),
                f'/profile/{self.post.author}/',
                self.authorized_client,
            ),
            (
                self.urls.get('profile_unfollow'),
                f'/profile/{self.post.author}/',
                self.authorized_client,
            ),
        )
        for url, redirect_url, client in redirects:
            with self.subTest(url=url, redirect_url=redirect_url):
                self.assertRedirects(client.get(url), redirect_url)

    def test_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = (
            (
                self.urls.get('follow_index'),
                'posts/follow.html',
                self.authorized_client,
            ),
            (self.urls.get('group_list'), 'posts/group_list.html', self.anon),
            (self.urls.get('index'), 'posts/index.html', self.anon),
            (
                self.urls.get('post_create'),
                'posts/post_create.html',
                self.authorized_client,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.anon,
            ),
            (
                self.urls.get('post_edit'),
                'posts/post_create.html',
                self.author_client,
            ),
            (self.urls.get('profile'), 'posts/profile.html', self.anon),
        )
        for url, template, client in templates:
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(client.get(url), template)
