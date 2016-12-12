from pathlib import Path
from pyparsing import *
from pprint import pprint
from collections import OrderedDict


# filePath = Path(r'e:/dishonored_reverse/out/game2.resources/generated/decls/animtree/animtree/animtree_paused_leaf.animtree.decl')
# filePath = Path(r'e:/dishonored_reverse/out/game2.resources/generated/decls/arktree/components/characters/bt/ambush_waylayer_psychic.arktree.decl')


inputData = '''
{
    edit = {
        root = {
            m_settings = {
                m_class = "arkTreeNodeSettings_Activator_AttributeModifier";
                m_object = {
                    m_stimSettings = {
                        m_handled = "";
                        m_consumed = "";
                    }
                    m_comment = "";
                    m_modifiers = {
                        num = 1;
                        item[0] = {
                            m_attribute = "ARK_ATTRIBUTE_AMBUSH_RALLY_PSYCHIC";
                            m_increase = 1;
                            m_percentage = 0;
                            m_duration = 0;
                        }
                    }
                }
            }
            m_children = {
                num = 1;
                item[0] = {
                    m_settings = {
                        m_class = "arkTreeNodeSettings_TreeReference";
                        m_object = {
                            m_stimSettings = {
                                m_handled = "";
                                m_consumed = "";
                            }
                            m_comment = "";
                            m_subTree = "components/characters/bt/ambush_waylayer.arktree";
                        }
                    }
                    m_children = {
                        num = 0;
                    }
                }
            }
        }
    }
}
'''



# print(inputData)
def make_keyword(kwd_str, kwd_value):
    return Keyword(kwd_str).setParseAction(replaceWith(kwd_value))
TRUE  = make_keyword("true", True)
FALSE = make_keyword("false", False)
NULL  = make_keyword("null", None)

LBRACK, RBRACK, LBRACE, RBRACE, COLON, ASSIGN, SEMICOLON = map(Suppress, "[]{}:=;")

declString = dblQuotedString().setParseAction(removeQuotes)
declKey = Word(alphanums + '_[]')
# declNumber = Word(nums)

declNumber = Regex(r"\d+(\.\d*)?").setParseAction(lambda t: float(t[0]))

declObject = Forward()
declValue = Forward()
declElements = Dict( declValue )
declArray = Group(LBRACK + Optional(declElements, []) + RBRACK)
# declValue << (declString | declNumber | declObject  | declArray | TRUE | FALSE | NULL)
declValue << (declString | declNumber | declObject| TRUE | FALSE)
memberDef = Group(declKey + Optional(ASSIGN) + declValue + Optional(SEMICOLON))
declMembers = ZeroOrMore(memberDef)
declObject << Dict(LBRACE + Optional(declMembers) + RBRACE)

declComment = cppStyleComment 
declObject.ignore(declComment)
# declObject.setDebug(True)



def ParseDeclToDict(inputData):
    def convertArray(d):
        if 'num' in d:
            # print('---------convertArray', d)
            num = int(d['num'])
            # print('d[num] = ', num, (len(d) - 1), num == (len(d) - 1))
            # print(type(num))
            if num == (len(d) - 1):
                arr = [None] * num
                # print(arr)

                for k,v in d.items():
                    if k == 'num': continue
                    # print(k, v)
                    spl = k[:-1].split('[')
                    assert(spl[0] == 'item')
                    idx = int(spl[1])
                    
                    arr[idx] = v
                return arr

        if all(k.startswith('enumItem') for k in d.keys()):
            e = {}
            for k,v in d.items():
                spl = k[:-1].split('[')
                e[spl[1]] = v
            return e
        return d

    def resAsDict(res):
        # return res.asDict()
        # print(res.asList)
        # print(res.__tokdict)
        # res.__tokdict = OrderedDict
        # print(res.__tokdict)
        # return dict(res.items())
        # print([k for k in res.iterkeys()])

        return res.asDict()
        # return OrderedDict(res.items())

    def convertResult(res):
        # print('convertResult', res)
        # d = OrderedDict()
        d= {}
        for k,v in res.items():
            # print(k, type(v))
            if type(v) is ParseResults:
                d[k] = convertResult(resAsDict(v))
            else:
                d[k] = v

        d = convertArray(d)
        return d


    results = declObject.parseString(inputData)
    # pprint(results.dump())
    # print(results.dump())
    # pprint(results.asDict(), width=1)

    # return convertResult(resAsDict(results))

    return results



