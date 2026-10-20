#!/usr/bin/env python3
"""Read-only, offline lookup of Restream streaming routes (destinations, methods, protocols, chat)."""
import argparse
import json
import re
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / 'references' / 'streaming-catalog.json'

NOTICE = ('Documentation snapshot; no live account or stream tested. '
          'Null means unknown. Select the actual route if multiple records match.')

def normalized(value):
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', help='Destination, method, protocol, encoder, or "chat"')
    parser.add_argument('--list', action='store_true', help='List names and route categories')
    args = parser.parse_args()
    data = json.loads(CATALOG.read_text(encoding='utf-8'))
    groups = ['platforms', 'methods', 'custom_protocols', 'delivery_and_operations', 'encoder_adapters']
    entries = [(group, item) for group in groups for item in data[group]]
    if args.list:
        result = {'audit_date':data['audit_date'], 'coverage':data['coverage'],
                  'entries':[{'category':g,'name':v['name'],'id':v.get('id')} for g,v in entries]}
    else:
        if not args.query or not normalized(args.query): parser.error('Supply a query or --list.')
        q = normalized(args.query)
        # Directional terms deliberately return all relevant named routes.
        broad = {'srt':['srt-input','custom-srt'], 'whip':['whip-input','custom-whip'],
                 'zoom':['zoom','zoom-input'], 'rtmp':['rtmp-input','custom-rtmp','rtmp-source','rtmp-pull'],
                 'hls':['custom-hls'], 'chat':[]}
        matches = []
        for group,item in entries:
            names = [item['name'],item.get('id','')] + item.get('aliases',[])
            names += [v['name'] for v in item.get('variants',[])]
            names += [v['id'] for v in item.get('variants',[])]
            terms = [normalized(n) for n in names if n]
            if q in terms or (q in broad and item.get('id') in broad[q]):
                matches.append({'category':group,**item})
        if not matches and q not in broad:
            matches = [{'category':g,**v} for g,v in entries
                       if q in normalized(v['name']+' '+v.get('id',''))]
        conflicts = data['documentation_conflicts'] if q in ('conflicts','research') else []
        source_ids = set()
        def collect(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k=='sources' and isinstance(v,list): source_ids.update(v)
                    else: collect(v)
            elif isinstance(value,list):
                for v in value: collect(v)
        collect(matches)
        # Include explicit conflicts intersecting the selected records' sources.
        if matches:
            conflicts = [c for c in data['documentation_conflicts'] if source_ids.intersection(c['sources'])]
        collect(conflicts)
        chat = data['chat_matrix'] if q=='chat' else []
        collect(chat)
        result = {'audit_date':data['audit_date'],
                  'notice':NOTICE,
                  'query':args.query,'matches':matches,'conflicts':conflicts,'chat':chat,
                  'sources':{s:data['sources'][s] for s in sorted(source_ids)}}
        if not matches and not conflicts and not chat:
            result['message']='No documented match. Use --list or verify current provider documentation; do not invent settings.'
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
