import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Post
from posts.tests.common import image

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.MEDIA_TESTS)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='TestUser')

        cls.anon = Client()
        cls.authorized_client = Client()

        cls.authorized_client.force_login(cls.user)

        cls.group = mixer.blend('posts.Group', title='Тестовая группа')
        cls.uploaded = image('test_gif.gif')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_TESTS, ignore_errors=True)
        cache.clear()

    def test_create_post(self):
        """Создание записи в Post при отправке валидной формы."""
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
                'author': self.user.username,
                'image': self.uploaded,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.name, 'posts/test_gif.gif')
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ),
        )

    def test_guest_client_create_post(self):
        """Проверка запрета создания поста неавторизированным пользователем."""
        self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост для анонима',
                'group': self.group.id,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit(self):
        """Редактирование записи в Post при отправке валидной формы."""
        new_post = mixer.blend('posts.Post', author=self.user)
        uploaded_new = image('test_gif_new.gif')
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=(new_post.id,),
            ),
            {
                'text': 'Тестовый пост',
                'group': self.group.id,
                'image': uploaded_new,
            },
            follow=True,
        )
        post = Post.objects.get()
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(new_post.id,),
            ),
        )
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(
            post.author,
            self.user,
        )
        self.assertEqual(post.image.name, 'posts/test_gif_new.gif')

    def test_guest_client_post_edit(self):
        """
        Проверка запрета редактирования поста
        неавторизированным пользователем.
        """
        group1 = mixer.blend('posts.Group', title='Тестовая группа 1')
        post = mixer.blend('posts.Post', author=self.user, group=self.group)
        self.anon.post(
            reverse(
                'posts:post_edit',
                args=(post.id,),
            ),
            {
                'text': 'Тестовый пост для анонима',
                'group': group1.id,
            },
            follow=True,
        )
        self.assertNotEqual(post.group.title, 'Тестовая группа 1')
        self.assertNotEqual(post.text, 'Тестовый пост для анонима')

    def test_add_comment(self):
        """Создание комментария в Comment при отправке валидной формы."""
        post = mixer.blend('posts.Post', author=self.user, group=self.group)
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=(post.id,),
            ),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, 'Тестовый комментарий')
        self.assertEqual(comment.author, self.user)

    def test_guest_client_add_comment(self):
        """
        Проверка запрета создания комментария неавторизированным пользователем.
        """
        post = mixer.blend('posts.Post', author=self.user, group=self.group)
        self.anon.post(
            reverse(
                'posts:add_comment',
                args=(post.id,),
            ),
            {
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
