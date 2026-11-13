"""Optional, source-reviewed argument annotations for usage signatures."""
from html import escape
import json
import re

INTENTS = {'in', 'out', 'inout', 'conditional'}


def signature_code(signature):
    """Mask inline comments without changing offsets in the displayed text."""
    result=[];quote=None;comment=False;i=0
    while i<len(signature):
        char=signature[i]
        if char=='\n':comment=False
        if comment:result.append(' ' if char!='\n' else char)
        elif quote:
            result.append(char)
            if char==quote:
                if i+1<len(signature) and signature[i+1]==quote:
                    result.append(signature[i+1]);i+=1
                else:quote=None
        elif char in "'\"":quote=char;result.append(char)
        elif char=='!':comment=True;result.append(' ')
        else:result.append(char)
        i+=1
    return ''.join(result)


def signature_calls(signature):
    """Locate outer calls without treating nested actual expressions as calls."""
    signature=signature_code(signature)
    calls = []
    position = 0
    while position < len(signature):
        match = re.search(r'([A-Za-z][A-Za-z0-9_]*(?:%[A-Za-z][A-Za-z0-9_]*)*)\s*\(', signature[position:])
        if not match:
            break
        start = position+match.end()-1
        depth, quote, i = 1, None, start+1
        while i < len(signature) and depth:
            char = signature[i]
            if quote:
                if char == quote:
                    if i+1 < len(signature) and signature[i+1] == quote:
                        i += 2
                        continue
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            i += 1
        if depth:
            break
        calls.append({'name':match[1], 'start':start+1, 'end':i-1})
        position = i
    return calls


def argument_tokens(signature):
    """Tokenize only the call's argument region, excluding quoted literals."""
    tokens = []
    pattern = r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|(?<![.\w])[A-Za-z][A-Za-z0-9_]*(?![.\w])"
    for call in signature_calls(signature):
        for match in re.finditer(pattern, signature[call['start']:call['end']]):
            if match.group()[0] not in "'\"":
                tokens.append((call['start']+match.start(), call['start']+match.end(), match.group()))
    return tokens


def usage_tokens(procedure):
    signature = procedure['signature']
    procedure_name = procedure.get('procedure', '').lower()
    if procedure_name.startswith(('operator(', 'assignment(')) and not signature_calls(signature):
        first = 0 if procedure_name.startswith('assignment(') else signature.find('=')+1
        return [(0, first+m.start(), first+m.end(), m[0])
                for m in re.finditer(r'(?<![.\w])[A-Za-z][A-Za-z0-9_]*(?![.\w])',signature_code(signature)[first:])]
    return [(index, start, end, name) for index,call in enumerate(signature_calls(signature))
            for start,end,name in argument_tokens(signature)
            if call['start'] <= start < end <= call['end']]


