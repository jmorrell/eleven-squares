"""Inline opentype.js and the generator into design/studio/index.html (the published page)."""
import os
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "design", "studio")
src = open(os.path.join(d, "index.src.html")).read()
src = src.replace("/*OPENTYPE*/", open(os.path.join(d, "vendor", "opentype.min.js")).read().replace("</script", "<\\/script"))
src = src.replace("/*GENERATOR*/", open(os.path.join(d, "generator.js")).read())
open(os.path.join(d, "index.html"), "w").write(src)
print("wrote design/studio/index.html", len(src) // 1024, "KB")
