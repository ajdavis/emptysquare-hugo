import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const tex = new TeX();
const svg = new SVG({ fontCache: 'local' });

const html = mathjax.document('', { InputJax: tex, OutputJax: svg });

const input = process.argv[2];
const node = html.convert(input, { display: false });

// outerHTML would be like <mjx-container><svg>..., innerHTML is just <svg>...
console.log(adaptor.innerHTML(node));
