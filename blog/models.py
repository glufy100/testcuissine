from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Post(models.Model):
    CATEGORIES = [('sale', 'Salé'), ('sucre', 'Sucré'), ('boulange', 'Boulange'), ('experience', 'Expériences')]
    title = models.CharField('Titre', max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField('En quelques mots', max_length=280)
    content = models.TextField('L’histoire du raté')
    lesson = models.TextField('La leçon à retenir', blank=True)
    category = models.CharField('Catégorie', max_length=20, choices=CATEGORIES, default='sale')
    disaster = models.PositiveSmallIntegerField('Niveau de catastrophe / 5', default=3, blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    minutes = models.PositiveIntegerField('Temps passé (minutes)', default=30, blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(1440)])
    image = models.ImageField('Photo du résultat', upload_to='articles/%Y/%m/', blank=True)
    image_url = models.URLField('Photo de démonstration', blank=True)
    published = models.BooleanField('Publier sur le blog', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        verbose_name = 'article'

    def __str__(self):
        return self.title

    @property
    def photo(self):
        return self.image.url if self.image else self.image_url

    def get_absolute_url(self):
        return reverse('detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:180] or 'rate'
            self.slug = base
            i = 2
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{base}-{i}'
                i += 1
        super().save(*args, **kwargs)

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField('Photo', upload_to='articles/galerie/%Y/%m/')
    caption = models.CharField('Légende', max_length=200, blank=True)

    class Meta:
        ordering = ['pk']
