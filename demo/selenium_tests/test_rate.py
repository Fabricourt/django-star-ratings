from mock import patch
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from hypothesis import given
from hypothesis.extra.django import TestCase
from hypothesis.strategies import integers, lists
from selenium.common.exceptions import NoSuchElementException


class RateTest(TestCase, StaticLiveServerTestCase):
    def login(self, username, password):
        self.driver.find_element_by_id('login-link').click()
        self.driver.find_element_by_id('id_username').send_keys(username)
        self.driver.find_element_by_id('id_password').send_keys(password)
        self.driver.find_element_by_id('id_submit').click()

    def logout(self):
        try:
            self.driver.find_element_by_id('logout-link').click()
        except NoSuchElementException:
            pass

    def tearDown(self):
        self.logout()

    @given(integers(min_value=1, max_value=5))
    def test_click_first_star___rating_is_set_to_one(self, value):
        expected_percentage = 20 * value
        expected_style = 'width: {}%;'.format(expected_percentage)

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(value)).click()

        foreground = self.driver.find_element_by_class_name('star-ratings-rating-foreground')
        average_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')
        count_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')
        user_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')

        self.assertEqual(expected_style, str(foreground.get_attribute('style')).strip())
        self.assertEqual(value, float(average_elem.text))
        self.assertEqual(1, int(count_elem.text))
        self.assertEqual(value, int(user_elem.text))

    @given(integers(min_value=1, max_value=10))
    def test_star_rating_range_is_set___rating_range_on_page_is_the_star_rating(self, value):
        with patch('star_ratings.templatetags.ratings.STAR_RATINGS_RANGE', value):
            self.driver.get(self.live_server_url)

            background = self.driver.find_element_by_class_name('star-ratings-rating-background')
            elements = background.find_elements_by_tag_name('li')

            self.assertEqual(value, len(elements))
