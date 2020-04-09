import time
from django.test import TestCase, Client, override_settings
from .models import User, Post, Follow
from yatube import settings
from django.shortcuts import redirect

class ProfileTest(TestCase):
        def setUp(self):
                # создание тестового клиента — подходящая задача для функции setUp()
                self.client = Client()
                # создаём пользователя
                self.user = User.objects.create_user(
                        username="admin2", email="admin@2.com", password="12345"
                )
                self.user2 = User.objects.create_user(
                        username="admin3", email="admin@3.com", password="12345"
                )
                

               

        
        def test_profile(self):
                self.client.force_login(self.user)
                response = self.client.get(f"/{self.user.username}/")
                self.assertEqual(response.status_code, 200)

        def test_authed_new(self):
                self.client.force_login(self.user)
                response = self.client.post('/new/', {"text": "new_post"}, follow=True)
                post = Post.objects.filter(author=self.user, text="new_post").first()
                self.assertIsNotNone(post)
                self.client.logout()

        def test_unauth_new(self):
                response = self.client.post('/new/', {"text": "new_post"}, follow=True)
                self.assertRedirects(response, '/auth/login/?next=/new/')
        
        @override_settings(CACHES=settings.TEST_CACHES)
        def test_new_post_exists(self):
                self.client.force_login(self.user)
                post = Post.objects.create(text="This will be a new post. the only post known to mankind", author=self.user)
                response = self.client.get('/')
                self.assertContains(response, post)
                response = self.client.get(f'/{self.user.username}/{post.id}/')
                self.assertContains(response, post)
                response = self.client.get(f"/{self.user.username}/")
                self.assertContains(response, post)

        @override_settings(CACHES=settings.TEST_CACHES)
        def test_authed_user_can_edit(self):
                self.client.force_login(self.user)
                post = Post.objects.create(text='This is an unedited version of the post', author=self.user)
                self.client.post(f"/{self.user.username}/{post.id}/edit/", {'text': 'This is an edited version of the post'}, follow=True)
                edited_post = 'This is an edited version of the post'
                index_response = self.client.get('/')
                profile_response = self.client.get(f"/{self.user.username}/")
                post_response = self.client.get(f'/{self.user.username}/{post.id}/')
                self.assertEqual(index_response.context['post'].text, edited_post)
                self.assertContains(profile_response, edited_post)
                self.assertEqual(post_response.context['post'].text, edited_post)
        
        @override_settings(CACHES=settings.TEST_CACHES)
        def test_postpage_has_img(self):
                self.client.force_login(self.user)
                post = Post.objects.create(text='This is a new post with no image', author=self.user)
                with open ("media\posts\img.jpeg", 'rb') as img:
                        self.client.post(f"/{self.user.username}/{post.id}/edit/", {'text': 'This post is supposed to be with an image', 'image': img}, follow=True)
                post_response = self.client.get(f'/{self.user.username}/{post.id}/')
                index_response = self.client.get('/')
                profile_response = self.client.get(f"/{self.user.username}/")
                self.assertContains(post_response, "img")
                self.assertContains(index_response, "img")
                self.assertContains(profile_response, "img")
                
        def test_unable_to_upload_anonimg(self):
                self.client.force_login(self.user)
                with open ("media\posts\\readme.txt") as txt:
                        self.client.post(f"/new", {'text': 'This post is supposed to be with an image', 'image': txt}, follow=True)
                index_response = self.client.get('/')
                self.assertNotContains(index_response, "img")#не знаю как доделать этот тест. вернусь позже

        def test_chached_posts(self):
                self.client.force_login(self.user)
                post = Post.objects.create(text='This is a new post. It shouldnt be seen right away.', author=self.user)
                index_response = self.client.get('/')
                self.assertNotContains(index_response, post.text)
                time.sleep(11)#другого способа не придумал, сорян. 
                index_response = self.client.get('/')
                self.assertContains(index_response, post.text)
        
        #тесты 1 и 2. Вроде как проверяется и первый и второй тест тут. 
        @override_settings(CACHES=settings.TEST_CACHES)
        def test_authed_user_can_sub_unsub(self):
                self.client.force_login(self.user)
                post = Post.objects.create(text='If ive done everything right you should see this text', author=self.user2)
                self.client.get(f'/{self.user2.username}/follow', follow=True)#могу фолловиться 
                response = self.client.get('/follow/')
                self.assertContains(response, post.text)#проверяю что есть пост у авторов подписок
                self.client.get(f'/{self.user2.username}/unfollow', follow=True)#могу анфоловиться 
                response_new = self.client.get('/follow/')#проверяю что нету если не подписан
                #print(response_new.content.decode('utf-8'))
                self.assertNotContains(response_new, post.text)

        def test_unauthed_user_cant_comment(self):
                post = Post.objects.create(text='If ive done everything right you should see this text', author=self.user2)
                response = self.client.post(f'/{self.user2.username}/{post.id}/comment/', {'text': "test comment", 'author': self.user}, follow=True)
                self.assertRedirects(response, '/auth/login/?next=/admin3/1/comment/')
        
