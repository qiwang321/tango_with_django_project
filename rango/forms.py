from django import forms
from rango.models import Page, Category

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        model = Category
        fields = ('name', 'views', 'likes')


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.CharField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        model = Page
        fields = ('title', 'url', 'views')

    # fixed a mal-formed url
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        
        # If url is not empty and doesn't start with http://
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url
            
        return cleaned_data


# user registration
from rango.models import UserProfile
from django.contrib.auth.models import User
class UserForm(forms.ModelForm):
    # fields are modified if only the form element has different attributes than the model field
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    website = forms.CharField(help_text="Please enter your website.", required=False)
    picture = forms.ImageField(help_text="Select a profile image to upload.", required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('website')

        if url and not url.startswith('http://'):
            url = 'http://' + url
        cleaned_data['website'] = url

        return cleaned_data
