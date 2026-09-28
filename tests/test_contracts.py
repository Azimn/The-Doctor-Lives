from pretorius.contracts import CognitiveView, Experience


def test_cognitive_view_is_renderer_neutral():
    view = CognitiveView(
        identity_roots=("Dr. Pretorius",),
        salient_memories=(),
        concerns=(),
        commitments=(),
        relationships={},
        interoception={},
    )
    assert view.identity_roots == ("Dr. Pretorius",)


def test_experience_distinguishes_observation():
    proposed = Experience(content="A renderer claimed this.", source="renderer", observed=False)
    assert proposed.observed is False