filePath = Path(r'e:/dishonored_reverse/out/game2.resources/generated/decls/arktree/components/characters/bt/ambush_waylayer_psychic.arktree.decl')
# filePath = Path(r'e:\dishonored_reverse\out\game2.resources\generated\decls\arktree\components\characters\bt\ambush_waylayer_deaf.arktree.decl')
with filePath.open('r') as f:
    inputData = f.read()


# inputData = '''
# {
#     root = {
#         m_settings = {
#             m_class = "arkTreeNodeSettings_Activator_AttributeModifier";
#         }
#         z = {
#             num = 2
#             item[1] = "i1"
#             item[0] = "i0"
#         }
#                                         m_relationship = {
#                                                                                 enumItem[ALLY] = true;
#                                                                                 enumItem[NEUTRAL] = true;
#                                                                                 enumItem[ENEMY] = false;
#                                                                                 enumItem[UNDEFINED] = true;
#                                                                             }
#     }
# }
# '''

inputData = '''
{
    a = 1
    b = { x = 2 }
    c = 3
}
'''

res = ParseDeclToDict(inputData)

# pprint([x for x in res.asList()])


def convertResult(res):
    # print('convertResult', res)
    # d = OrderedDict()
    d = OrderedDict()
    for v in res:
        if type(v) is ParseResults:
            d[k] = convertResult(v)
        else:
            d[k] = v

    # d = convertArray(d)
    return d
convertResult(res)


# import itertools
# def grouper(iterable, n, fillvalue=None):
#     "Collect data into fixed-length chunks or blocks"
#     # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
#     args = [iter(iterable)] * n
#     return itertools.zip_longest(*args, fillvalue=fillvalue)

# def recurse(res, level=''):
#     d = dict()
#     prev = None
#     for v in res:
#         print(level, type(v), v, prev)
#         if type(v) is ParseResults:
#             x = recurse(v, level+' ')
#             if prev:
#                 d[prev] = x
#                 prev = None
#             else:
#                 d.update(x)
#             print(level, x)
#         elif prev:
#             d[prev] = v
#             prev = None
#             pass
#         else:
#             prev = v
#     print(level, d)
#     return d


# d = recurse(res)
# pprint(d)




# for 




# inputData = '''
# {
# x = asdf
# y = 123
# }
# '''

# LBRACE = '{'
# RBRACE = '}'
# ASSIGN = '='

# tokens = inputData.split()
# print(tokens)


# class Context:
#     def __init__(self):
#         self.result = None
#         self.stack = []
#         self.keysStack = ['root']


# def PushObj(ctx):
#     print('PushObj')
#     ctx.stack.append({})

# def PopObj(ctx):
#     print('PopObj')
#     obj = ctx.stack[-1]
#     del ctx.stack[-1]
#     if len(ctx.stack) == 0:
#         ctx.result = obj
#     else:
#         ctx.stack[-1][ctx.keysStack[-1]] = obj
#         del keysStack[-1]

# def PushValue(ctx, token):
#     print('PushValue')
#     if len(ctx.stack) == len(ctx.keysStack):
#         ctx.keysStack.append(token)
#     else:
#         ctx.stack[-1][ctx.keysStack[-1]] = token
#         del ctx.keysStack[-1]


# ctx = Context()
# for token in tokens:
#     if token == LBRACE:
#         PushObj(ctx)
#     elif token == RBRACE:
#         PopObj(ctx)
#     elif token == ASSIGN:
#         pass
#     else:
#         PushValue(ctx, token)


# print('-------------- result')
# print(ctx.result)


