from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.utils import truncatechars
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.model_fields_info = (
            ('text', 'текст', 'Введите текст поста'),
            ('pub_date', 'дата публикации', ''),
            ('author', 'автор', ''),
            ('group', 'сообщество', 'Группа, к которой будет относиться пост'),
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        fields = {
            str(self.post): truncatechars(
                self.post.text,
                settings.POST_CHARACTER_LIMIT,
            ),
            str(self.group): (
                truncatechars(self.group.title, settings.GROUP_CHARACTER_LIMIT)
                + '…'
                if len(self.group.title) > settings.GROUP_CHARACTER_LIMIT
                else self.group.title
            ),
        }
        for field, expected_value in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    verbose,
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, verbose, help_text in self.model_fields_info:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    help_text,
                )
