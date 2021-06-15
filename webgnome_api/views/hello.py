"""
    The base URI for our server.
"""
from email import message_from_string
from pkg_resources import get_distribution

from pyramid.response import Response
from cornice import Service

hello = Service(name='hello', path='/', description="Introduction")


@hello.get()
def get_package_info_response(request):
    """Returns Package Version Information in html."""

    body = ('<html>'
            '    <body>'
            '        <h1>WebGnome API Server Package Versions</h1>'
            '        <p>{}</p>'
            '        <p>{}</p>'
            '    </body>'
            '</html>'
            .format(get_pkg_info_table('webgnome_api'),
                    get_pkg_info_table('pygnome'),
                    )
            )

    response = Response(content_type='text/html', body=body)

    return response


def get_pkg_info_table(package):
    pkg_info = get_distribution(package).get_metadata('PKG-INFO')
    msg_dict = dict(message_from_string(pkg_info))

    header_fields = [package]
    rows = []
    for k in ('Name', 'Version', 'Branch', 'LastUpdate', 'Author'):
        if k in msg_dict:
            rows.append([k + ':', msg_dict[k]])

    return to_table(header_fields, rows)


def to_table(header_items, row_items):
    header = to_table_row(header_items, header=True)
    rows = ''.join([to_table_row(r) for r in row_items])

    return '<table>{}{}</table>'.format(header, rows)


def to_table_row(items, header=False):
    if header is True:
        return '<tr>{}</tr>'.format(''.join([to_table_header(i) for i in items]))
    else:
        return '<tr>{}</tr>'.format(''.join([to_table_data(i) for i in items]))


def to_table_header(item):
    return '<th>{}</th>'.format(item)


def to_table_data(item):
    return '<td>{}</td>'.format(item)
