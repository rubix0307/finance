from django.test import TestCase
from receipt.models import Shop


class ShopModelTest(TestCase):

    def setUp(self):
        self.shop1 = Shop.objects.create(name="CONAD BERGAMO", address="Via G. Carducci, 55")
        self.shop2 = Shop.objects.create(name="CONAD MILANO", address="Via Roma, 12")
        self.shop3 = Shop.objects.create(name="LIDL TORINO", address="Corso Francia, 5")

    def test_create_new_shop(self):
        """
        Test the creation of a new store if there is no new store.
        """
        new_shop = Shop.find_or_create(name="ESSELUNGA FIRENZE", address="Piazza della Repubblica, 10")
        self.assertIsInstance(new_shop, Shop)
        self.assertEqual(new_shop.name, "ESSELUNGA FIRENZE")
        self.assertEqual(new_shop.address, "Piazza della Repubblica, 10")

    def test_find_existing_shop(self):
        """
        Test of finding an existing store by exact name match.
        """
        found_shop = Shop.find_or_create(name="CONAD BERGAMO", address="Some other address")
        self.assertEqual(found_shop, self.shop1)

    def test_find_similar_shop(self):
        """
        The test of finding a similar store.
        """
        similar_shop = Shop.find_or_create(name="CONA BERGMO", similarity=0.5)
        self.assertEqual(similar_shop, self.shop1)

    def test_create_shop_if_not_similar_enough(self):
        """
        If the match is not close enough, a new store is created.
        """
        new_shop = Shop.find_or_create(name="UNKNOWN SHOP", address="Random Address")
        self.assertNotEqual(new_shop, self.shop1)
        self.assertNotEqual(new_shop, self.shop2)
        self.assertNotEqual(new_shop, self.shop3)
        self.assertEqual(new_shop.name, "UNKNOWN SHOP")

    def test_find_shop_with_different_case(self):
        """
        A case-insensitive store search.
        """
        found_shop = Shop.find_or_create(name="conad bergamo")
        self.assertEqual(found_shop, self.shop1)

    def test_similarity_threshold(self):
        """
        Checking the operation of the similarity parameter.
        """
        found_shop = Shop.find_or_create(name="CONA BERGMO", similarity=0.9)
        self.assertNotEqual(found_shop, self.shop1)
