import requests
from jinja2 import Template

api_data = requests.get("https://api.dev1-sg.com/v1/public/apis/rest").json()
rest_apis = next(iter(api_data.values()))

all_routes = []
for api in rest_apis:
    for route, full_path in zip(api["routes"], api["fullPaths"]):
        all_routes.append({
            "apiName": api["name"],
            "method": route["method"],
            "path": route["path"],
            "fullPath": full_path
        })

template = Template("""\
|#|API|Method|Path|Full URL|
|---|---|---|---|---|
{% for route in routes -%}
|{{ loop.index }}|{{ route.apiName }}|{{ route.method }}|{{ route.path }}|{{ route.fullPath }}|
{% endfor -%}
""")

print(template.render(routes=all_routes))
