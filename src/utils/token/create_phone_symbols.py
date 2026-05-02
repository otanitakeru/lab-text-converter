import os

import yaml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_phone_symbols(input_file_path: str, output_file_path: str) -> None:

    with open(input_file_path, "r", encoding="utf-8") as f:
        kana2phone_map = yaml.safe_load(f)

    phones = list(set(phone for phones in kana2phone_map.values() for phone in phones))
    phones.extend(["a:", "i:", "u:", "e:", "o:"])
    phones = sorted(phones)

    with open(output_file_path, "w", encoding="utf-8") as f:
        for phone in phones:
            f.write(phone + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file_path",
        type=str,
        default=os.path.join(CURRENT_DIR, "kana2phone.yaml"),
    )
    parser.add_argument(
        "-o",
        "--output_file_path",
        type=str,
        default=os.path.join(CURRENT_DIR, "phone_symbols.txt"),
    )
    args = parser.parse_args()

    get_phone_symbols(args.input_file_path, args.output_file_path)
