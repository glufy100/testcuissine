from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Post
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import tempfile

class BlogTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user('chef', password='test-pass-123', is_staff=True)
        self.reader = get_user_model().objects.create_user('lecteur', password='test-pass-123')
        self.post = Post.objects.create(title='Gâteau brûlé', excerpt='Un essai au chocolat', content='Une histoire', category='sucre', published=True)
        self.draft = Post.objects.create(title='Mon brouillon secret', excerpt='Privé', content='Privé', published=False)

    def test_public_browsing_and_filters(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, self.post.title)
        self.assertNotContains(response, self.draft.title)
        self.assertContains(self.client.get('/?q=chocolat'), self.post.title)
        self.assertNotContains(self.client.get('/?categorie=sale'), 'Lire Gâteau brûlé')
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.post.get_absolute_url()).status_code, 200)

    def test_admin_requires_staff(self):
        self.assertRedirects(self.client.get('/admin/'), '/connexion/?next=/admin/', fetch_redirect_response=False)
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        response = self.client.post(reverse('edit', args=[self.post.pk]), {'title': 'Intrusion'})
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Gâteau brûlé')

    def test_editor_publish_draft_delete(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(self.client.get(reverse('edit', args=[self.post.pk])).status_code, 200)
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 200)
        payload = {'title': 'Un nouveau raté', 'excerpt': 'Résumé', 'content': '<script>alert(1)</script>', 'category': 'sale', 'disaster': 3, 'minutes': 25}
        self.assertRedirects(self.client.post(reverse('create'), payload), reverse('dashboard'))
        new = Post.objects.get(title=payload['title'])
        self.assertFalse(new.published)
        self.assertContains(self.client.get(new.get_absolute_url()), '&lt;script&gt;')
        payload['published'] = 'on'
        self.client.post(reverse('edit', args=[new.pk]), payload)
        new.refresh_from_db()
        self.assertTrue(new.published)
        self.assertEqual(self.client.get(reverse('delete', args=[new.pk])).status_code, 405)
        self.client.post(reverse('delete', args=[new.pk]))
        self.assertFalse(Post.objects.filter(pk=new.pk).exists())

    def test_validation_and_csrf(self):
        self.client.force_login(self.staff)
        invalid = {'title': 'Mauvais score', 'excerpt': 'Résumé', 'content': 'Texte', 'category': 'sale', 'disaster': 9, 'minutes': 20}
        response = self.client.post(reverse('create'), invalid)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='Mauvais score').exists())
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.staff)
        self.assertEqual(strict.post(reverse('delete', args=[self.post.pk])).status_code, 403)

    def test_real_login_logout(self):
        response = self.client.post(reverse('login'), {'username': 'chef', 'password': 'test-pass-123'})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))

    def test_photo_upload(self):
        self.client.force_login(self.staff)
        output = io.BytesIO()
        Image.new('RGB', (30, 30), 'green').save(output, format='PNG')
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            payload = {'title': 'Photo du raté', 'excerpt': 'Un gâteau', 'content': 'Voici ma photo', 'category': 'sucre', 'disaster': 3, 'minutes': 15, 'published': 'on', 'image': SimpleUploadedFile('gateau.png', output.getvalue(), content_type='image/png'), 'gallery_images': [SimpleUploadedFile('detail.png', output.getvalue(), content_type='image/png'), SimpleUploadedFile('cuisson.png', output.getvalue(), content_type='image/png')]}
            self.assertRedirects(self.client.post(reverse('create'), payload), reverse('dashboard'))
            post = Post.objects.get(title='Photo du raté')
            self.assertTrue(post.image.storage.exists(post.image.name))
            self.assertContains(self.client.get(post.get_absolute_url()), post.image.url)
            self.assertEqual(post.gallery.count(), 2)
            response = self.client.get(post.get_absolute_url())
            for photo in post.gallery.all():
                self.assertContains(response, photo.image.url)
            payload.pop('image')
            payload['gallery_images'] = [SimpleUploadedFile('ok.png', output.getvalue(), content_type='image/png'), SimpleUploadedFile('faux.jpg', b'pas une image', content_type='image/jpeg')]
            payload['title'] = 'Galerie invalide'
            self.assertEqual(self.client.post(reverse('create'), payload).status_code, 200)
            self.assertFalse(Post.objects.filter(title='Galerie invalide').exists())
