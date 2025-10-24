from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user_connection = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating_total = Post.objects.filter(author=self).aggregate(total=sum('post_rating'))['total'] or 0
        post_rating_total *= 3

        comment_by_author_total = Comment.objects.filter(user=self.user_connection).aggregate(total=sum('rating_comment'))['total'] or 0

        comment_on_posts_total = Comment.objects.filter(post_connection__author=self).aggregate(total=sum('rating_comment'))['total'] or 0

        self.rating = post_rating_total + comment_by_author_total + comment_on_posts_total
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    CHOICES_POST = [
        ('Article', 'Статья'),
        ('News', 'Новость')
    ]

    post_choice = models.CharField(max_length=10, choices=CHOICES_POST)
    auto_post_datetime = models.DateTimeField(auto_now_add=True)
    category_connection = models.ManyToManyField(Category, through='PostCategory')
    headline = models.CharField(max_length=225, choices=CHOICES_POST, unique=True)
    text = models.TextField(unique=True, choices=CHOICES_POST)
    post_rating = models.IntegerField(default=0, choices=CHOICES_POST)

    def like(self):
        self.post_rating += 1
        return self.post_rating

    def dislike(self):
        if self.post_rating > 0:
            self.post_rating -= 1
        else:
            self.post_rating = 0

    def preview(self):
        return self.text[0:123]

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post_connection = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.TextField(unique=True)
    datetime_create_comment = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        return self.rating_comment

    def dislike(self):
        if self.rating_comment > 0:
            self.rating_comment -= 1
        else:
            self.rating_comment = 0

    user1 = User.objects.create_user('Pushkin')
    user2 = User.objects.create_user('Tolstoy')

    author1 = Author.objects.create(user=user1)
    author2 = Author.objects.create(user=user2)

    category1 = Category.objects.create(name='Спорт')
    category2 = Category.objects.create(name='Наука')
    category3 = Category.objects.create(name='Технологии')
    category4 = Category.objects.create(name='Природа')


    post1 = Post.objects.create(
        author=author1,
        post_type='article',
        title='Первая статья',
        content='Содержание первой статьи',
        rating=0
    )
    post1.categories.add(cat1, cat2)


    post2 = Post.objects.create(
        author=author2,
        post_type='article',
        title='Вторая статья',
        content='Содержание второй статьи',
        rating=0
    )
    post2.categories.add(cat3)


    news1 = Post.objects.create(
        author=author1,
        post_type='news',
        title='Новость',
        content='Содержание новости',
        rating=0
    )
    news1.categories.add(cat1, cat4)


    comment1 = Comment.objects.create(post=post1, user=user1, text='Комментарий 1 к статье 1', rating=0)
    comment2 = Comment.objects.create(post=post1, user=user2, text='Комментарий 2 к статье 1', rating=0)
    comment3 = Comment.objects.create(post=post2, user=user1, text='Комментарий к статье 2', rating=0)
    comment4 = Comment.objects.create(post=news1, user=user2, text='Комментарий к новости', rating=0)


    post1.like()
    post1.like()
    post2.dislike()
    news1.like()


    comment1.like()
    comment2.dislike()
    comment3.like()
    comment4.dislike()

    author1.update_rating()
    author2.update_rating()

    best_author = Author.objects.order_by('-rating').first()
    print(f"Лучший пользователь: {best_author.user.username}, рейтинг: {best_author.rating}")

    best_post = Post.objects.filter(post_type='article').order_by('-rating').first()
    print(f"Лучшая статья:")
    print(f"Дата: {best_post.created_at}")
    print(f"Автор: {best_post.author.user.username}")
    print(f"Рейтинг: {best_post.rating}")
    print(f"Заголовок: {best_post.title}")
    print(f"Превью: {best_post.preview()}")

    comments = Comment.objects.filter(post=best_post)
    print("Комментарии к лучшей статье:")
    for comment in comments:
        print(
            f"Дата: {comment.created_at}, Пользователь: {comment.user.username}, Рейтинг: {comment.rating}, Текст: {comment.text}")