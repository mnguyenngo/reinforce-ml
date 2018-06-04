def render_text(doc):
    """Replaces keywords in user submission with html to highlight the keyword
    """
    output = doc.text
    nc = list(doc.noun_chunks)
    for chunk in nc:
        output = output.replace(
            chunk.text,
            '<span id="noun-chunk">' + chunk.text + '</span>')
    return output
