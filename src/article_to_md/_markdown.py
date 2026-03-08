from html_to_markdown import convert as html_to_markdown_convert
from markdownify import MarkdownConverter


class CustomConverter(MarkdownConverter):
    def convert_var(self, el, text, parent_tags):
        """Render <var> as italic"""
        return f"*{text}*" if text else ""

    def convert_abbr(self, el, text, parent_tags):
        """Render <abbr title="...">TEXT</abbr> as TEXT (title)"""
        title = el.get("title", "")
        if title and text:
            return f"{text} ({title})"
        return text or ""

    def convert_table(self, el, text, parent_tags):
        """Delegate table rendering to html-to-markdown"""

        table_html = str(el)

        try:
            return html_to_markdown_convert(table_html)
        except Exception as e:
            print(f"Error converting table with html-to-markdown: {e}")
            return super().convert_table(el, text, parent_tags)
