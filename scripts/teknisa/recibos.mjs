import { mkdir, readFile, writeFile, rename, open, unlink } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';

export const PRIVATE_DIRECTORY = fileURLToPath(new URL('../../tmp/teknisa/', import.meta.url));
export function createFileJournal(directory = PRIVATE_DIRECTORY) {
  const filename = id => {
    if (!/^[a-f0-9-]{36}$/.test(id)) throw new Error('Identificador de recibo inválido.');
    return join(directory, `${id}.json`);
  };
  return {
    directory,
    async save(record) {
      await mkdir(directory, { recursive: true });
      const destination = filename(record.id), temp = `${destination}.${randomUUID()}.tmp`;
      await writeFile(temp, JSON.stringify(record, null, 2), { encoding: 'utf8', mode: 0o600, flag: 'wx' });
      await rename(temp, destination);
    },
    async load(id) { return JSON.parse(await readFile(filename(id), 'utf8')); },
    async lock(target, callback) {
      await mkdir(directory, { recursive: true });
      const key = createHash('sha256').update(`${target.organization}:${target.branch}`).digest('hex');
      const path = join(directory, `${key}.lock`);
      let handle;
      try { handle = await open(path, 'wx', 0o600); }
      catch (error) {
        if (error.code === 'EEXIST') throw new Error('Há uma execução local nessa unidade. Confira o processo e o recibo antes de remover um bloqueio antigo.');
        throw error;
      }
      try {
        await handle.writeFile(JSON.stringify({ owner: randomUUID(), createdAt: new Date().toISOString() }));
        return await callback();
      } finally { await handle.close(); await unlink(path); }
    },
  };
}
