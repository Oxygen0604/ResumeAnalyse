import unittest
from manager import create_app

class AppTestCase(unittest.TestCase):

    def setUp(self):
        """在每个测试之前运行"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        """在每个测试之后运行"""
        self.app_context.pop()

    def test_app_is_up(self):
        """测试应用是否运行"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_404_error(self):
        """测试404错误"""
        response = self.client.get('/this-does-not-exist')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()