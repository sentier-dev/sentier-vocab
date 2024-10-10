from sentier_vocab.add_terms import add_custom_terms
from sentier_vocab.input.custom_products import CUSTOM_PRODUCTS_DATA
from sentier_vocab.input.peakachu_products import ELECTRICITY_PRODUCTS_DATA
from sentier_vocab.input.peakachu_model_terms import ELECTRICITY_MODEL_TERMS_DATA


def add_custom_products():
    add_custom_terms(CUSTOM_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "custom-products")
    add_custom_terms(ELECTRICITY_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "electricity-custom-products")
    add_custom_terms(ELECTRICITY_MODEL_TERMS_DATA, "https://vocab.sentier.dev/model-terms/", "electricity-custom-model-terms")


if __name__ == "__main__":
    add_custom_products()
