import re
import unicodedata


# online document lib as json format from
# https://gist.github.com/samuelcolvin/4b5bb9bb163b1122ff17e29e48c10992
doc_json_url = (
    "https://gist.githubusercontent.com/"
    "samuelcolvin/4b5bb9bb163b1122ff17e29e48c10992/raw/"
    "80c5925c42f1442c24963aaf5eb1a324d47afe95/logfire_docs.json"
)


def make_doc_uri(title: str, path: str) -> str:
    uri_path = re.sub(r"\.md$", "", path)
    return (
        f"https://logfire.pydantic.dev/docs/{uri_path}/#{slugify(title, '-')}"
    )

# utility function taken unchanged from
# https://github.com/Python-Markdown/markdown/blob/3.7/markdown/extensions/toc.py#L38
def slugify(value: str, separator: str, unicode: bool = False) -> str:
    """Slugify a string, to make it URL friendly."""

    if not unicode:
        # replace extended latin characters with ascii, i.e. `žlutý` => `zluty`
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(rf"[{separator}\s]+", separator, value)
