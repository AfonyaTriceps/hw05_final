from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from core.utils import truncatechars
from posts.models import GROUP_CHARACTER_LIMIT

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User, username='auth')

        cls.post = mixer.blend('posts.Post', author=cls.user)

        cls.model_fields_info = (
            ('text', 'текст', 'Введите текст поста'),
            ('pub_date', 'дата публикации', ''),
            ('author', 'автор', ''),
            ('group', 'сообщество', 'Группа, к которой будет относиться пост'),
            ('image', 'картинка', ''),
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        fields = {
            str(self.post): truncatechars(
                self.post.text,
            ),
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_post_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_post_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    help_text,
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User, username='auth')

        cls.group = mixer.blend('posts.Group', title='Тестовая группа')

        cls.model_fields_info = (
            ('title', 'заголовок', ''),
            ('slug', 'слаг', ''),
            ('description', 'описание', ''),
        )

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        fields = {
            str(self.group): (
                truncatechars(self.group.title, GROUP_CHARACTER_LIMIT)
            ),
        }
        for key, expected_value in fields.items():
            with self.subTest(field=key):
                self.assertEqual(key, expected_value)

    def test_group_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_post_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    help_text,
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='auth')

        cls.post = mixer.blend('posts.Post', author=cls.user)
        cls.comment = mixer.blend('posts.Comment', post=cls.post)

        cls.model_fields_info = (
            ('post', 'пост', ''),
            ('author', 'автор', ''),
            ('text', 'текст', 'Напишите свой комментарий к посту'),
            ('created', 'дата и время публикации', ''),
        )

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        fields = {
            str(self.comment): (truncatechars(self.comment.text)),
        }
        for key, expected_value in fields.items():
            with self.subTest(field=key):
                self.assertEqual(key, expected_value)

    def test_group_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_post_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    help_text,
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.follower = mixer.blend(User, username='follower')
        cls.following = mixer.blend(User, username='following')

        cls.post = mixer.blend('posts.Post', author=cls.following)
        cls.follow = mixer.blend(
            'posts.Follow',
            user=cls.follower,
            author=cls.post.author,
        )

        cls.model_fields_info = (
            ('user', 'подписчик', ''),
            ('author', 'автор', ''),
        )

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        fields = {
            str(self.follow): (
                f'Подписчик: {self.follow.user}, автор: {self.follow.author}'
            ),
        }
        for key, expected_value in fields.items():
            with self.subTest(field=key):
                self.assertEqual(key, expected_value)

    def test_group_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    verbose,
                )
