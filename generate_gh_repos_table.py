import requests
from jinja2 import Template

repos = next(iter(requests.get("https://api.dev1-sg.com/v1/public/repos/gh").json().values()))

template = Template("""\
|#|Name|Description|Language|Last Push|
|---|---|---|---|---|
{% for repo in repos -%}
|{{ loop.index }}|[{{ repo.name }}]({{ repo.url }})|{{ repo.description or "-" }}|{{ repo.language or "-" }}|{{ repo.last_push or "-" }}|
{% endfor -%}
""")

print(template.render(repos=repos))
