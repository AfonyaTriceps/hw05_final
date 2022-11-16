from django.contrib.auth import get_user_model
from django.db import models

from core.utils import truncatechars

User = get_user_model()

GROUP_CHARACTER_LIMIT = 20


class Group(models.Model):
    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField('слаг', max_length=100, unique=True)
    description = models.TextField('описание')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return truncatechars(self.title, GROUP_CHARACTER_LIMIT)


class Post(models.Model):
    text = models.TextField('текст', help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='сообщество',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField('картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return truncatechars(self.text)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField(
        'текст',
        help_text='Напишите свой комментарий к посту',
    )
    created = models.DateTimeField(
        'дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        return truncatechars(self.text)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'Подписчик: {self.user}, автор: {self.author}'
