"""
This was copied from: https://github.com/pygments/pygments/blob/ce53c4e4b7548fb97d8c532bec82f8d275d9a7f1/pygments/lexers/configs.py#L694

The Authors are: https://github.com/pygments/pygments/blob/ce53c4e4b7548fb97d8c532bec82f8d275d9a7f1/AUTHORS

The following license applies to this file:

Copyright (c) 2006-2022 by the respective authors (see AUTHORS file).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


from pygments.lexer import ExtendedRegexLexer, bygroups, include, words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number, Punctuation, Whitespace, Error, Literal


class CustomLexer(ExtendedRegexLexer):
    """
    Lexer for terraformi ``.tf`` files.
    """

    name = 'Docker-Bake'
    url = 'https://www.terraform.io/'
    aliases = ['bake']
    filenames = ['*.hcl']
    mimetypes = ['application/x-docker-bake']
    version_added = '2.1'

    classes = ('variable', 'group', 'target')
    classes_re = "({})".format(('|').join(classes))

    types = ('string', 'number', 'bool', 'list', 'tuple', 'map', 'set', 'object', 'null')

    numeric_functions = ('abs', 'ceil', 'floor', 'log', 'max',
                         'mix', 'parseint', 'pow', 'signum')

    string_functions = ('chomp', 'format', 'formatlist', 'indent',
                        'join', 'lower', 'regex', 'regexall', 'replace',
                        'split', 'strrev', 'substr', 'title', 'trim',
                        'trimprefix', 'trimsuffix', 'trimspace', 'upper'
                        )

    collection_functions = ('alltrue', 'anytrue', 'chunklist', 'coalesce',
                            'coalescelist', 'compact', 'concat', 'contains',
                            'distinct', 'element', 'flatten', 'index', 'keys',
                            'length', 'list', 'lookup', 'map', 'matchkeys',
                            'merge', 'range', 'reverse', 'setintersection',
                            'setproduct', 'setsubtract', 'setunion', 'slice',
                            'sort', 'sum', 'transpose', 'values', 'zipmap'
                            )

    encoding_functions = ('base64decode', 'base64encode', 'base64gzip',
                          'csvdecode', 'jsondecode', 'jsonencode', 'textdecodebase64',
                          'textencodebase64', 'urlencode', 'yamldecode', 'yamlencode')

    filesystem_functions = ('abspath', 'dirname', 'pathexpand', 'basename',
                            'file', 'fileexists', 'fileset', 'filebase64', 'templatefile')

    date_time_functions = ('formatdate', 'timeadd', 'timestamp')

    hash_crypto_functions = ('base64sha256', 'base64sha512', 'bcrypt', 'filebase64sha256',
                             'filebase64sha512', 'filemd5', 'filesha1', 'filesha256', 'filesha512',
                             'md5', 'rsadecrypt', 'sha1', 'sha256', 'sha512', 'uuid', 'uuidv5')

    ip_network_functions = ('cidrhost', 'cidrnetmask', 'cidrsubnet', 'cidrsubnets')

    type_conversion_functions = ('can', 'defaults', 'tobool', 'tolist', 'tomap',
                                 'tonumber', 'toset', 'tostring', 'try')

    builtins = numeric_functions + string_functions + collection_functions + encoding_functions +\
        filesystem_functions + date_time_functions + hash_crypto_functions + ip_network_functions +\
        type_conversion_functions
    builtins_re = "({})".format(('|').join(builtins))

    def heredoc_callback(self, match, ctx):
        # Parse a terraform heredoc
        # match: 1 = <<[-]?, 2 = name 3 = rest of line

        start = match.start(1)
        yield start, Operator, match.group(1)        # <<[-]?
        yield match.start(2), String.Delimiter, match.group(2)  # heredoc name

        ctx.pos = match.start(3)
        ctx.end = match.end(3)
        yield ctx.pos, String.Heredoc, match.group(3)
        ctx.pos = match.end()

        hdname = match.group(2)
        tolerant = True  # leading whitespace is always accepted

        lines = []

        for match in line_re.finditer(ctx.text, ctx.pos):
            if tolerant:
                check = match.group().strip()
            else:
                check = match.group().rstrip()
            if check == hdname:
                for amatch in lines:
                    yield amatch.start(), String.Heredoc, amatch.group()
                yield match.start(), String.Delimiter, match.group()
                ctx.pos = match.end()
                break
            else:
                lines.append(match)
        else:
            # end of heredoc not found -- error!
            for amatch in lines:
                yield amatch.start(), Error, amatch.group()
        ctx.end = len(ctx.text)

    tokens = {
        'root': [
            include('basic'),
            include('whitespace'),

            # Strings
            (r'(".*")', bygroups(String.Double)),

            # Constants
            (words(('true', 'false'), prefix=r'\b', suffix=r'\b'), Name.Constant),

            # Types
            (words(types, prefix=r'\b', suffix=r'\b'), Keyword.Type),

            include('identifier'),
            include('punctuation'),
            (r'[0-9]+', Number),
        ],
        'basic': [
            (r'\s*/\*', Comment.Multiline, 'comment'),
            (r'\s*(#|//).*\n', Comment.Single),
            include('whitespace'),

            # e.g. terraform {
            # e.g. egress {
            (r'(\s*)([0-9a-zA-Z-_]+)(\s*)(=?)(\s*)(\{)',
             bygroups(Whitespace, Name.Builtin, Whitespace, Operator, Whitespace, Punctuation)),

            # Assignment with attributes, e.g. something = ...
            (r'(\s*)([0-9a-zA-Z-_]+)(\s*)(=)(\s*)',
             bygroups(Whitespace, Name.Attribute, Whitespace, Operator, Whitespace)),

            # Assignment with environment variables and similar, e.g. "something" = ...
            # or key value assignment, e.g. "SlotName" : ...
            (r'(\s*)("\S+")(\s*)([=:])(\s*)',
             bygroups(Whitespace, Literal.String.Double, Whitespace, Operator, Whitespace)),

            # Functions, e.g. jsonencode(element("value"))
            (builtins_re + r'(\()', bygroups(Name.Function, Punctuation)),

            # List of attributes, e.g. ignore_changes = [last_modified, filename]
            (r'(\[)([a-z_,\s]+)(\])', bygroups(Punctuation, Name.Builtin, Punctuation)),

            # e.g. resource "aws_security_group" "allow_tls" {
            # e.g. backend "consul" {
            (classes_re + r'(\s+)("[0-9a-zA-Z-_]+")?(\s*)("[0-9a-zA-Z-_]+")(\s+)(\{)',
             bygroups(Keyword.Reserved, Whitespace, Name.Class, Whitespace, Name.Variable, Whitespace, Punctuation)),

            # here-doc style delimited strings
            (r'(<<-?)\s*([a-zA-Z_]\w*)(.*?\n)', heredoc_callback),
        ],
        'identifier': [
            (r'\b(var\.[0-9a-zA-Z-_\.\[\]]+)\b', bygroups(Name.Variable)),
            (r'\b([0-9a-zA-Z-_\[\]]+\.[0-9a-zA-Z-_\.\[\]]+)\b',
             bygroups(Name.Variable)),
        ],
        'punctuation': [
            (r'[\[\]()\{\},.?:!=]', Punctuation),
        ],
        'comment': [
            (r'[^*/]', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline)
        ],
        'whitespace': [
            (r'\n', Whitespace),
            (r'\s+', Whitespace),
            (r'(\\)(\n)', bygroups(Text, Whitespace)),
        ],
    }