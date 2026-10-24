import json
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def metadata(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("Missing YAML frontmatter")
    end = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:end]))


class PackageTests(unittest.TestCase):
    def test_frontmatter(self):
        parsed = metadata(ROOT / "SKILL.md")
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed["name"], ROOT.name)
        self.assertIsInstance(parsed["description"], str)
        self.assertTrue(parsed["description"].strip())

    def test_relative_links(self):
        for file in ROOT.rglob("*.md"):
            for link in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", file.read_text()):
                if link.startswith(("https://", "http://", "#")):
                    continue
                target = (file.parent / link.split("#", 1)[0]).resolve()
                with self.subTest(file=file.name, link=link):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file())

    def test_case_contract(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["input"])
                self.assertTrue(case["must"])
                self.assertTrue(case["must_not"])
        self.assertTrue(any(case.get("held_out") for case in cases))

    def test_portable_examples(self):
        for file in ROOT.rglob("*"):
            if file.suffix not in {".md", ".json"}:
                continue
            text = file.read_text(encoding="utf-8")
            with self.subTest(file=file.name):
                self.assertNotRegex(text, r"/home/[^/\s]+/|[A-Z]:\\Users\\")
                self.assertNotIn("storageState.json", text)


if __name__ == "__main__":
    unittest.main()
