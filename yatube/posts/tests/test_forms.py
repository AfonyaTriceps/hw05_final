import shutil
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=settings.MEDIA_TESTS)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif', content=cls.small_gif, content_type='image/gif'
        )
        cls.anon = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_TESTS, ignore_errors=True)

    def test_create_post(self):
        """Создание записи в Post при отправке валидной формы."""
        Post.objects.all().delete()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый пост',
                'group': self.group.id,
                'author': self.user.username,
                'image': self.uploaded,
            },
            follow=True,
        )
        post = Post.objects.get()
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(
            post.author.username,
            self.user.username,
        )
        self.assertEqual(post.image.name, 'posts/small.gif')
        self.assertEqual(Post.objects.count(), 1)

    def test_guest_client_create_post(self):
        """Проверка запрета создания поста неавторизированным пользователем."""
        Post.objects.all().delete()
        response = self.anon.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый пост для анонима',
                'group': self.group.id,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertNotEqual(Post.objects.count(), 1)

    def test_post_edit(self):
        """Редактирование записи в Post при отправке валидной формы."""
        small_gif_new = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_new = SimpleUploadedFile(
            name='small_new.gif',
            content=small_gif_new,
            content_type='image/gif',
        )
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=(self.post.id,),
            ),
            data={
                'text': 'Тестовый пост',
                'group': self.group.id,
                'author': self.user.username,
                'image': uploaded_new,
            },
            follow=True,
        )
        post = Post.objects.get()
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(self.post.id,),
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(
            post.author.username,
            self.user.username,
        )
        self.assertEqual(post.image.name, 'posts/small_new.gif')

    def test_guest_client_post_edit(self):
        """
        Проверка запрета редактирования поста
        неавторизированным пользователем.
        """
        self.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug1',
            description='Тестовое описание1',
        )
        response = self.anon.post(
            reverse(
                'posts:post_edit',
                args=(self.post.id,),
            ),
            data={
                'text': 'Тестовый пост для анонима',
                'group': self.group1.id,
            },
            follow=True,
        )
        post = Post.objects.get()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
        )
        self.assertNotEqual(post.group.title, 'Тестовая группа 1')
        self.assertNotEqual(post.text, 'Тестовый пост для анонима')

    def test_add_comment(self):
        """Создание комментария в Comment при отправке валидной формы."""
        Comment.objects.all().delete()
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=(self.post.id,),
            ),
            data={
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        comment = Comment.objects.get()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(comment.text, 'Тестовый комментарий')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(Comment.objects.count(), 1)

    def test_guest_client_add_comment(self):
        """
        Проверка запрета создания комментария неавторизированным пользователем.
        """
        Comment.objects.all().delete()
        response = self.anon.post(
            reverse(
                'posts:add_comment',
                args=(self.post.id,),
            ),
            data={
                'text': 'Тестовый комментарий',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(), 1)
