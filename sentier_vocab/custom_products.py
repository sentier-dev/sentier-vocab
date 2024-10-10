import json
from pathlib import Path

from loguru import logger

from sentier_vocab.add_terms import add_custom_terms
from sentier_vocab.input.custom_products import CUSTOM_PRODUCTS_DATA

created_ttls = []
def add_custom_products():
    out_file = add_custom_terms(CUSTOM_PRODUCTS_DATA, "https://vocab.sentier.dev/products/", "custom-products")
    created_ttls.append({"graph": "https://vocab.sentier.dev/products/",
                         "ttl_file": str(out_file.name)})
    logger.info(f"Added {out_file} to outputs")
    


if __name__ == "__main__":
    add_custom_products()
    with Path("new_ttls.json").open(mode="w", encoding="utf-8") as f:
        f.write(json.dumps(created_ttls, indent=2))
