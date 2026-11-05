#!/usr/bin/env python3
"""Fingerprint local JS/CSS in a built Pages artifact, never in source HTML."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re

REFERENCE=re.compile(r'(?P<attribute>\b(?:src|href))=(?P<quote>[\"\'])(?P<url>assets/[^\"\'?#]+\.(?:js|css))(?P=quote)')


def versionar(directory: Path,page='vouchers.html'):
    root=directory.resolve()
    target=(root/page).resolve()
    if not target.is_relative_to(root) or not target.is_file() or target.suffix!='.html':
        raise ValueError('Pagina fora do artefato ou inexistente')
    source=target.read_text(encoding='utf8')
    generated={}
    def rewrite(match):
        url=match.group('url');asset=(target.parent/url).resolve()
        if not asset.is_relative_to(root/'assets') or not asset.is_file():
            raise ValueError('Asset local ausente ou fora do artefato: '+url)
        data=asset.read_bytes();digest=hashlib.sha256(data).hexdigest()[:16]
        stem=re.sub(r'\.[0-9a-f]{16}$','',asset.stem)
        versioned=asset.with_name(f'{stem}.{digest}{asset.suffix}')
        if versioned.exists() and versioned.read_bytes()!=data:raise ValueError('Hash em conflito')
        versioned.write_bytes(data)
        output=versioned.relative_to(target.parent).as_posix()
        generated[url]=output
        return f'{match.group("attribute")}={match.group("quote")}{output}{match.group("quote")}'
    updated=REFERENCE.sub(rewrite,source)
    if not generated:raise ValueError('Nenhum asset local encontrado para versionar')
    target.write_text(updated,encoding='utf8')
    return generated


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--page',default='vouchers.html')
    args=parser.parse_args()
    result=versionar(args.directory,args.page)
    print(f'PAGES_ASSETS_VERSIONED_OK count={len(result)} page={args.page}')


if __name__=='__main__':main()
