import re
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlparse

import curl_cffi
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from cyclopts import App, Parameter
from readabilipy import simple_json_from_html_string
from trafilatura import extract
from unidecode import unidecode

from article_to_md._ad import remove_by_cosmetic_filters
from article_to_md._cache import get_easylist_filters
from article_to_md._markdown import CustomConverter

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

MethodChoice = Literal["readability", "trafilatura", "raw"]
FavorChoice = Literal["recall", "precision"]

app = App(help_formatter="plain")


def create_filename_from_meta(soup: BeautifulSoup, url: str, title: str | None = None) -> str:
    final_title = ""

    if title is not None:
        final_title = title
    else:
        html_title_tag = soup.title
        if html_title_tag and html_title_tag.string:
            final_title = html_title_tag.string.strip()

    if not final_title:
        parsed_url = urlparse(url)
        url_path_segment = f"{parsed_url.netloc}{parsed_url.path}".strip("/")

        # Replace common separators (slashes, dots) with spaces for processing
        final_title = re.sub(r"[./-]", " ", url_path_segment)

    ascii_title = unidecode(final_title)
    safe_title = re.sub(r"[^a-zA-Z0-9.\- ]", "", ascii_title)
    safe_title = safe_title.replace(" ", "_")
    safe_title = re.sub(r"_+", "_", safe_title).strip("_")

    # Trim title to avoid path limits
    safe_title = safe_title[:192]

    # Remove milliseconds
    timestamp = datetime.now(UTC).isoformat().replace(":", "-").split(".")[0]

    return f"{safe_title}_{timestamp}"


@app.default
def main(
    sources: list[str],
    /,
    *,
    method: MethodChoice = "readability",
    favor: FavorChoice | None = None,
    remove_ads: bool = False,
    strip_tag: Annotated[tuple[str, ...], Parameter(negative="--no-strip")] = ("img",),
    output: Annotated[Path | None, Parameter(name=["-o", "--output"])] = None,
):
    """
    Convert an article or web page to Markdown.

    Parameters
    ----------
    sources : list[str]
        One or more URLs or paths to local HTML files.
    method : MethodChoice, optional
        The extraction engine to use.
    favor : FavorChoice, optional
        Whether to favor 'precision' or 'recall' when using trafilatura.
    remove_ads : bool, optional
        Apply EasyList cosmetic filters to remove ads before processing.
    strip_tag : tuple[str, ...], optional
        HTML tag to strip from the final output. Repeat this flag to remove multiple tags. Use --no-strip to disable.
    output : Path, optional
        Output file path, directory, or '-' for stdout. If not specified, an auto-generated file name is used.
    """
    write_to_stdout = output == Path("-")

    if output and not write_to_stdout:
        if len(sources) > 1 and not output.is_dir():
            print(
                "Error: A single output file path cannot be used with multiple sources. Please specify a directory.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    for source in sources:
        parsed = urlparse(source)
        is_url = all([parsed.scheme, parsed.netloc])

        if is_url:
            url = source
            request = curl_cffi.get(source, impersonate="chrome")
            request.raise_for_status()
            html = request.text
        else:
            path = Path(source)
            url = path.name
            if not path.exists():
                print(f"Error: File or URL not found: {source}", file=sys.stderr)
                raise SystemExit(1)

            html = path.read_text(encoding="utf-8")

        soup = BeautifulSoup(html, "lxml")

        if remove_ads:
            soup = remove_by_cosmetic_filters(soup, get_easylist_filters())

        title = content = None

        if method == "readability":
            article = simple_json_from_html_string(str(soup), use_readability=True)
            title = article.get("title")
            content = article.get("content")

        if method == "trafilatura" or not content:
            common_kwargs = {
                "filecontent": str(soup),
                "include_comments": False,
                "output_format": "html",
                "include_tables": True,
                "deduplicate": True,
            }

            dynamic_kwargs = {}
            if favor == "precision":
                dynamic_kwargs["favor_precision"] = True
            elif favor == "recall":
                dynamic_kwargs["favor_recall"] = True

            content = extract(**common_kwargs, **dynamic_kwargs)

        if method == "raw" or not content:
            content = str(soup)

        filename = create_filename_from_meta(soup, url, title)

        markdown = CustomConverter(
            heading_style="ATX", bs4_options="lxml", newline_style="BACKSLASH", strip=list(strip_tag), autolinks=False
        ).convert(content)

        if write_to_stdout:
            sys.stdout.write(markdown)
            if len(sources) > 1 and source != sources[-1]:
                sys.stdout.write("\n\n")
        else:
            gen_filename = f"{create_filename_from_meta(soup, url, title)}.md"

            if output is None:
                target_path = Path(gen_filename)
            elif output.is_dir():
                target_path = output / gen_filename
            else:
                target_path = output

            target_path.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    app()
