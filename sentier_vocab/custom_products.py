from sentier_vocab.add_terms import add_custom_terms
from sentier_vocab.input.custom_products import CUSTOM_PRODUCTS_DATA
from sentier_vocab.input.electricity_model_terms import ELECTRICITY_MODEL_TERMS_DATA
from sentier_vocab.input.electricity_products import ELECTRICITY_PRODUCTS_DATA


def add_custom_products():
    out_file = add_custom_terms(CUSTOM_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "custom-products")
    created_ttls.append(
        {"graph": "https://vocab.sentier.dev/products/", "ttl_file": str(out_file.name)}
    )    
add_custom_terms(
        ELECTRICITY_PRODUCTS_DATA,
        "https://vocab.sentier.dev/products/electricity/",
        "electricity-custom-products",
    )

    out_file = created_ttls.append(
        {"graph": "https://vocab.sentier.dev/products/", "ttl_file": str(out_file.name)}
    )
    logger.info(f"Added {out_file} to outputs")
    out_file = add_custom_terms(
        ELECTRICITY_MODEL_TERMS_DATA,
        "https://vocab.sentier.dev/model-terms/emission-factor/",
        "electricity-custom-model-terms",
    )
    created_ttls.append(
        {"graph": "https://vocab.sentier.dev/model-terms/", "ttl_file": str(out_file.name)}
    )


if __name__ == "__main__":
    add_custom_products()
    with Path(Path(__file__).parent / "output" / "new_ttls.json").open(
        mode="w", encoding="utf-8"
    ) as f:
        f.write(json.dumps(created_ttls, indent=2))
