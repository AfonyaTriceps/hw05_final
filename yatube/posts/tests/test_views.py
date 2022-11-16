import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Post
from posts.tests.common import image

User = get_user_model()


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='TestUser')

        cls.authorized_client = Client()

        cls.authorized_client.force_login(cls.user)

        cls.group = mixer.blend('posts.Group', title='Тестовая группа')
        cls.post = mixer.blend('posts.Post', author=cls.user)
        cls.INDEX = ('posts:index', 'posts/index.html', '')
        cls.GROUP = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.group.slug,),
        )
        cls.PROFILE = (
            'posts:profile',
            'posts/profile.html',
            (cls.user.username,),
        )
        cls.POST = (
            'posts:post_detail',
            'posts/post_detail.html',
            (cls.post.id,),
        )
        cls.POST_EDIT = (
            'posts:post_edit',
            'posts/post_create.html',
            (cls.post.id,),
        )
        cls.CREATE_POST = ('posts:post_create', 'posts/post_create.html', '')
        cls.PAGINATED_URLS = (
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE,
            cls.POST,
            cls.POST_EDIT,
            cls.CREATE_POST,
        )

    def setUp(self):
        cache.clear()

    def test_cache_index_page(self):
        """Проверка работы кэша."""
        post = mixer.blend('posts.Post', author=self.user)

        response = self.authorized_client.get(reverse('posts:index'))
        post.delete()
        old_response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, old_response.content)
        cache.clear()
        new_response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(old_response.content, new_response.content)


@override_settings(MEDIA_ROOT=settings.MEDIA_TESTS)
class ContextViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='TestUser')

        cls.authorized_client = Client()

        cls.authorized_client.force_login(cls.user)

        cls.uploaded = image('test_gif.gif')
        cls.group = mixer.blend('posts.Group', title='Тестовая группа')
        cls.post = mixer.blend('posts.Post', author=cls.user, group=cls.group)
        cls.urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            reverse(
                'posts:profile',
                args=(cls.user.username,),
            ),
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_TESTS, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_index_group_profile_show_correct_context(self):
        """
        Шаблоны index, group_list, profile сформированы с
        правильным контекстом.
        """
        for reverse_name in self.urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_entry = response.context['page_obj'][0]
                post_text_0 = first_entry.text
                post_author_0 = first_entry.author.username
                post_image_0 = first_entry.image
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_author_0, str(self.post.author))
                self.assertEqual(post_image_0, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.id,),
            ),
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(
            response.context.get('post').author,
            self.post.author,
        )
        self.assertEqual(
            response.context.get('post').group.title,
            self.post.group.title,
        )
        self.assertEqual(
            response.context.get('post').image,
            self.post.image,
        )

    def test_create_edit_show_correct_context(self):
        """
        Шаблоны post_create, post_edit сформированы с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                args=(self.post.id,),
            ),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_selected_group(self):
        """
        Проверяем создание поста на страницах с выбранной группой
        и отсутствие поста в другой группе
        """
        post = mixer.blend('posts.Post', author=self.user, group=self.group)
        group = mixer.blend('posts.Group')
        for reverse_name in self.urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(post, response.context['page_obj'])

        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                args=(self.group.slug,),
            ),
        )
        self.assertNotIn(group, response.context['page_obj'])


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='auth')
        cls.author = mixer.blend(User, username='author')
        cls.unfollower = mixer.blend(User, username='unfollower')

        cls.authorized_client = Client()
        cls.unfollower_client = Client()

        cls.authorized_client.force_login(cls.user)
        cls.unfollower_client.force_login(cls.unfollower)

        cls.post = mixer.blend('posts.Post', author=cls.author)

    def setUp(self):
        cache.clear()

    def test_authorized_user_can_follow(self):
        """Пользователь имеет возможность подписаться."""
        Follow.objects.all().delete()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.author.username,),
            ),
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_authorized_user_can_unfollow(self):
        """Пользователь имеет возможность отписаться."""
        Follow.objects.all().delete()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.author.username,),
            ),
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.author.username,),
            ),
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_in_feed_subscriber(self):
        """Пост появляется в ленте подписанного пользователя."""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        context = response.context['page_obj']
        self.assertIn(self.post, context)

    def test_new_post_doesnt_in_feed_unsubscribed(self):
        """Пост не появляется в ленте неподписанного пользователя."""
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        context = response.context['page_obj']
        self.assertNotIn(self.post, context)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = mixer.blend(User, username='TestUser')

        cls.authorized_client = Client()

        cls.authorized_client.force_login(cls.user)

        cls.group = mixer.blend('posts.Group', title='Тестовая группа')

        cls.uploaded = image('test_gif.gif')
        cls.posts = []
        for paginator_post in range(13):
            cls.posts.append(
                Post(
                    author=cls.user,
                    group=cls.group,
                    text=f'{paginator_post}',
                ),
            )
        Post.objects.bulk_create(cls.posts)
        cls.urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            reverse(
                'posts:profile',
                args=(cls.user.username,),
            ),
        ]

    def test_first_page_contains_ten_records(self):
        """
        Paginator предоставляет ожидаемое количество постов на первую страницу.
        """
        for reverse_name in self.urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_QUANTITY,
                )

    def test_second_page_contains_three_records(self):
        """
        Paginator предоставляет ожидаемое количество
        постов на вторую страницу.
        """
        for reverse_name in self.urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
