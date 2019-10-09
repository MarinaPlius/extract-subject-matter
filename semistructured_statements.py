import itertools
from spacy.parts_of_speech import CONJ, DET, NOUN, VERB

def semistructured_statements(
    doc, entity, *, cue="be", ignore_entity_case=True, min_n_words=1, max_n_words=20
):
    """
    Extract "semi-structured statements" from a spacy-parsed doc, each as a
    (entity, cue, fragment) triple. This is similar to subject-verb-object triples.
    Args:
        doc (:class:`spacy.tokens.Doc`)
        entity (str): a noun or noun phrase of some sort (e.g. "President Obama",
            "global warming", "Python")
        cue (str): verb lemma with which ``entity`` is associated
            (e.g. "talk about", "have", "write")
        ignore_entity_case (bool): if True, entity matching is case-independent
        min_n_words (int): min number of tokens allowed in a matching fragment
        max_n_words (int): max number of tokens allowed in a matching fragment
    Yields:
        (:class:`spacy.tokens.Span` or :class:`spacy.tokens.Token`, :class:`spacy.tokens.Span` or :class:`spacy.tokens.Token`, :class:`spacy.tokens.Span`):
        where each element is a matching (entity, cue, fragment) triple
    Notes:
        Inspired by N. Diakopoulos, A. Zhang, A. Salway. Visual Analytics of
        Media Frames in Online News and Blogs. IEEE InfoVis Workshop on Text
        Visualization. October, 2013.
        Which itself was inspired by by Salway, A.; Kelly, L.; Skadiņa, I.; and
        Jones, G. 2010. Portable Extraction of Partially Structured Facts from
        the Web. In Proc. ICETAL 2010, LNAI 6233, 345-356. Heidelberg, Springer.
    """
    if ignore_entity_case is True:
        entity_toks = entity.lower().split(" ")
        get_tok_text = lambda x: x.lower_
    else:
        entity_toks = entity.split(" ")
        get_tok_text = lambda x: x.text
    first_entity_tok = entity_toks[0]
    n_entity_toks = len(entity_toks)
    cue = cue.lower()
    cue_toks = cue.split(" ")
    n_cue_toks = len(cue_toks)

    def is_good_last_tok(tok):
        if tok.is_punct:
            return False
        if tok.pos in {CONJ, DET}:
            return False
        return True

    for sent in doc.sents:
        for tok in sent:

            # filter by entity
            if get_tok_text(tok) != first_entity_tok:
                continue
            if n_entity_toks == 1:
                the_entity = tok
                the_entity_root = the_entity
            if tok.i + n_cue_toks >= len(doc):
                continue
            elif all(
                get_tok_text(tok.nbor(i=i + 1)) == et
                for i, et in enumerate(entity_toks[1:])
            ):
                the_entity = doc[tok.i : tok.i + n_entity_toks]
                the_entity_root = the_entity.root
            else:
                continue

            # filter by cue
            terh = the_entity_root.head
            if terh.lemma_ != cue_toks[0]:
                continue
            if n_cue_toks == 1:
                min_cue_i = terh.i
                max_cue_i = terh.i + n_cue_toks
                the_cue = terh
            elif all(
                terh.nbor(i=i + 1).lemma_ == ct for i, ct in enumerate(cue_toks[1:])
            ):
                min_cue_i = terh.i
                max_cue_i = terh.i + n_cue_toks
                the_cue = doc[terh.i : max_cue_i]
            else:
                continue
            if the_entity_root in the_cue.rights:
                continue

            # now add adjacent auxiliary and negating tokens to the cue, for context
            try:
                min_cue_i = min(
                    left.i
                    for left in itertools.takewhile(
                        lambda x: x.dep_ in {"aux", "neg"},
                        reversed(list(the_cue.lefts)),
                    )
                )
            except ValueError:
                pass
            try:
                max_cue_i = max(
                    right.i
                    for right in itertools.takewhile(
                        lambda x: x.dep_ in {"aux", "neg"}, the_cue.rights
                    )
                )
            except ValueError:
                pass
            if max_cue_i - min_cue_i > 1:
                the_cue = doc[min_cue_i:max_cue_i]
            else:
                the_cue = doc[min_cue_i]

            # filter by fragment
            try:
                min_frag_i = min(right.left_edge.i for right in the_cue.rights)
                max_frag_i = max(right.right_edge.i for right in the_cue.rights)
            except ValueError:
                continue
            while is_good_last_tok(doc[max_frag_i]) is False:
                max_frag_i -= 1
            n_fragment_toks = max_frag_i - min_frag_i
            if (
                n_fragment_toks <= 0
                or n_fragment_toks < min_n_words
                or n_fragment_toks > max_n_words
            ):
                continue
            # HACK...
            if min_frag_i == max_cue_i - 1:
                min_frag_i += 1
            the_fragment = doc[min_frag_i : max_frag_i + 1]

            yield (the_entity, the_cue, the_fragment)