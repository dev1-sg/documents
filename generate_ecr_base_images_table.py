import requests
from jinja2 import Template

url = "https://api.dev1-sg.com/v1/public/images/base"

response = requests.get(url)
response.raise_for_status()
data = response.json()

key = next(iter(data))
images = data[key]

template_str = """
|#|Image|URI|Tag|Size(MB)|
|---|---|---|---|---|
{% for image in images -%}
|{{image.number}}|[{{image.image_name}}](https://gallery.ecr.aws/dev1-sg/{{image.image_name}})|{{image.uri}}|{{image.latest_tag}}|{{image.size_mb}} MB|
{% endfor %}
"""

template = Template(template_str)
print(template.render(images=images))
