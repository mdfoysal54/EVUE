from pathlib import Path
p=Path("backend/evu/settings.py")
s=p.read_text(encoding="utf-8")
if '"sitecontrol"' not in s:
    anchor='    "commerce",'
    if anchor not in s: raise SystemExit("Missing settings anchor; edit INSTALLED_APPS manually")
    s=s.replace(anchor, anchor+'\n    "sitecontrol",')
if 'MEDIA_URL = ' not in s:
    s += '\n# User-uploaded media: use private/object storage and signed URLs in production.\nMEDIA_URL = "/media/"\nMEDIA_ROOT = BASE_DIR / "media"\n'
p.write_text(s,encoding="utf-8")
p=Path("backend/evu/urls.py");s=p.read_text(encoding="utf-8")
if 'include("sitecontrol.urls")' not in s:
    anchor='urlpatterns = ['
    if anchor not in s: raise SystemExit("Missing urls anchor")
    s=s.replace(anchor,anchor+'\n    path("api/site/", include("sitecontrol.urls")),')
p.write_text(s,encoding="utf-8")
print("Settings and URLs updated. Review git diff before building.")
