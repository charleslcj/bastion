import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SelectParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.select_name: str | None = None
        self.option: dict[str, str | None] | None = None
        self.options: dict[str, list[dict[str, str | None]]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "select":
            self.select_name = values.get("name")
        elif tag == "option" and self.select_name:
            self.option = {
                "value": values.get("value"),
                "data_en": values.get("data-en"),
                "data_zh": values.get("data-zh"),
                "text": "",
            }

    def handle_data(self, data: str) -> None:
        if self.option is not None:
            self.option["text"] = (self.option["text"] or "") + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self.select_name and self.option is not None:
            self.option["text"] = (self.option["text"] or "").strip()
            self.options.setdefault(self.select_name, []).append(self.option)
            self.option = None
        elif tag == "select":
            self.select_name = None


def read_options(filename: str) -> dict[str, list[dict[str, str | None]]]:
    parser = SelectParser()
    parser.feed((ROOT / filename).read_text(encoding="utf-8"))
    return parser.options


def submitted_values(options: list[dict[str, str | None]], language: str) -> list[str | None]:
    """Model the browser rule: explicit value wins; otherwise option text is submitted."""
    result: list[str | None] = []
    for option in options:
        visible_text = option[f"data_{language}"] or option["text"]
        result.append(option["value"] if option["value"] is not None else visible_text)
    return result


class FormOptionValueTests(unittest.TestCase):
    def test_quote_choices_keep_canonical_values_after_language_switches(self) -> None:
        expected = {
            "Equipment": [
                "40ft container",
                "40ft high cube",
                "20ft container",
                "45ft container",
                "Reefer container",
                "53ft dry van (FTL)",
                "Flatbed / step deck",
                "Other — see notes",
            ],
            "Service": ["Live unload", "Drop and pick", "Not sure yet"],
            "Special requirements": [
                "Nothing special — standard dry container",
                "Overweight / needs special permit",
                "Hazmat",
                "Refrigerated / temperature controlled",
                "Urgent — needs to move within 24 hours",
                "Government or military destination",
                "Other — see notes",
            ],
        }
        options = read_options("quote.html")

        self.assertEqual(set(options), set(expected))
        self.assertEqual(sum(map(len, options.values())), 18)
        for select_name, canonical_values in expected.items():
            for language in ("en", "zh", "en"):
                self.assertEqual(
                    submitted_values(options[select_name], language),
                    canonical_values,
                    f"{select_name} changed submitted values after switching to {language}",
                )

    def test_homepage_service_choices_submit_same_values_in_both_pages(self) -> None:
        canonical_values = [
            "Freight brokerage — move a shipment",
            "Drayage / transload at LA / Long Beach",
            "Warehousing / distribution",
            "Specialty / regulated freight (fuel, hazmat, reefer)",
            "Supply-chain consulting / network optimization",
            "Fractional CFO / financial operations",
            "Government teaming / subcontract",
            "Other",
        ]

        bilingual = read_options("index.html")["Service"]
        chinese_page = read_options("zh/index.html")["Service"]
        for language in ("en", "zh", "en"):
            self.assertEqual(submitted_values(bilingual, language), canonical_values)
        self.assertEqual(submitted_values(chinese_page, "zh"), canonical_values)


if __name__ == "__main__":
    unittest.main()
