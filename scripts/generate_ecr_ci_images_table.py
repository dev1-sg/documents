import requests
from jinja2 import Template

images = next(iter(requests.get("https://api.dev1-sg.com/v1/public/images/ci").json().values()))

template = Template("""\
|#|Image|Group|URI|Latest Tag|Size(MB)|SHA256|Source|Last Push|
|---|---|---|---|---|---|---|---|---|
{% for image in images -%}
|{{ loop.index }}|[{{ image.image_name.split('/')[-1] }}](https://gallery.ecr.aws/dev1-sg/{{ image.image_name }})|{{ image.image_group }}|{{ image.uri }}|{{ image.latest_tag }}|{{ image.size_mb }} MB|{{ image.latest_sha }}|[https://github.com/dev1-sg/docker-ci-images/tree/main/src/{{ image.image_name.split('/')[-1] }}](https://github.com/dev1-sg/docker-ci-images/tree/main/src/{{ image.image_name.split('/')[-1] }})|{{ image.last_push }}|
{% endfor -%}
""")

print(template.render(images=images))
