def process_text(text, ignore_first=False, return_as_string=False):
    """
    Input:  Raw text extracted from a BS4 tag object (i.e: tag.text)
    Output: Either:
            - (Default) A list of strings, itemized by any newlines encountered
            - A single string of text, concatenated with ". "
    """
    
    text_list = [x.strip() for x in text.splitlines()]
    text_list = list(filter(bool, text_list))
    
    if ignore_first:
        text_list = text_list[1:]
    
    if return_as_string:
        return ". ".join(text_list)
    else:
        return text_list
