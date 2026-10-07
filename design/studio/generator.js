/* s(11) design generator — shared by the browser studio and scripts/render_params.js.
 *
 * generate(params, fonts, {forExport}) -> SVG string.
 * `fonts` maps font id -> opentype.js Font (plus FALLBACK_FONT for missing glyphs).
 * Every random choice comes from a seeded stream per subsystem, so changing one
 * control (e.g. ghost count) doesn't reshuffle the others.
 */
(function (root) {
  "use strict";

  const W = 1200, H = 1600;

  // Walter Trump's 1979 packing of 11 unit squares, side s(11) = 3.87708359…
  // (numerical reconstruction, see scripts/solve_packing.py). First 5 are tilted.
  const PACKING = {"side":3.87708359,"tilted":5,"squares":[[[1.636187988,3.113084185],[2.400187399,2.467867245],[3.045404339,3.231866656],[2.281404928,3.877083596]],[[0.735966619,2.564442536],[1.499965994,1.919225553],[2.145182977,2.683224927],[1.381183603,3.328441911]],[[1.483916698,1.90022157],[2.247916113,1.255004635],[2.893133048,2.019004051],[2.129133633,2.664220986]],[[-4e-08,1.877083611],[0.763999325,1.231866617],[1.409216319,1.995865982],[0.645216954,2.641082976]],[[0.747949975,1.212862674],[1.511949338,0.567645677],[2.157166335,1.33164504],[1.393166972,1.976862037]],[[0.0,2.87708359],[1.0,2.87708359],[1.0,3.87708359],[0.0,3.87708359]],[[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0]],[[1.87708359,0.0],[2.87708359,0.0],[2.87708359,1.0],[1.87708359,1.0]],[[2.87708359,0.0],[3.87708359,0.0],[3.87708359,1.0],[2.87708359,1.0]],[[2.87708359,0.999999974],[3.87708359,0.999999974],[3.87708359,1.999999974],[2.87708359,1.999999974]],[[2.87708359,2.032558583],[3.87708359,2.032558583],[3.87708359,3.032558583],[2.87708359,3.032558583]]]};

  const FONTS = {
    "inter-800": { label: "Inter ExtraBold", file: "inter-latin-800-normal.woff" },
    "inter-900": { label: "Inter Black", file: "inter-latin-900-normal.woff" },
    "archivo-black": { label: "Archivo Black", file: "archivo-black-latin-400-normal.woff" },
    "syne-800": { label: "Syne ExtraBold", file: "syne-latin-800-normal.woff" },
    "unbounded-800": { label: "Unbounded ExtraBold", file: "unbounded-latin-800-normal.woff" },
    "anton": { label: "Anton", file: "anton-latin-400-normal.woff" },
    "big-shoulders-900": { label: "Big Shoulders Display Black", file: "big-shoulders-display-latin-900-normal.woff" },
    "rubik-mono-one": { label: "Rubik Mono One", file: "rubik-mono-one-latin-400-normal.woff" },
    "chakra-petch-700": { label: "Chakra Petch Bold", file: "chakra-petch-latin-700-normal.woff" },
    "fraunces-900": { label: "Fraunces Black", file: "fraunces-latin-900-normal.woff" },
    "dm-serif-display": { label: "DM Serif Display", file: "dm-serif-display-latin-400-normal.woff" },
    "instrument-serif": { label: "Instrument Serif", file: "instrument-serif-latin-400-normal.woff" },
    "instrument-serif-italic": { label: "Instrument Serif Italic", file: "instrument-serif-latin-400-italic.woff" },
    "ibm-plex-serif-italic": { label: "IBM Plex Serif Italic", file: "ibm-plex-serif-latin-400-italic.woff" },
    "vt323": { label: "VT323 (terminal)", file: "vt323-latin-400-normal.woff" },
    "silkscreen-700": { label: "Silkscreen (pixel)", file: "silkscreen-latin-700-normal.woff" },
    "major-mono-display": { label: "Major Mono Display", file: "major-mono-display-latin-400-normal.woff" },
    "space-mono-700": { label: "Space Mono Bold", file: "space-mono-latin-700-normal.woff" },
    "space-mono-400": { label: "Space Mono", file: "space-mono-latin-400-normal.woff" },
    "jetbrains-mono-800": { label: "JetBrains Mono ExtraBold", file: "jetbrains-mono-latin-800-normal.woff" },
    "jetbrains-mono-400": { label: "JetBrains Mono", file: "jetbrains-mono-latin-400-normal.woff" },
    "ibm-plex-mono-700": { label: "IBM Plex Mono Bold", file: "ibm-plex-mono-latin-700-normal.woff" },
    "ibm-plex-mono-400": { label: "IBM Plex Mono", file: "ibm-plex-mono-latin-400-normal.woff" },
  };
  const FALLBACK_FONT = { id: "fallback", file: "fallback-dejavu-mono.woff" };

  const DEFAULTS = {
    seedGhosts: 11,                // each subsystem has its own seed so you can
    seedSlices: 11,                // lock one and scrub another
    seedShade: 11,
    seedGrain: 11,
    bg: "#0a0a0c",
    ink: "#ece6d8",
    palette: ["#ff2d55", "#00e5ff", "#ffd400", "#2f6bff", "#39ff88", "#ff7a00", "#ffffff", "#c86bff", "#ff4fa3"],

    packSize: 600,
    packX: 0,                      // offset from centre
    packY: 260,
    squareStyle: "solid",          // solid | outline
    tiltFill: "#ece6d8",
    axisFill: "#3c424b",
    axisShade: 0.12,
    tiltShade: 0,
    gap: 3,
    outline: true,
    outlineColor: "#ece6d8",
    outlineWidth: 3,
    ghostsThroughGaps: true,

    ghostCount: 34,
    ghostWhich: "all",             // all | tilted | axis
    ghostScaleBias: 1,             // >1 favours small boxes, <1 favours large
    ghostScaleMin: 1.0,
    ghostScaleMax: 1.25,
    ghostAngle: 12,
    ghostAxisAngle: 4,
    ghostJitter: 0.3,
    ghostStroke: 1.5,
    ghostStrokeVar: 0.33,
    ghostOpacityMin: 0.25,
    ghostOpacityMax: 0.75,
    ghostBoxChance: 0.25,
    ghostShiftChance: 0.25,
    ghostShiftMax: 60,
    ghostColorMode: "palette",     // palette | single
    ghostColor: "#00e5ff",
    sliceChance: 0.3,
    sliceShift: 80,
    sliceReach: 200,
    sliceHeightMin: 4,
    sliceHeightMax: 24,
    sliceGapMin: 10,
    sliceGapMax: 50,

    headText: "Optimal",
    headFont: "inter-800",
    headSize: 170,
    headX: 0,
    headY: 1270,
    headTracking: 0,
    headColor: "#ece6d8",
    splitAmount: 5,
    splitA: "#00e5ff",
    splitB: "#ff2d55",
    splitOpacity: 0.8,
    headSlicePos: 0.27,            // slice top, as fraction of size above baseline
    headSliceHeight: 0.17,
    headSliceShift: 26,
    headSlice2: false,
    headSlice2Pos: 0.62,
    headSlice2Height: 0.08,
    headSlice2Shift: -18,

    subText: "∀ P : Packing 11,  side P ≥ 3.87708359…",
    subFont: "space-mono-400",
    subSize: 24,
    subX: 0,
    subY: 1360,
    subTracking: 1,
    subColor: "#ece6d8",
    subOpacity: 1,

    grainCount: 0,
    grainOpacityMax: 0.4,
    grainSize: 2,
    grainColourChance: 0.4,
    exportBackground: false,
  };

  // ------------------------------------------------------------- utilities
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function stream(seed, salt) {
    let h = 2166136261 ^ (seed | 0);
    h = Math.imul(h ^ salt, 16777619);
    h = Math.imul(h ^ (h >>> 13), 0x5bd1e995);
    const r = mulberry32(h ^ (h >>> 15));
    const api = {
      next: r,
      uniform: (a, b) => a + (b - a) * r(),
      choice: (arr) => arr[Math.floor(r() * arr.length) % arr.length],
      gauss: (mu, sd) => {
        const u = 1 - r(), v = r();
        return mu + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
      },
    };
    return api;
  }
  const f2 = (v) => (Math.round(v * 100) / 100).toString();
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  function hexToRgb(h) {
    const m = /^#?([0-9a-f]{6})$/i.exec(h || "");
    const n = m ? parseInt(m[1], 16) : 0;
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function shade(hex, t) {  // t in [-1, 1]: towards black / white
    const c = hexToRgb(hex).map((v) => Math.round(t >= 0 ? v + (255 - v) * t : v * (1 + t)));
    return "#" + c.map((v) => v.toString(16).padStart(2, "0")).join("");
  }

  // ------------------------------------------------------------- text → outlines
  function layoutText(str, fontId, size, tracking, fonts) {
    const main = fonts[fontId] || fonts[DEFAULTS.headFont];
    const fb = fonts[FALLBACK_FONT.id];
    const glyphs = [];
    let x = 0, prev = null;
    for (const ch of String(str)) {
      let font = main, g = main.charToGlyph(ch);
      if ((!g || g.index === 0) && ch !== " " && fb) {
        const g2 = fb.charToGlyph(ch);
        if (g2 && g2.index !== 0) { font = fb; g = g2; }
      }
      const k = size / font.unitsPerEm;
      if (prev && prev.font === font) x += font.getKerningValue(prev.g, g) * k;
      glyphs.push({ font, g, x, k });
      x += (g.advanceWidth || 0) * k + tracking;
      prev = { font, g };
    }
    return { glyphs, width: Math.max(0, x - tracking) };
  }
  function textPath(str, fontId, size, cx, y, tracking, fonts) {
    const L = layoutText(str, fontId, size, tracking, fonts);
    const x0 = cx - L.width / 2;
    return L.glyphs.map(({ font, g, x }) => g.getPath(x0 + x, y, size).toPathData(2)).join("");
  }

  // ------------------------------------------------------------- geometry
  function toPx(pts, x, y, size, side) {
    const u = size / side;
    return pts.map(([a, b]) => [x + a * u, y + (side - b) * u]);
  }
  const polyD = (pts) => "M" + pts.map(([a, b]) => f2(a) + "," + f2(b)).join("L") + "Z";

  function ghostSquares(p, k) {
    const r = stream(p.seedGhosts, 1000 + k);
    const S = PACKING.side, c = S / 2;
    const lo = p.ghostScaleMin, hi = Math.max(lo, p.ghostScaleMax);
    const f = lo + (hi - lo) * Math.pow(r.next(), Math.max(0.05, p.ghostScaleBias));
    const sq = PACKING.squares.map((q, i) => {
      const mx = q.reduce((s, v) => s + v[0], 0) / 4;
      const my = q.reduce((s, v) => s + v[1], 0) / 4;
      const da = (r.gauss(0, 1) * (i < PACKING.tilted ? p.ghostAngle : p.ghostAxisAngle) * Math.PI) / 180;
      const tx = r.gauss(0, p.ghostJitter), ty = r.gauss(0, p.ghostJitter);
      const ca = Math.cos(da), sa = Math.sin(da);
      return q.map(([a, b]) => [
        (mx + tx - c) * f + c + (a - mx) * ca - (b - my) * sa,
        (my + ty - c) * f + c + (a - mx) * sa + (b - my) * ca,
      ]);
    });
    return {
      sq, f,
      colour: p.ghostColorMode === "single" ? p.ghostColor : r.choice(p.palette),
      dx: r.next() < p.ghostShiftChance ? r.uniform(-p.ghostShiftMax, p.ghostShiftMax) : 0,
      op: r.uniform(p.ghostOpacityMin, Math.max(p.ghostOpacityMin, p.ghostOpacityMax)),
      width: Math.max(0.1, p.ghostStroke * (1 + (r.next() * 2 - 1) * p.ghostStrokeVar)),
      box: r.next() < p.ghostBoxChance,
    };
  }

  // ------------------------------------------------------------- main
  function generate(params, fonts, opts) {
    const p = Object.assign({}, DEFAULTS, params || {});
    if (params && params.seed != null) {
      for (const k of ["seedGhosts", "seedSlices", "seedShade", "seedGrain"]) if (params[k] == null) p[k] = params.seed;
    }
    const forExport = !!(opts && opts.forExport);
    const out = [];
    const add = (s) => out.push(s);
    const S = PACKING.side;
    const A = p.packSize, X = (W - A) / 2 + p.packX, Y = p.packY;

    add(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${W} ${H}"` +
        (forExport ? ` width="12in" height="16in"` : ` preserveAspectRatio="xMidYMid meet"`) + `>`);
    add(`<title>${esc(p.headText)} — s(11) = 3.87708359…</title>`);
    if (forExport) add(`<metadata id="params">${esc(JSON.stringify(p))}</metadata>`);
    if (!forExport || p.exportBackground) add(`<rect id="shirt" width="${W}" height="${H}" fill="${p.bg}"/>`);

    // ghosts: rejected arrangements, each in the (larger) box it would need
    add(`<g id="sq-ghosts" fill="none" stroke-linejoin="round">`);
    for (let k = 0; k < p.ghostCount; k++) {
      const g = ghostSquares(p, k);
      add(`<g stroke="${g.colour}" stroke-width="${f2(g.width)}" opacity="${g.op.toFixed(2)}"` +
          (g.dx ? ` transform="translate(${f2(g.dx)},0)"` : "") + `>`);
      g.sq.forEach((q, i) => {
        const tilted = i < PACKING.tilted;
        if (p.ghostWhich === "tilted" && !tilted) return;
        if (p.ghostWhich === "axis" && tilted) return;
        add(`<path d="${polyD(toPx(q, X, Y, A, S))}"/>`);
      });
      if (g.box) {
        const d = (A * (g.f - 1)) / 2;
        add(`<rect x="${f2(X - d)}" y="${f2(Y - d)}" width="${f2(A * g.f)}" height="${f2(A * g.f)}"/>`);
      }
      add(`</g>`);
    }
    add(`</g>`);

    // tracking slips on the ghost layer only
    if (p.ghostCount > 0 && p.sliceChance > 0) {
      const r = stream(p.seedSlices, 7);
      let y = Y - p.sliceReach, n = 0;
      while (y < Y + A + p.sliceReach) {
        const h = r.uniform(p.sliceHeightMin, Math.max(p.sliceHeightMin, p.sliceHeightMax));
        if (r.next() < p.sliceChance) {
          const id = `sq-gs${n++}`, dx = r.uniform(-p.sliceShift, p.sliceShift);
          add(`<clipPath id="${id}"><rect x="0" y="${f2(y)}" width="${W}" height="${h}"/></clipPath>`);
          add(`<g clip-path="url(#${id})"><rect x="0" y="${f2(y)}" width="${W}" height="${h}" fill="${p.bg}"/>` +
              `<use href="#sq-ghosts" xlink:href="#sq-ghosts" transform="translate(${f2(dx)},0)"/></g>`);
        }
        y += h + r.uniform(p.sliceGapMin, Math.max(p.sliceGapMin, p.sliceGapMax));
      }
    }

    // the packing, clean
    if (!p.ghostsThroughGaps) add(`<rect x="${f2(X)}" y="${f2(Y)}" width="${A}" height="${A}" fill="${p.bg}"/>`);
    const rs = stream(p.seedShade, 3);
    PACKING.squares.forEach((q, i) => {
      const tilted = i < PACKING.tilted;
      const t = rs.next() * 2 - 1;
      const fill = tilted ? shade(p.tiltFill, t * p.tiltShade) : shade(p.axisFill, t * p.axisShade);
      const d = polyD(toPx(q, X, Y, A, S));
      if (p.squareStyle === "outline") {
        add(`<path d="${d}" fill="none" stroke="${fill}" stroke-width="${f2(Math.max(p.gap, 1))}" stroke-linejoin="round"/>`);
      } else {
        add(`<path d="${d}" fill="${fill}"` + (p.gap > 0 ? ` stroke="${p.bg}" stroke-width="${f2(p.gap)}" stroke-linejoin="round"` : "") + `/>`);
      }
    });
    if (p.outline) {
      add(`<rect x="${f2(X)}" y="${f2(Y)}" width="${A}" height="${A}" fill="none" stroke="${p.outlineColor}" stroke-width="${f2(p.outlineWidth)}"/>`);
    }

    // headline: RGB split + tracking slips
    if (p.headText) {
      const d = textPath(p.headText, p.headFont, p.headSize, W / 2 + p.headX, p.headY, p.headTracking, fonts);
      const sa = p.splitAmount;
      const so = p.splitOpacity.toFixed(2);
      add(`<g id="sq-head">`);
      if (sa) {
        add(`<path d="${d}" fill="${p.splitA}" opacity="${so}" transform="translate(${f2(-sa)},0)"/>`);
        add(`<path d="${d}" fill="${p.splitB}" opacity="${so}" transform="translate(${f2(sa)},0)"/>`);
      }
      add(`<path d="${d}" fill="${p.headColor}"/>`);
      const slices = [[p.headSlicePos, p.headSliceHeight, p.headSliceShift]];
      if (p.headSlice2) slices.push([p.headSlice2Pos, p.headSlice2Height, p.headSlice2Shift]);
      slices.forEach(([pos, hh, dx], i) => {
        if (!hh || !dx) return;
        const sy = p.headY - pos * p.headSize, sh = hh * p.headSize, id = `sq-hs${i}`;
        add(`<clipPath id="${id}"><rect x="0" y="${f2(sy)}" width="${W}" height="${f2(sh)}"/></clipPath>`);
        add(`<g clip-path="url(#${id})"><rect x="0" y="${f2(sy)}" width="${W}" height="${f2(sh)}" fill="${p.bg}"/>`);
        if (sa) add(`<path d="${d}" fill="${p.splitA}" opacity="${so}" transform="translate(${f2(dx + Math.sign(dx) * sa * 1.6)},0)"/>`);
        add(`<path d="${d}" fill="${p.headColor}" transform="translate(${f2(dx)},0)"/></g>`);
      });
      add(`</g>`);
    }

    if (p.subText) {
      add(`<path d="${textPath(p.subText, p.subFont, p.subSize, W / 2 + p.subX, p.subY, p.subTracking, fonts)}" fill="${p.subColor}" opacity="${p.subOpacity}"/>`);
    }
    if (p.grainCount > 0) {
      const r = stream(p.seedGrain, 9);
      add(`<g id="sq-grain">`);
      for (let i = 0; i < p.grainCount; i++) {
        const s = f2(p.grainSize * r.uniform(0.6, 1.5));
        const c = r.next() < p.grainColourChance ? r.choice(p.palette) : p.ink;
        add(`<rect x="${f2(r.uniform(0, W))}" y="${f2(r.uniform(0, H))}" width="${s}" height="${s}" fill="${c}" opacity="${r.uniform(0.1, p.grainOpacityMax).toFixed(2)}"/>`);
      }
      add(`</g>`);
    }
    add(`</svg>`);
    return out.join("\n");
  }

  const api = { W, H, PACKING, FONTS, FALLBACK_FONT, DEFAULTS, generate };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SquaresGen = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
