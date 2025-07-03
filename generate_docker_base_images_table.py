import requests
from jinja2 import Template

url = "https://q04rtykgt9.execute-api.us-east-1.amazonaws.com/prod/images/base"

response = requests.get(url)
response.raise_for_status()
data = response.json()

key = next(iter(data))
images = data[key]

template_str = """
|#|Image|URI|Tag|Size(MB)|
|---|---|---|---|---|
{% for image in images -%}
|{{image.number}}|{{image.image_name}}|{{image.uri}}|{{image.latest_tag}}|{{"%.2f"|format(image.size_mb)}}|
{% endfor %}
"""

template = Template(template_str)
print(template.render(images=images))