def validate_arguments(procedure, evidence_paths):
    review=procedure.get('argument_intent_review')
    if review is not None:
        if (not isinstance(review,dict) or review.get('status') not in {'checked','partial','not-applicable'} or
                not re.fullmatch(r'\d{4}-\d{2}-\d{2}',review.get('reviewed_on','')) or
                not isinstance(review.get('issues'),list) or not isinstance(review.get('sources'),list)):
            raise ValueError('Invalid argument-intent review record.')
        if ((review['status']=='checked' and (review['issues'] or not review['sources'])) or
                (review['status']=='partial' and not review['issues']) or
                (review['status']=='not-applicable' and not review.get('notes'))):
            raise ValueError('Argument-intent review status needs matching scope notes.')
        for source in review['sources']:
            if (source.get('path') not in evidence_paths or type(source.get('line_start')) is not int or
                    type(source.get('line_end')) is not int or not 1<=source['line_start']<=source['line_end']):
                raise ValueError('Argument-intent review needs pinned source ranges.')
    details=procedure.get('argument_details',[])
    known={(index,name.casefold()) for index,_,_,name in usage_tokens(procedure)} if procedure.get('signature') else set()
    seen_details=set()
    for detail in details:
        key=(detail.get('call_index',0),detail.get('name','').casefold())
        if key not in known or key in seen_details or not detail.get('declarations'):
            raise ValueError('Argument details need distinct displayed arguments and declarations.')
        seen_details.add(key)
        for item in detail['declarations']:
            for source in [item,*item.get('comments',[])]:
                if (source.get('path') not in evidence_paths or not isinstance(source.get('text'),str) or not source['text'].strip()
                        or type(source.get('line_start')) is not int or type(source.get('line_end')) is not int
                        or not 1<=source['line_start']<=source['line_end']):
                    raise ValueError('Argument declarations/comments need text and pinned source ranges.')
    arguments = procedure.get('arguments')
    if arguments is None:
        return
    if (not isinstance(arguments, list) or not arguments or
            procedure.get('role') not in {'public-entry-point', 'public-adapter', 'implementation-helper'} or
            not procedure.get('signature')):
        raise ValueError('Argument intents need a callable usage signature.')
    names = {(index, name.casefold()) for index, _, _, name in usage_tokens(procedure)}
    seen = set()
    for arg in arguments:
        if not isinstance(arg, dict):
            raise ValueError('Argument annotations must be objects.')
        name = arg.get('name', '')
        index = arg.get('call_index', 0)
        if (not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name) or
                type(index) is not int or (index, name.casefold()) in seen or
                (index, name.casefold()) not in names or arg.get('intent') not in INTENTS):
            raise ValueError('Invalid, duplicate or absent argument intent annotation.')
        seen.add((index, name.casefold()))
        if 'dummy' in arg and (not isinstance(arg['dummy'], str) or
                              not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', arg['dummy'])):
            raise ValueError('Invalid source dummy-argument name.')
        if arg['intent']=='conditional':
            variants=arg.get('variants')
            if not isinstance(variants,list) or len(variants)<2:
                raise ValueError('Conditional intent needs source-linked alternatives.')
            for variant in variants:
                if not isinstance(variant,dict) or variant.get('intent') not in {'in','out','inout'} or not variant.get('condition'):
                    raise ValueError('Conditional intent needs explicit conditions.')
                validate_arguments({**procedure,'arguments':[{'name':name,**{k:v for k,v in variant.items() if k!='condition'},
                                                            'call_index':index}]},evidence_paths)
        start, end = arg.get('line_start'), arg.get('line_end')
        if (arg.get('path') not in evidence_paths or type(start) is not int or type(end) is not int or
                start < 1 or end < start or not any(
                    d['path'] == arg['path'] and d['line_start'] <= start <= end <= d['line_end']
                    for d in procedure.get('declarations', []))):
            raise ValueError('Argument intents must link to recorded argument declarations.')


def individual_declaration(text, name):
    """Select one entity without splitting dimensions, selectors or literals.

    Return None for unfamiliar syntax; the unchanged source stays in details.
    This is a display projection, never a rewritten source/evidence record.
    """
    depth=0;quote=None;separator=None;i=0
    while i<len(text):
        char=text[i]
        if quote:
            if char==quote:
                if i+1<len(text) and text[i+1]==quote:i+=2;continue
                quote=None
        elif char in "'\"":quote=char
        elif char in '([':depth+=1
        elif char in ')]':depth-=1
        elif depth==0 and text[i:i+2]=='::':separator=i;break
        i+=1
    if separator is not None:
        prefix=text[:separator+2].rstrip()+' '
        entities=text[separator+2:]
    else:
        head=re.match(r'\s*(?:double\s*precision|double\s*complex|integer|real|complex|logical|character|type|class|procedure|external|dimension|allocatable|pointer|optional|target|value|contiguous|intent)\b',text,re.I)
        if not head:return None
        i=head.end()
        while i<len(text) and text[i].isspace():i+=1
        if i<len(text) and text[i]=='*':
            i+=1
            while i<len(text) and text[i].isspace():i+=1
            if i<len(text) and text[i]!='(':
                selector=re.match(r'(?:[0-9]+|[a-z][a-z0-9_]*)',text[i:],re.I)
                if not selector:return None
                i+=selector.end()
                while i<len(text) and text[i].isspace():i+=1
        if i<len(text) and text[i]=='(':
            depth=1;i+=1
            while i<len(text) and depth:
                if text[i]=='(':depth+=1
                elif text[i]==')':depth-=1
                i+=1
            if depth:return None
        prefix=text[:i].rstrip()+' '
        entities=text[i:]
    parts=[];start=0;depth=0;quote=None;i=0
    while i<len(entities):
        char=entities[i]
        if quote:
            if char==quote:
                if i+1<len(entities) and entities[i+1]==quote:i+=2;continue
                quote=None
        elif char in "'\"":quote=char
        elif char in '([':depth+=1
        elif char in ')]':depth-=1
        elif char==',' and depth==0:
            parts.append(entities[start:i].strip());start=i+1
        i+=1
    if depth or quote:return None
    parts.append(entities[start:].strip())
    matches=[entity for entity in parts if (m:=re.match(r'([a-z][a-z0-9_]*)\b',entity,re.I)) and m[1].casefold()==name.casefold()]
    return prefix+matches[0] if len(matches)==1 else None


def top_level_items(text):
    """Offsets for comma-separated items; strings, shapes and arrays stay intact."""
    start=0;depth=0;quote=None;i=0
    while i<len(text):
        char=text[i]
        if quote:
            if char==quote:
                if i+1<len(text) and text[i+1]==quote:i+=2;continue
                quote=None
        elif char in "'\"":quote=char
        elif char in '([':depth+=1
        elif char in ')]':depth-=1
        elif char==',' and depth==0:
            yield start,i;start=i+1
        i+=1
    yield start,len(text)


def declared_optional(detail):
    """Only explicit OPTIONAL in declaration attributes, never prose or names."""
    typed=[]
    for declaration in detail.get('declarations',[]):
        code=re.sub(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", '', signature_code(declaration['text']))
        if re.match(r'^\s*optional\b',code,re.I):return True
        if '::' not in code:continue
        prefix=code.split('::',1)[0]
        attributes=[prefix[a:b].strip().lower() for a,b in top_level_items(prefix)]
        optional='optional' in attributes
        if optional or re.match(r'^\s*(?:real|integer|complex|logical|character|double\s*precision|double\s*complex|type|class|procedure)\b',prefix,re.I):
            typed.append(optional)
    # Conflicting typed declarations may be preprocessing alternatives; do not
    # turn an OPTIONAL in just one alternative into an unconditional promise.
    return bool(typed) and all(typed)


def optional_argument_ranges(procedure):
    signature=procedure['signature'];code=signature_code(signature)
    optional={(d.get('call_index',0),d['name'].casefold()) for d in procedure.get('argument_details',[]) if declared_optional(d)}
    keywords={(d.get('call_index',0),d.get('dummy',d['name']).casefold()) for d in procedure.get('argument_details',[]) if declared_optional(d)}
    result=[]
    for index,call in enumerate(signature_calls(signature)):
        for first,last in top_level_items(code[call['start']:call['end']]):
            first+=call['start'];last+=call['start']
            while first<last and code[first] in ' \t\r\n&':first+=1
            while last>first and code[last-1] in ' \t\r\n&':last-=1
            item=code[first:last]
            keyword=re.match(r'^([a-z][a-z0-9_]*)\s*=(?!=|>)',item,re.I)
            # Preserve existing documentation groups; keyword values may still
            # contain an ordinary Fortran array constructor.
            if item.startswith('[') or (not keyword and ('[' in item or ']' in item)):continue
            plain=re.fullmatch(r'[a-z][a-z0-9_]*',item,re.I)
            name=keyword[1] if keyword else plain[0] if plain else None
            if name and (index,name.casefold()) in (keywords | optional if keyword else optional):result.append((first,last))
    return result


def optional_notation_markup(procedure):
    if optional_argument_ranges(procedure):
        return '<p class="optional-notation">Brackets added around optional arguments are documentation notation, not literal Fortran syntax.</p>'
    return ''


def signature_markup(procedure):
    """Escape usage text and mark source-declared optional arguments for display."""
    signature = procedure['signature']
    markers={}
    for first,last in optional_argument_ranges(procedure):
        markers[first]='[';markers[last]=']'
    def fragment(first,last):
        result=[];previous=first
        for position in sorted(p for p in markers if first<=p<last):
            result.extend([escape(signature[previous:position]),markers[position]]);previous=position
        result.append(escape(signature[previous:last]))
        return ''.join(result)
    intents = {(arg.get('call_index', 0), arg['name'].casefold()): arg
               for arg in procedure.get('arguments', [])}
    details = {(a.get('call_index',0),a['name'].casefold()):a for a in procedure.get('argument_details',[])}
    parts, previous = [], 0
    for index, start, end, name in usage_tokens(procedure):
        argument = intents.get((index, name.casefold()))
        intent = argument['intent'] if argument else None
        detail=details.get((index,name.casefold()))
        if intent not in INTENTS and not detail:
            continue
        parts.append(fragment(previous,start))
        description=('; '.join('intent('+v['intent']+') when '+v['condition'] for v in argument['variants'])
                     if intent=='conditional' else 'intent('+intent+')' if intent else 'Declaration unavailable.')
        code_ranges=[]
        if detail:
            blocks=[]
            declaration_blocks=[]
            displayed_intents=set()
            if detail.get('implementation'):blocks.append('Specific procedure: '+detail['implementation'])
            for d in detail['declarations']:
                block=(individual_declaration(d['text'],detail.get('dummy',detail['name']))
                       if d.get('shared') else d['text'])
                if block:declaration_blocks.append((len(blocks),len(block)))
                block=block or 'Declaration available in source details.'
                # Read only declaration code, not comments or quoted examples.
                code=re.sub(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", '', signature_code(block))
                displayed_intents.update(re.sub(r'\s+', '', value).lower() for value in
                    re.findall(r'\bintent\s*\(\s*(in\s*out|out|in)\s*\)',code,re.I))
                if d.get('comments'):
                    block+='\n'+('Shared comment: ' if d.get('shared') else '')+'\n'.join(c['text'] for c in d['comments'])
                blocks.append(block)
            if detail.get('dummy'):
                blocks.insert(0,'Source dummy: '+detail['dummy'])
                declaration_blocks=[(index+1,length) for index,length in declaration_blocks]
            for index,length in declaration_blocks:
                first=sum(len(block)+2 for block in blocks[:index])
                code_ranges.append([first,first+length])
            represented=(intent in {'in','out','inout'} and displayed_intents=={intent}) or (intent is None)
            description='\n\n'.join(blocks)+('' if represented else '\n\n'+description)
        label = escape(name+': '+description, quote=True)
        parts.append(f'<span class="argument-intent" data-argument-intent="{intent or "unspecified"}" '
                     f'data-intent-description="{escape(description,quote=True)}" '
                     f'data-code-ranges="{escape(json.dumps(code_ranges),quote=True)}" data-argument-label="{escape(name,quote=True)}" '
                     f'tabindex="0" role="note" title="{label}" aria-label="{label}">{fragment(start,end)}</span>')
        previous = end
    parts.append(fragment(previous,len(signature)))
    return ''.join(parts)


def argument_details_markup(procedure, source_url):
    details=procedure.get('argument_details',[])
    if not details:return ''
    result='<details class="argument-details"><summary><span class="show-declarations">Show declarations</span><span class="hide-declarations">Hide declarations</span></summary><dl>'
    order={(index,name.casefold()):position for position,(index,_,_,name) in enumerate(usage_tokens(procedure))}
    for argument in sorted(details,key=lambda a:order.get((a.get('call_index',0),a['name'].casefold()),len(order))):
        name=argument['name']
        if argument.get('implementation'):name+='; specific procedure '+argument['implementation']
        if argument.get('dummy'):name+=' (source dummy: '+argument['dummy']+')'
        if 'call_index' in argument:name+='; call '+str(argument['call_index']+1)
        result+='<dt><code class="declaration-code">'+escape(name)+'</code></dt><dd>'
        for declaration in argument['declarations']:
            projected=individual_declaration(declaration['text'],argument.get('dummy',argument['name']))
            normalized=' data-normalized-code="'+escape(projected,quote=True)+'"' if projected else ''
            result+='<pre><code class="declaration-code"'+normalized+'>'+escape(declaration['text'])+'</code></pre>'
            if declaration.get('shared'):result+='<p>Shared declaration; associated comments may describe several arguments.</p>'
            for comment in declaration.get('comments',[]):
                result+='<p class="argument-comment">'+escape(comment['text'])+' '+source_link(comment,source_url)+'</p>'
            result+=source_link(declaration,source_url)
        result+='</dd>'
    return result+'</dl></details>'


def source_link(record, source_url):
    from urllib.parse import quote
    url=source_url+quote(record['path'],safe='/')+'#L'+str(record['line_start'])+'-L'+str(record['line_end'])
    return '<a href="'+escape(url,quote=True)+'">'+escape(record['path']+':'+str(record['line_start']))+'</a>'
