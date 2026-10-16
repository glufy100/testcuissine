from django import forms
from .models import Post

class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else ([data] if data else [])
        if len(files) > 20:
            raise forms.ValidationError('Ajoute au maximum 20 photos à la fois.')
        images = [super(MultipleImageField, self).clean(file, initial) for file in files]
        if any(image.size > 8 * 1024 * 1024 for image in images):
            raise forms.ValidationError('Chaque photo doit peser moins de 8 Mo.')
        return images

class PostForm(forms.ModelForm):
    gallery_images = MultipleImageField(label='Photos supplémentaires', required=False, widget=MultipleImageInput(attrs={'accept': 'image/*'}))
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'category', 'disaster', 'minutes', 'image', 'content', 'lesson', 'published']
        widgets = {'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Ce que je voulais faire… Ce qui s’est vraiment passé…'}), 'lesson': forms.Textarea(attrs={'rows': 3}), 'excerpt': forms.Textarea(attrs={'rows': 2}), 'disaster': forms.NumberInput(attrs={'min': 1, 'max': 5})}

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 8 * 1024 * 1024:
            raise forms.ValidationError('La photo doit peser moins de 8 Mo.')
        return image
