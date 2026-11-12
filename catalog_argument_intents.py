"""Optional, source-reviewed argument annotations for usage signatures."""
from html import escape
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


def signature_markup(procedure):
    """Preserve literal signature text and escape every fragment independently."""
    signature = procedure['signature']
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
        parts.append(escape(signature[previous:start]))
        description=('; '.join('intent('+v['intent']+') when '+v['condition'] for v in argument['variants'])
                     if intent=='conditional' else 'intent('+intent+')' if intent else 'No explicit INTENT recorded')
        if detail:
            blocks=[]
            if detail.get('implementation'):blocks.append('Specific procedure: '+detail['implementation'])
            for d in detail['declarations']:
                block=d['text']
                if d.get('shared'):block+='\n(Shared declaration; comments may describe several arguments.)'
                block+=''.join('\n'+c['text'] for c in d.get('comments',[]))
                blocks.append(block)
            if detail.get('dummy'):blocks.insert(0,'Source dummy: '+detail['dummy'])
            description='\n\n'.join(blocks)+'\n\n'+description
        label = escape(name+': '+description, quote=True)
        parts.append(f'<span class="argument-intent" data-argument-intent="{intent or "unspecified"}" '
                     f'data-intent-description="{escape(description,quote=True)}" '
                     f'tabindex="0" role="note" title="{label}" aria-label="{label}">{escape(name)}</span>')
        previous = end
    parts.append(escape(signature[previous:]))
    return ''.join(parts)


def argument_details_markup(procedure, source_url):
    details=procedure.get('argument_details',[])
    if not details:return ''
    result='<details class="argument-details"><summary>Argument declarations and source comments</summary><dl>'
    for argument in details:
        name=argument['name']
        if argument.get('implementation'):name+='; specific procedure '+argument['implementation']
        if argument.get('dummy'):name+=' (source dummy: '+argument['dummy']+')'
        if 'call_index' in argument:name+='; call '+str(argument['call_index']+1)
        result+='<dt><code>'+escape(name)+'</code></dt><dd>'
        for declaration in argument['declarations']:
            result+='<pre><code>'+escape(declaration['text'])+'</code></pre>'
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
