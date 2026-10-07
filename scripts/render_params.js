// Render a studio parameter set to a print-ready SVG (all text outlined).
//
//   npm i opentype.js@1.3.4
//   node scripts/render_params.js params.json out.svg [--background]
//
// params.json is what the studio's "Copy parameters" button gives you; missing
// keys fall back to the defaults in design/studio/generator.js.
const fs = require("fs");
const path = require("path");
const opentype = require("opentype.js");
const gen = require("../design/studio/generator.js");

const [, , inFile, outFile, ...flags] = process.argv;
if (!inFile || !outFile) {
  console.error("usage: node scripts/render_params.js params.json out.svg [--background]");
  process.exit(1);
}
const params = JSON.parse(fs.readFileSync(inFile, "utf8"));
if (flags.includes("--background")) params.exportBackground = true;

const dir = path.join(__dirname, "..", "design", "studio", "fonts");
const load = (file) => {
  const b = fs.readFileSync(path.join(dir, file));
  return opentype.parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
};
const fonts = { [gen.FALLBACK_FONT.id]: load(gen.FALLBACK_FONT.file) };
const p = Object.assign({}, gen.DEFAULTS, params);
for (const id of new Set([p.headFont, p.subFont, gen.DEFAULTS.headFont])) {
  fonts[id] = load(gen.FONTS[id].file);
}
fs.writeFileSync(outFile, gen.generate(params, fonts, { forExport: true }));
console.log("wrote", outFile);
