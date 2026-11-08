"""Command line entry point. Examples: python -m gitrex demo, collect, render."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from .github import collect, GithubError
from .render import render, PACKAGE_ROOT


def _atomic_write(path:Path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def main(argv=None):
    parser=argparse.ArgumentParser(description='GitRex - a T-Rex fueled by GitHub activity')
    sub=parser.add_subparsers(dest='command',required=True)
    demo=sub.add_parser('demo',help='Offline generated sample, no GitHub token')
    live=sub.add_parser('live',help='Fetch public GitHub contributions and render')
    collect_p=sub.add_parser('collect',help='Fetch public activity into a snapshot JSON')
    render_p=sub.add_parser('render',help='Render existing snapshot JSON')
    for p in (demo,live,render_p):
        p.add_argument('--output-dir',default='output')
        p.add_argument('--width',type=int,default=720)
        p.add_argument('--frames',type=int,default=12)
    for p in (live,collect_p):
        p.add_argument('--login',default=os.environ.get('GITREX_LOGIN','narayanangourav'))
        p.add_argument('--token',default=None,help='Use GH_TOKEN environment variable instead where possible')
    collect_p.add_argument('--output',default='snapshot.json')
    render_p.add_argument('snapshot',help='Path to collected JSON snapshot')
    args=parser.parse_args(argv)
    try:
        if args.command=='demo':
            snap=json.loads((PACKAGE_ROOT/'assets'/'demo_snapshot.json').read_text(encoding='utf-8'))
        elif args.command in ('live','collect'):
            snap=collect(args.login,args.token)
            if args.command=='collect':
                _atomic_write(Path(args.output),snap)
                print(f'Collected {len(snap["daily"])} days -> {args.output}')
                return 0
        else:
            snap=json.loads(Path(args.snapshot).read_text(encoding='utf-8'))
        result=render(snap,Path(args.output_dir),args.width,args.frames,demo=(args.command=='demo'))
        if args.command=='live':
            # Publication requires a fully successful live render; no demo fallback.
            _atomic_write(Path(args.output_dir)/'snapshot.json',snap)
        print(f'GitRex: @{snap["login"]} | {result["state"]["stage"]} | '
              f'{result["state"]["contributions"]} contributions')
        print('GIF:',result['gif'],'(',round(result['size_bytes']/1024/1024,2),'MiB )')
        print('Preview:',result['preview'])
        return 0
    except (GithubError,ValueError,OSError,KeyError,json.JSONDecodeError) as e:
        print('GitRex error:',str(e),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
