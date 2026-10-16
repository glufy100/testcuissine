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
        self.staff = get_user_model().objects.create_user('chef', password='test-pass-123', is_staff=True, is_superuser=True)
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
        self.assertEqual(self.client.get('/admin/').status_code, 403)
        response = self.client.post(reverse('edit', args=[self.post.pk]), {'title': 'Intrusion'})
        self.assertEqual(response.status_code, 403)
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

    def test_login_lockout_covers_both_login_pages(self):
        for _ in range(5):
            response = self.client.post(reverse('login'), {'username': 'chef', 'password': 'incorrect'})
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, '15 minutes', status_code=429)
        self.assertEqual(self.client.post(reverse('login'), {'username': 'chef', 'password': 'test-pass-123'}).status_code, 429)
        self.assertEqual(self.client.post('/gestion-django/login/', {'username': 'chef', 'password': 'test-pass-123'}).status_code, 429)

    def test_admin_password_change(self):
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get(reverse('password_change')).status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('password_change')).status_code, 200)
        payload = {'old_password': 'test-pass-123', 'new_password1': 'Court-7!', 'new_password2': 'Court-7!'}
        self.assertEqual(self.client.post(reverse('password_change'), payload).status_code, 200)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password('test-pass-123'))
        payload.update(new_password1='Cuisine-solide-2026!', new_password2='Cuisine-solide-2026!')
        self.assertRedirects(self.client.post(reverse('password_change'), payload), reverse('password_changed'))
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password('Cuisine-solide-2026!'))

    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=True, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True, SECURE_HSTS_SECONDS=31536000)
    def test_production_https_and_cookies(self):
        self.assertEqual(self.client.get('/').status_code, 301)
        response = self.client.get(reverse('login'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('max-age=31536000', response['Strict-Transport-Security'])
        self.assertTrue(response.cookies['csrftoken']['secure'])
        response = self.client.post(reverse('login'), {'username': 'chef', 'password': 'test-pass-123'}, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.cookies['sessionid']['secure'])
        self.assertTrue(response.cookies['sessionid']['httponly'])

    def test_only_admin_can_publish_even_with_staff_permissions(self):
        from django.contrib.auth.models import Permission
        employee = get_user_model().objects.create_user('equipe', password='Equipe-pass-2026!', is_staff=True)
        employee.user_permissions.set(Permission.objects.filter(content_type__app_label='blog'))
        payload = {'title': 'Publication interdite', 'excerpt': 'Résumé', 'content': 'Texte', 'category': 'sale', 'disaster': 2, 'minutes': 20, 'published': 'on'}
        for user in (None, self.reader, employee):
            self.client.logout()
            if user:
                self.client.force_login(user)
            expected = 403 if user else 302
            self.assertEqual(self.client.post(reverse('create'), payload).status_code, expected)
            self.assertEqual(self.client.post(reverse('edit', args=[self.draft.pk]), payload).status_code, expected)
            self.assertEqual(self.client.post(reverse('delete', args=[self.post.pk])).status_code, expected)
            self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.draft.refresh_from_db()
        self.assertFalse(self.draft.published)
        self.assertFalse(Post.objects.filter(title='Publication interdite').exists())
        self.assertEqual(self.client.post('/gestion-django/blog/post/add/', payload).status_code, 403)
        self.assertEqual(self.client.post(f'/gestion-django/blog/post/{self.draft.pk}/change/', payload).status_code, 403)

    def test_non_admin_cannot_log_into_publishing_interface(self):
        response = self.client.post(reverse('login'), {'username': 'lecteur', 'password': 'test-pass-123'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
