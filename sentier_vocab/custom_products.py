from sentier_vocab.add_terms import add_custom_terms
from sentier_vocab.input.custom_products import CUSTOM_PRODUCTS_DATA


def add_custom_products():
    add_custom_terms(CUSTOM_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "custom-products")


if __name__ == "__main__":
    add_custom_products()
