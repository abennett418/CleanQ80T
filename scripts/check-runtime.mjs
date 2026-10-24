// The widget runs on the TV, not Node: reject syntax beyond ES5 in every shipped script.
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { parse } from 'acorn';

const app = fileURLToPath(new URL('../app/', import.meta.url));
function checkDirectory(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) checkDirectory(path);
    else if (entry.name.endsWith('.js')) parse(readFileSync(path, 'utf8'), { ecmaVersion: 5 });
  }
}
checkDirectory(app);
console.log('Packaged JavaScript parses as ES5.');
