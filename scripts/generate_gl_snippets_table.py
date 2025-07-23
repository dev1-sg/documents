import requests
from jinja2 import Template

snippets = next(iter(requests.get("https://api.dev1-sg.com/v1/public/snippets/gl").json().values()))

template = Template("""\
|#|Name|Raw URL|ID|Last Updated|
|---|---|---|---|---|
{% for snippet in snippets -%}
|{{ loop.index }}|{{ snippet.name }}|{{ snippet.raw_url }}|{{ snippet.id }}|{{ snippet.updated_at }}|
{% endfor -%}
""")

print(template.render(snippets=snippets))
