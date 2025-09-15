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