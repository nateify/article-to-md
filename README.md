# article-to-md
A CLI tool to extract core content from webpages or local HTML and convert it to Markdown.

```
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help (-h)  Display this message and exit.                                                                          │
│ --version    Display application version.                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Parameters ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  SOURCE --source                [required]                                                                         │
│    --method                       [choices: readability, trafilatura, raw] [default: readability]                    │
│    --favor                        [choices: recall, precision]                                                       │
│    --remove-ads --no-remove-ads   [default: False]                                                                   │
│    --strip-tag --empty-strip-tag                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Installation

[uv](https://docs.astral.sh/uv/) is recommended to install the package in a managed environment:

    uv tool install article-to-md

**Note**: To use the readability method, Node.js (v14+) must be installed on your system. Without Node.js, the tool uses Python-based extraction.

## Usage

From a publicly accessible web page:

```bash
article-to-md https://example.com/article
```

From a local HTML file:

```bash
article-to-md /path/to/file.html
```

Advanced options:

- `--remove-ads` - Basic ad removal from the DOM using generic cosmetic filters from [EasyList](https://easylist.to/)
- `--method` - Affects pre-processing of the DOM before conversion to Markdown.
  - `readability` (default) - Uses [ReadabiliPy](https://github.com/alan-turing-institute/ReadabiliPy) which can use the original Readability.js Node package when Node is present on the system.
  - `trafilatura` - Uses the [Trafilatura](https://trafilatura.readthedocs.io/en/latest/index.html) pure Python library
  - `raw` - Sends the full DOM to be converted
- `--favor` - Only used with `--method trafilatura` to control options [documented here](https://trafilatura.readthedocs.io/en/latest/usage-cli.html#optimizing-for-precision-and-recall).
- `--strip-tag` - An HTML tag to be stripped from the DOM before conversion
  - This argument can be supplied multiple times 
  - By default, `<img>` tags are stripped; use `--empty-strip-tag` to keep them.

## Features

- Stealth Requests: Uses curl_cffi to impersonate a Chrome browser and avoid bot detection.
- Enhanced Markdown:
  - Converts `<var>` to italics. 
  - Includes `<abbr>` titles in the text output.
  - Renders Markdown tables from HTML tables