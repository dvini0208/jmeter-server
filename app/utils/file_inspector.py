from pathlib import Path
import re
import xml.etree.ElementTree as ET


def find_referenced_csvs(jmx_path: Path) -> list[str]:
    refs = []

    try:
        tree = ET.parse(jmx_path)
        root = tree.getroot()

        for elem in root.iter():
            if elem.tag == "stringProp" and elem.attrib.get("name") == "filename":
                value = (elem.text or "").strip()
                if value.lower().endswith(".csv"):
                    refs.append(value)

    except ET.ParseError:
        text = jmx_path.read_text(encoding="utf-8", errors="ignore")
        refs.extend(re.findall(r'[^\\s"\']+\\.csv', text, flags=re.IGNORECASE))

    return sorted(set(refs))


def check_missing_dependencies(base_dir: Path, references: list[str]) -> list[str]:
    missing = []

    for ref in references:
        full_path = base_dir / Path(ref).name
        if not full_path.exists():
            missing.append(ref)

    return missing