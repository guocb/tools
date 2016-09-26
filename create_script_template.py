#!/usr/bin/env python
'''
Create template for new python/shell scripts to save some time.
'''
# pytlint: disable=missing-docstring
import argparse
import sys

from collections import namedtuple


class Argument(namedtuple('Argument', ['short', 'long', 'type', 'default'])):
    '''
    >>> a = Argument('j:job:int:4')
    >>> str(a)
    "    parser.add_argument(\\n\
        'j', 'job', type=int, default=4\\n\
    )"
    >>> a = Argument('j:job')
    >>> str(a)
    "    parser.add_argument(\\n        'j', 'job'\\n    )"
    '''
    def __new__(cls, string):
        arguments = string.split(':', 4)
        l = len(arguments)
        if l > 4:
            raise TypeError('Argument with more than 4 metas')
        arguments.extend([None] * (4 - l))
        return tuple.__new__(cls, arguments)

    def __repr__(self):
        tmpl = ['    parser.add_argument(']
        args = ["'%s'" % s for s in (self.short, self.long) if s]
        if self.type:
            args.append('type=%s' % self.type)
        if self.default:
            args.append('default=%s' % self.default)
        args = '        %s' % ', '.join(args)
        tmpl.extend([args, '    )'])
        return '\n'.join(tmpl)


def python_template(args):
    tmpl = [
        '#!/usr/bin/env python',
        "'''",
        "'''",
        '# pylint: disable=missing-docstring',
        'import argparse',
        'import sys',
        '', '',
        'def parse_args(argv):',
        '    parser = argparse.ArgumentParser(description=__doc__)',
    ]
    for a in args.args:
        tmpl.append(str(Argument(a)))
    tmpl.append('    return parser.parse_args(argv)')

    if not args.no_main:
        tmpl.extend([
            '', '',
            'def main(argv):',
            '    args = parse_args(argv)',
            '', '',
            "if __name__ == '__main__':",
            '    sys.exit(main(sys.argv[1:]))',
            ''
        ])

    with args.script_name as f:
        f.write('\n'.join(tmpl))


def add_python_options(subparser):
    parser = subparser.add_parser('python',
                                  help='Create template for a python script.')
    parser.add_argument(
        '--no-main', action='store_true',
        help="Doesn't create main function."
    )
    parser.add_argument(
        '--no-test', action='store_true',
        help="Doesn't create test script."
    )
    parser.add_argument(
        '-a', '--arg', dest='args', action='append',
        metavar='SHORT:LONG:TYPE:DEFAULT',
        help='arguments for the new script'
    )
    parser.add_argument(
        'script_name', metavar='SCRIPT_NAME', type=argparse.FileType('w'),
        help='script name (w/o ext name)'
    )
    parser.set_defaults(func=python_template)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    subparser = parser.add_subparsers()
    add_python_options(subparser)
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
