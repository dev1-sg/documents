import requests
from jinja2 import Template

url = "https://api.dev1-sg.com/v1/public/repos/gh"

response = requests.get(url)
response.raise_for_status()
data = response.json()

key = next(iter(data))
images = data[key]

template_str = """
| # | Name | Description | Language | Last Push |
| --- | --- | --- | --- | --- |
{% for repo in repos %}
| {{ loop.index }} | [{{ repo.name }}]({{ repo.url }}) | {{ repo.description or "-" }} | {{ repo.language or "-" }} | {{ repo.last_push or "-" }} |
{% endfor %}
"""

template = Template(template_str)
print(template.render(repos=images))
