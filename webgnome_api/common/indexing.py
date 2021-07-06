
import docutils.core
import pprint

def iter_keywords(str):
    lines = str.splitlines()
    in_tr = False
    ret = set()
    for lin in lines:
        if in_tr:
            keyword = lin.strip().lower()
            ret.add(keyword)
        if "keywords" in lin or "keyword" in lin:
            in_tr = True
        else:
            in_tr = False
    return ', '.join(sorted(ret))

# NOTE: Use 'sorted(set(...)' to collapse duplicates.
# NOTE: Use 'str.lower()' to standardize on lower case.


'''
# Unquote this section for hacking and run under 'python -i'.
# Then inspect the 'doc' and 'pub' variables.

# 'internals' copied from 'examples.py' in Docutils 0.12 source distribution.
def internals(input_string, source_path=None, destination_path=None,
              input_encoding='unicode', settings_overrides=None):
    """
    Return the document tree and publisher, for exploring Docutils internals.

    Parameters: see `html_parts()`.
    """
    if settings_overrides:
        overrides = settings_overrides.copy()
    else:
        overrides = {}
    overrides['input_encoding'] = input_encoding
    output, pub = docutils.core.publish_programmatically(
        source_class=docutils.io.StringInput, source=input_string,
        source_path=source_path,
        destination_class=docutils.io.NullOutput, destination=None,
        destination_path=destination_path,
        reader=None, reader_name='standalone',
        parser=None, parser_name='restructuredtext',
        writer=None, writer_name='null',
        settings=None, settings_spec=None, settings_overrides=overrides,
        config_section=None, enable_exit_status=None)
    return pub.writer.document, pub

doc, pub = internals(TEXT, input_encoding="utf-8")
'''
