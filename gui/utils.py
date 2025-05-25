def wrap_text(text, font, max_width):
    """Return a list of lines, each of which will fit into max_width pixels."""
    words = text.split(' ')
    lines = []
    current = []
    for word in words:
        current.append(word)
        # measure width of “current line”
        w, _ = font.size(' '.join(current))
        if w > max_width:
            # remove last word, push line, start new
            current.pop()
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines
