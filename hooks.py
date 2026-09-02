"""MkDocs hook: generates the indicator reference table from source code.

The table is injected into any page that contains the placeholder comment
``<!-- INDICATORS_TABLE -->``.  This keeps docs and code in sync — only
``indicator_dims.py`` needs updating when indicators change.
"""

from avenir_goals_scenario._runner.indicator_dims import list_indicators


def on_page_markdown(markdown: str, page, **kwargs) -> str:
    if "<!-- INDICATORS_TABLE -->" not in markdown:
        return markdown

    def _fmt_dim(d) -> str:
        if isinstance(d, str):
            return f"`{d}`"
        if d.labels:
            labels = ", ".join(d.labels)
            return f"`{d.name}` [{labels}]"
        return f"`{d.name}`"

    rows = [
        "| Indicator | Description | Columns |",
        "| :--- | :--- | :--- |",
    ]
    for name, spec in list_indicators().items():
        dim_parts = [_fmt_dim(d) for d in spec.dims] + ["`year`"]
        dims_cell = "<br>".join(dim_parts)
        rows.append(f"| `{name}` | {spec.description} | {dims_cell} |")

    table = "\n".join(rows)
    return markdown.replace("<!-- INDICATORS_TABLE -->", table)
