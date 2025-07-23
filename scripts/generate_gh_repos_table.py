import requests
from jinja2 import Template

repos = next(iter(requests.get("https://api.dev1-sg.com/v1/public/gh/repos").json().values()))

template = Template("""\
|#|Name|Description|Clone URL|Language|Topics|Last Push|
|---|---|---|---|---|---|---|
{% for repo in repos -%}
|{{ loop.index }}|[{{ repo.name }}]({{ repo.url }})|{{ repo.description or "-" }}|{{ repo.clone_url }}|{{ repo.language or "-" }}|{{ repo.topics | join(", ") }}|{{ repo.last_push or "-" }}|
{% endfor -%}
""")

print(template.render(repos=repos))
