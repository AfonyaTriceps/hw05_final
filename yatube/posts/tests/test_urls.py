from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()

POST_ID = 1


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.anon = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }
        cls.POST_INDEX = ('/', 'posts/index.html')
        cls.POST_GROUP = (f'/group/{cls.group.slug}/', 'posts/group_list.html')
        cls.POST_PROFILE = (f'/profile/{cls.user}/', 'posts/profile.html')
        cls.POST_URL = (f'/posts/{cls.post.id}/', 'posts/post_detail.html')
        cls.POST_EDIT_URL = (
            f'/posts/{POST_ID}/edit/',
            'posts/post_create.html',
        )
        cls.POST_CREATE_URL = ('/create/', 'posts/post_create.html')
        cls.PUBLIC_URLS = [
            cls.POST_INDEX,
            cls.POST_GROUP,
            cls.POST_PROFILE,
            cls.POST_URL,
        ]
        cls.PRIVATE_URLS = [
            cls.POST_EDIT_URL,
            cls.POST_CREATE_URL,
        ]
        cls.URLS = cls.PUBLIC_URLS + cls.PRIVATE_URLS

    def setUp(self):
        cache.clear()

    def test_urls_exists_at_desired_location(self):
        """Страницы в PUBLIC_URLS доступны любому пользователю"""
        for address, templates in self.PUBLIC_URLS:
            with self.subTest(address):
                response = self.anon.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страницы /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_at_desired_location(self):
        """Страница /unexisting_page/ возвращает код 404."""
        response = self.anon.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_edit_url_redirect_anonymous_on_auth_login(self):
        """
        Страницы create и edit перенаправят неавторизированного
        пользователя на страницу логина.
        """
        for address, templates in self.PRIVATE_URLS:
            with self.subTest(address=address):
                response = self.anon.get(address)
                self.assertRedirects(response, '/auth/login/?next=' + address)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.URLS:
            with self.subTest(url=url, template=template):
                got = self.authorized_client.get(url)
                self.assertTemplateUsed(got, template)
