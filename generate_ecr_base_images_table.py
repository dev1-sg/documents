import requests
from jinja2 import Template

images = next(iter(requests.get("https://api.dev1-sg.com/v1/public/images/base").json().values()))

template = Template("""\
|#|Image|URI|Tag|Size(MB)|
|---|---|---|---|---|
{% for image in images -%}
|{{ image.number }}|[{{ image.image_name }}](https://gallery.ecr.aws/dev1-sg/{{ image.image_name }})|{{ image.uri }}|{{ image.latest_tag }}|{{ image.size_mb }} MB|
{% endfor -%}
""")

print(template.render(images=images))
