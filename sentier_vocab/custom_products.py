from sentier_vocab.add_terms import add_custom_terms
from sentier_vocab.input.custom_products import CUSTOM_PRODUCTS_DATA
from sentier_vocab.input.electricity_model_terms import ELECTRICITY_MODEL_TERMS_DATA
from sentier_vocab.input.electricity_products import ELECTRICITY_PRODUCTS_DATA
from sentier_vocab.input.printed_circuit_board import PCB_PRODUCTS_DATA, PCB_MODEL_TERMS_DATA


def add_custom_products():
    add_custom_terms(CUSTOM_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "custom-products")
    add_custom_terms(
        ELECTRICITY_PRODUCTS_DATA,
        "https://vocab.sentier.dev/products/electricity/",
        "electricity-custom-products",
    )
    add_custom_terms(
        ELECTRICITY_MODEL_TERMS_DATA,
        "https://vocab.sentier.dev/model-terms/emission-factor/",
        "electricity-custom-model-terms",
    )
    add_custom_terms(
        PCB_PRODUCTS_DATA,
        "https://vocab.sentier.dev/products/electronics/",
        "pcb-product-terms",
    )
    add_custom_terms(
        PCB_MODEL_TERMS_DATA,
        "https://vocab.sentier.dev/model-terms/electronics/pcb/",
        "pcb-model-terms",
    )


if __name__ == "__main__":
    add_custom_products()
