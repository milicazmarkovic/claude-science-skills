"""Pure-chemistry helpers for the ketcher-canvas-default skill.

These run in the python compute kernel (Indigo-backed). They do NOT touch the
Ketcher canvas themselves — MCP/app calls (open_sketcher/set_structure/
get_structure/highlight_atoms) only work from the repl tool. Use these to
prepare structures/indices, then push results via set_structure from repl.
"""


def inchi_to_smiles(inchi):
    """InChI string -> canonical SMILES (Indigo). InChIKey is a hash and
    cannot be decoded here — look it up via PubChem first."""
    from indigo import Indigo
    from indigo.inchi import IndigoInchi
    ind = Indigo()
    ii = IndigoInchi(ind)
    return ii.loadMolecule(inchi).canonicalSmiles()


def smiles_to_inchi(smiles):
    """SMILES -> (InChI, InChIKey) via Indigo."""
    from indigo import Indigo
    from indigo.inchi import IndigoInchi
    ind = Indigo()
    ii = IndigoInchi(ind)
    inchi = ii.getInchi(ind.loadMolecule(smiles))
    return inchi, ii.getInchiKey(inchi)


def map_reaction(rxn_smiles, mode="discard"):
    """Assign atom-atom mapping numbers to a reaction SMILES and return the
    mapped reaction SMILES (ready for set_structure(rxn=...)). mode is one of
    'discard' | 'keep' | 'alter' | 'clear'."""
    from indigo import Indigo
    ind = Indigo()
    rxn = ind.loadReaction(rxn_smiles)
    rxn.automap(mode)
    return rxn.smiles()


def canvas_order_match(molfile, smarts):
    """Return matched atom indices IN CANVAS (molfile) ORDER so they can be
    passed straight to highlight_atoms. Matching against the canvas molfile
    (not a SMILES) keeps indices aligned with the Ketcher canvas."""
    from indigo import Indigo
    ind = Indigo()
    target = ind.loadMolecule(molfile)
    query = ind.loadSmarts(smarts)
    matcher = ind.substructureMatcher(target)
    m = matcher.match(query)
    if m is None:
        return []
    idx = []
    for qa in query.iterateAtoms():
        ta = m.mapAtom(qa)
        if ta is not None:
            idx.append(ta.index())
    return idx


def render_structure(smiles_or_rxn, out_path, is_reaction=False, width=900, fmt="png"):
    """Render a molecule or reaction to an image file via Indigo. Returns the
    path. Caller is responsible for save_artifacts(out_path)."""
    from indigo import Indigo
    from indigo.renderer import IndigoRenderer
    ind = Indigo()
    ren = IndigoRenderer(ind)
    ind.setOption("render-output-format", fmt)
    ind.setOption("render-image-width", width)
    obj = ind.loadReaction(smiles_or_rxn) if is_reaction else ind.loadMolecule(smiles_or_rxn)
    obj.layout()
    ren.renderToFile(obj, out_path)
    return out_path
