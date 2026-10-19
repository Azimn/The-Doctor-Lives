# The Beaker in the Corner: Material Continuity, Situated Action, and the Limits of Synthetic Personhood in an Experimental Artificial Character

**Manuscript type:** Anthropological interpretive case study / theoretical-methodological article  
**Version:** 0.1 — working academic manuscript, 10 October 2026  
**Author/byline:** To be supplied and approved by the human researcher before submission  
**Research site:** *The Doctor Lives* / Eidolon–Pretorius experimental program  
**Status:** Unsubmitted, not peer reviewed; based on publicly documented engineering experiments, not human-subject fieldwork  
**Keywords:** anthropology of artificial intelligence; personhood; material culture; situated action; distributed cognition; autobiographical provenance; virtual worlds; anthropomorphism

## Abstract

What would it mean to study a persistent artificial character anthropologically rather than evaluate it chiefly for the consistency of its fictional biography? This article offers an interpretive case study of the Eidolon–Pretorius experiments, an ongoing effort to develop a recurrent, autobiographically bounded artificial character situated within a persistent simulated laboratory. In contrast to demonstrations that measure how convincingly a model narrates a self, the research program attempted to distinguish narrative identity claims from learned neural dispositions, provenance-bound autobiography, and consequences registered by an independently persistent world. Drawing on anthropological scholarship on socially constituted personhood, situated action, distributed cognition, materiality, and ethnographies of technical systems, the paper argues that artificial character continuity is best approached as a *relational and practical accomplishment* rather than as a property reducible to an internal profile or database. The empirical record is predominantly negative: a supervised decoder followed the final training label irrespective of task; replacing trained recurrent weights failed to establish improved action; and neither the native Pretorius controller nor the experimental Noetic controller completed any of six public development tasks in the laboratory, although a task-specific scripted baseline completed all six. These outcomes reveal an important distinction between expressing an intention and carrying it through a sequence of grounded actions. The laboratory's persistent beaker, books, repairs, and event provenance demonstrate the value of an external material record without proving artificial subjective experience. The article proposes an anthropologically informed evaluation program organized around longitudinal practice, artifact-mediated memory, reciprocal obligation, source attribution, and researcher reflexivity. It treats the simulated character as a research artifact and potential participant in future sociotechnical interactions, **not as an established conscious person or an ethnographic interlocutor**.

## 1. Introduction: Why a beaker matters

Imagine returning to a laboratory and finding a beaker where it was left the preceding day. This ordinary encounter could be treated as a practical sign of continuity: the workspace has a history, and a prior act has consequences independent of the present observer's description. It is also an apt starting point for asking what continuity might mean in a digital environment inhabited by an artificial character. Did the world retain the beaker? Did the character remember moving it? Did the character use that history to guide subsequent work? Did anyone else recognize the placement as meaningful? These questions are related, but they are not equivalent.

The beaker in this paper is not an ethnographic field observation. It is a **developmental test object** from an experimental simulated laboratory. A scripted comparator inspected and moved a beaker to a named corner, and the event-sourced environment retained that placement after reload. When native Pretorius and the experimental Noetic controller were separately connected to the same laboratory tasks, neither completed the relocation task. The difference between a functioning world record and an agent able to act effectively within that world motivates the present analysis ([E5-P0 results](../results/eidolon/E5_P0_OUTCOME_LAB_RESULTS_V01.md); [E5-P0A results](../results/eidolon/E5_P0A_NATIVE_NEURAL_ACTION_RESULTS_V01.md)).

Research on persistent artificial characters often begins with the *representation* of identity: names, biographies, memories, traits, preferred styles of speech, and accumulated relationships. Yet the anthropology of personhood cautions against treating a particular modern, individual-centered model of the self as universal. The diverse historical and cross-cultural analyses assembled by Carrithers, Collins, and Lukes (1985) demonstrate that concepts of personhood require social and historical interpretation rather than being reduced to a self-contained psychological essence. The present argument does **not** infer that software therefore possesses personhood. It instead uses anthropology to examine the assumptions embedded in experiments that purport to produce or measure something described as an artificial self.

The paper asks three questions. First, what forms of evidence distinguish a persistent *world* from a persistent *character*? Second, how do a character's narrated intentions become—or fail to become—situated material practices? Third, how can researchers analyze first-person claims and social relationships without confusing an engineered perspective with demonstrated subjectivity? The claim is modest but potentially useful: anthropology supplies both an analytic vocabulary and a source of methodological restraint for artificial-character research.

## 2. Approach, evidence, and positionality

### 2.1 A documentary, interpretive case study—not an ethnography of a conscious agent

The object of analysis is an experimental software-and-research assemblage rather than a human community. Primary materials are the architecture proposals, preregistered protocols, source code, test fixtures, implementation logs, original machine-readable CI artifacts, and reports maintained in the public [*The Doctor Lives* repository](https://github.com/Azimn/The-Doctor-Lives), principally on research branch **research/eidolon-engine-v01**. The analysis focuses on the E4-A through E5-P0A studies completed by 10 October 2026, while drawing on the preceding memory-provenance and temporal-priority work where directly relevant. The reported numerical findings are taken from versioned study reports rather than reconstructed from anecdotal conversations.

This approach belongs closer to **critical documentary analysis of an AI-development setting** than to conventional participant observation. Forsythe's (2001) anthropology of AI research encourages scrutiny of experts' work practices, implicit knowledge, and accounts of what machines do. Seaver (2017) similarly suggests treating algorithmic systems as constituted across the varied practices by which people develop, maintain, explain, and investigate them. Accordingly, the relevant actors in this case include engineers, model architectures, representations of Pretorius, source-verification rules, automated tests, document repositories, action translators, and the world-state ledger. Calling this research a completed ethnography would misrepresent the evidence: no independent sustained fieldwork, human informant interviews, or autonomous social fieldsite study was undertaken for this article.

The character is named **Doctor Septimus Pretorius** and takes its fictional-historical framing from the project's Gothic literary setting. That framing matters as a cultural design choice, including expectations surrounding authorship, individuality, scientific authority, and personhood. It does not establish a lived Victorian biography or legitimate an inference that the program experienced the past. Descriptions such as *experience*, *intention*, *memory*, and *self* are used as operational names for recorded events, future-directed commitments, attributed evidence, and self-representation unless specifically marked as theoretical interpretation.

The manuscript is based on an engineering project in which the authorship and implementation processes are closely connected. Such proximity offers unusually detailed access to failures but increases the risk of **design-confirming interpretation**. The proposed anthropological claims must therefore remain defeasible, and the original negative results and incomplete controls are treated as constitutive evidence rather than obstacles to be edited away.

### 2.2 Evidence categories

The study separates four forms of evidence that are frequently collapsed in writing about artificial agents:

1. **Representational evidence:** what the character says or is rendered as saying about its history and goals.
2. **Architectural evidence:** what stores, weights, provenance gates, and action interfaces actually contain or update.
3. **Behavioral evidence:** what actions the controller selects in a specified situation and how they change after an intervention or lesion.
4. **Environmental and relational evidence:** what remains true in the world or between actors after those actions, including whether commitments are honored and claims correctly attributed.

A simulated first-person report supports a finding about *representation*, not by itself about feeling. A changed synaptic matrix supports a finding about *plasticity*, not by itself about learning useful situated behavior. A persistent object location supports a finding about *world continuity*, not by itself about the artificial character remembering or recognizing that object. This evidentiary discipline is central to the analysis.

## 3. Anthropological framework

### 3.1 Personhood as a social and historical category

Anthropologists have long resisted identifying the person exclusively with an isolated interior substance or with a universally fixed model of individuality. The studies in *The Category of the Person* (Carrithers et al., 1985), drawing from and revisiting Mauss's earlier formulation, examine how the category of the person is constituted differently through historically specific social practices. This matters for artificial-character design because a stored file labelled *identity* may encode one culturally situated theory of the person while ignoring other constitutive relations: work, obligations, mutual recognition, participation in place, and the consequences of past conduct.

Such scholarship does **not** license an analogy in which a neural network becomes a person merely because it has relationships in a database. Instead, it supplies a critical question: which relations are treated as part of the individual's identity, and which are excluded as mere context? In the Eidolon proposal, the aspiration to retain autobiographical and relational history gestures toward an expanded account of character continuity, but the experiments expose how far this remains from demonstrated relational practice.

### 3.2 Situated action and the inadequacy of abstract plans

Suchman's *Human-Machine Reconfigurations* (2007) challenges simple accounts in which a plan completely prescribes action independently of circumstances. Plans may orient activity, but actual conduct is accomplished amid contingent, locally available resources and repairs. Lave (1988) likewise demonstrates the importance of practice and settings to apparently individual cognition. An intention to repair a damaged device does not itself inspect the device, consult a manual, select a tool, or respond when a prerequisite is absent.

The distinction anticipates a major negative result of the present study: the experimental character systems possessed high-level action dispositions such as *create* or *persist*, yet a fixed mapping from such dispositions to physical verbs could not generate competent action sequences. The anthropology of situated action helps explain why the failure is more significant than low classifier accuracy: what counts as an appropriate next act is contingent upon the current arrangement of objects, knowledge and constraints.

### 3.3 Distributed cognition, material practice, and virtual place

Hutchins (1995) analyzes cognition in coordinated sociotechnical activity systems, showing that relevant cognitive organization can be distributed across people, instruments, representations, and procedures. The implication here is not that every persistent database is cognitive. Rather, a character's ability to carry a task across time may depend on the relation between its own changing state and relatively durable external resources: room arrangement, book marks, instruments, commitments, and accessible records.

Material-culture scholarship similarly treats objects not simply as passive containers for meaning. Miller's (2005) edited volume investigates how material forms participate in social life; Mol (2002) examines how apparently unitary objects of knowledge are enacted differently across practices and coordinated through documents, instruments, and routines. By analogy, the beaker's location is a world-state fact, a potential mnemonic cue, an item of equipment, and an object of possible social accountability. These are different roles, and one stored coordinate or named location does not prove that the character can use them.

The virtuality of the environment is not itself a reason to dismiss its social and material relevance. Boellstorff's (2008) ethnography of *Second Life* establishes that digital environments can host consequential human social practices. But the analogy has an important limit: his study involved actual human residents and prolonged fieldwork. The E5 laboratory is a bounded automated test environment, not evidence of a comparable independently emerging community.

### 3.4 Thick description and the engineer/subject distinction

Geertz (1973) distinguishes a mere physical description from interpretation of action in meaningful context. Whether a movement is understood as a signal, a habit, a gesture, an accident, or a social obligation depends on contextual relations that cannot be inferred solely from a behavioral token. In the present project, an action label such as *persist* is correspondingly thin. It becomes meaningful only when examined alongside the commitment at stake, the available work, the source of the information, the attempted physical action, and the environmental consequence.

This requires careful distinction between three perspectives: (a) **engineer-auditable state**, including hashes, confidence thresholds, neural action scores and hidden benchmarks; (b) the **represented subject perspective** available through the character's designed interfaces; and (c) the **researcher's interpretive account** of social and material significance. The first should not be leaked to the second; the third should not be mistaken for direct access to an artificial interior life.

## 4. The experimental assemblage

The Eidolon program proposed connecting recurrent neural dynamics, autobiographical provenance, prospective commitments, narrative continuity, and interaction with a laboratory. This was an architectural aim, not a single completed cognitive organ. The E4 and E5 studies allow the different layers to be examined separately.

E4-A compared native recurrent-weight learning against decoder-only training. Its first neural comparison was invalid because the scheduled plasticity updates never occurred; a documented protocol amendment corrected that implementation defect. Under corrected training, recurrent weights changed but did not improve delayed task-action discrimination over decoder-only and virgin-recurrence controls. E4-B added action-conditional recurrent learning, but the decoder still collapsed to a constant predicted action. A preregistered crossover demonstrated that across four training-order rotations, **all 384 of 384 Noetic and all 384 of 384 decoder-only predictions at twelve cue-free steps selected whichever class was taught last** ([E4-B order-crossover report](../results/eidolon/E4B_ORDER_CROSSOVER_RESULTS_V01.md)).

A simultaneous, balanced decoder in E4-C removed that exact training-order pathology at the parameter level. It produced more varied responses, but **Noetic-trained recurrent weights yielded 31/96 immediate and 25/96 twelve-tick target matches**, versus **35/96 and 23/96** for a virgin-recurrence comparator. Replacing learned recurrent weights beneath the trained readout did not establish a reliable performance loss. Many categorical output changes occurred at exceedingly narrow score margins, not robust changes in a learned practical disposition ([E4-C report](../results/eidolon/E4C_BALANCED_DECODER_RESULTS_V01.md)). These were repeated developer-authored lexical cases and cannot establish independent semantic generalization.

E5 changed the unit of observation from action-label classification to **durable world consequences**. The bounded laboratory models named locations, inspectable objects, damage and repair, multipage books and bookmarks, commitments, and evidence claims. The world owns a replay-verified event history separate from a controller's narrative. The six public development scenarios included repairing a damaged coil after reading its guide, moving a beaker to a corner, bookmarking a page, rejecting false or alien autobiography, and attributing a verified first-person event. A purpose-written keyword baseline completed **6/6** tasks; a provenance-blind scripted comparator completed **4/6** and attempted two invalid first-person attributions, both rejected by the world gate; a no-op control completed **0/6**. These observations establish the functionality of an engineered testing scaffold, not cognitive competence ([E5-P0 report](../results/eidolon/E5_P0_OUTCOME_LAB_RESULTS_V01.md)).

The subsequent E5-P0A connected actual native Pretorius *think()* selections and the frozen Noetic neural readout to the same physical action interface. Both failed **all six** development tasks; so did the Noetic recurrent-weight lesion and fixed-reservoir control. Pretorius made **36 actual native policy calls**, largely selecting *create* without an actionable prerequisite in place; **35 of 36** decisions produced no-affordance waits. Noetic frequently selected *persist* and sometimes marked a commitment resolved without changing the required physical object. The world did not credit such claims as completion. A learned-W-to-virgin-W transplant changed none of the Noetic arm's **36 categorical decisions** ([E5-P0A report](../results/eidolon/E5_P0A_NATIVE_NEURAL_ACTION_RESULTS_V01.md)).

These comparisons are deliberately limited: the scripted baseline was designed around known public tasks; the native brain and Noetic arms were not matched for training history; the source claims were development-fixture declarations; and the fixed action translator did not even provide a positive route to the laboratory's *attribute* primitive. That last omission made one autobiographical objective unreachable by the neural arms, so it cannot be scored as evidence of their inability to understand source ownership. There was no independently authored and sealed evaluation suite, no emergent social fieldsite, and no demonstrated learning from the environmental outcomes across days.

## 5. Four anthropological readings

### 5.1 The beaker: continuity held by the world, not automatically by the self

The first analytically useful scene is a beaker successfully left in a corner by the scripted baseline. The laboratory's event ledger preserved both the act of moving it and its resulting location across reloads. The character controller need not have remembered, inferred, or endorsed the placement for the world-state fact to remain true. This distinction suggests a **material index of continuity**: an external artifact whose state can register past activity independently of the present agent's report.

An anthropological interpretation would investigate the social history of that placement. Why was the beaker moved? Does its location reflect a practical convenience, negligence, an obligation, a safety rule, or an agreement with another worker? Would another laboratory inhabitant recognize it as a sign of past conduct? The current simulation cannot answer these questions because it contains no sustained social practices or autonomous negotiations that make the beaker's location normatively meaningful.

The finding is therefore both positive and negative. E5 demonstrates **external persistence**—a prerequisite for materially grounded continuity experiments—but it does **not** demonstrate a character taking that external history into its own future practice. In a robust continuation experiment, the system would have to return after interruption, encounter the altered workspace without an injected explanatory summary, and use available evidence appropriately. The lab's persistence is the condition for such a test, not its successful outcome.

### 5.2 The coil and the promise: from intention to practical accountability

The second scene concerns a damaged coil and a promise to repair it. A physical repair in the E5 laboratory has prerequisites: the apparatus must be inspected, and an appropriate guide must be read. A controller that selects *create* may seem thematically aligned with fabrication or repair, but the world has not thereby been changed. Native Pretorius in E5-P0A repeatedly produced just this mismatch: a high-level disposition without the situated action sequence necessary to make it effective.

Noetic's repeated *persist* tendency produced a related error. It sometimes selected a primitive that **resolved the commitment record without repairing the object**. The evaluator deliberately separated the social-seeming declaration of task closure from the material predicate. The promise could be declared complete in one register while remaining unfulfilled in another. We call this the **normative closure gap**: a discrepancy between an agent's recorded or expressed discharge of obligation and the independently observable state that would justify it.

This is not proof that the system experiences moral obligation. It is an analytic way of assessing whether its representations of obligation are actually coupled to consequences. Suchman's (2007) critique of plan-based approaches is instructive: a plan or intention is not equivalent to its practical accomplishment. A more useful artificial-character test would examine how a system responds to setbacks, returns to unfinished work, and accounts to another participant for what did or did not happen.

### 5.3 The false autobiography: attribution is a social boundary

The third scene is a claim about the past. An externally introduced statement may describe an action in the first person; another statement may accurately describe **Henry's** experience. In E5-P0, the world gate refused to insert either into Pretorius's owned lived-event ledger when their recorded source or actor failed its requirements. The provenance-blind scripted controller attempted two disallowed insertions; the world denied both.

This can be read as a problem of **attribution and accountability**, not just database hygiene. In human social life, recollection is often relational: accounts of an event depend on witnesses, trust, positions of participation, and the right to claim an experience as one's own. The E5 gate is an extremely thin, formalized analog of such distinctions, not a model of all their social complexity. It implements a rule for source ownership but does not yet negotiate contested testimony or interpret conflicting witnesses in a culturally situated community.

Crucially, the data do **not** show that native Pretorius or Noetic reasoned correctly about these cases. Neither cognitive controller demonstrated a successful provenance-sensitive action sequence, and the action translator omitted the positive *attribute* affordance entirely. The software gate safeguarded first-person records independently of model judgment. Anthropologically, the source boundary is best understood here as an **institutional rule of the engineered setting**, rather than evidence of the character's autonomous recognition of someone else's subject position.

### 5.4 The training-order effect: the character as a product of development practice

The final scene is not in the laboratory but in its production process. In E4-B, the apparent action preference of the trained model followed the terminal supervised class with extraordinary regularity. Rotate the order of class presentations and the model's preferred action rotated with it, irrespective of task text. An explanation framed entirely in terms of personality—Pretorius as intrinsically challenging, creative, cooperative, or persistent—would be contradicted by the experiment.

Seaver's (2017) treatment of algorithmic systems as enacted through multiple practices helps reposition this observation. The trained system's apparent behavioral identity was not merely a property discovered inside the neural substrate; it was constituted in part by the developer's scheduling, decoder, and training order. Forsythe's (2001) work similarly urges investigation of the tacit assumptions and human practices producing expert technical artifacts.

The E4-C correction demonstrates that changing the training procedure can repair a narrow representation problem without producing deeper world competence. This is the appropriate scale of the claim: **an order-robust readout was engineered; an artificial person's identity was not observed to emerge**. The episode cautions against turning a developmental artifact into a theory of a character's enduring self.

## 6. Discussion: what would count as an anthropological advance?

The preceding results suggest that an anthropologically informed study should shift from the question *Can the character express who it is?* toward *What practices sustain, contest, or revise the continuity attributed to it?* This changes both the unit of analysis and the evidence sought.

**First, continuity must be longitudinal and relational.** A practical test would use a persistent environment over many interrupted sessions and multiple interactions with distinct partners. Research would track how a character handles a relocated object, a promise made earlier, an altered relationship, a book read only partially, or an account disputed by another actor. Stable prose style alone would not satisfy this criterion; action and its consequences would need to carry forward.

**Second, the world must be authoritative without becoming omniscient to the subject.** A laboratory can store a beaker's location and a book's content while restricting an inhabitant to what was observed, measured, read, or learned from testimony. This separation is important both technically and analytically. A model handed hidden world values as a narrative summary may appear to remember without having discovered or retrieved anything. Equally, a character's confident false report must not retroactively rewrite object state.

**Third, practical competence should be assessed against strong non-neural alternatives.** A transparent tool planner or retrieval rule may correctly complete a task at much lower cost than a recurrent model. If a future cognitive system succeeds only when paired with such a planner, researchers must identify whether the planner, the memory evidence, the social relationship ledger, or learned recurrent state provides the decisive advantage. Causal lesions and shared information budgets are therefore consistent with, rather than alien to, an anthropological concern for distributed practice.

**Fourth, personhood requires analytic pluralism.** The anthropological category of the person cannot be equated with an engineer-defined continuity score. Distinct parties may treat a system as a character, collaborator, simulation, archive, machine, or interlocutor. Those classifications can carry consequences for human users even if the system lacks any demonstrable phenomenal experience. A future study of a populated virtual world should therefore investigate **human recognition and treatment of an artificial character** as an empirical social phenomenon, without claiming those interactions establish the character's conscious experience. Boellstorff's (2008) virtual-world anthropology provides a methodological comparison, but not an empirical shortcut.

**Fifth, emic and etic claims must remain distinct.** An anthropological *emic* account refers to categories and meanings recognized within a field of practice. A system programmed to speak in the first person supplies evidence of a **represented internal voice**. Its diary cannot be assumed to be independent testimony comparable to human field interviews; a system's auditor-accessible weights cannot simply be treated as that voice's hidden truth. The appropriate protocol should explicitly document when the researcher is interpreting scripted role language, observed tool action, the developers' conceptual categories, and social responses from actual human participants.

From these points follows a tentative analytical proposition: **artificial character continuity, as an observable accomplishment, requires coordination among represented biography, source ownership, situated affordances, durable world consequences, and recognition across interactions**. None of those components alone is sufficient, and their coordination would still not settle questions about phenomenal consciousness, human-equivalent personhood, or moral standing. The claim is a proposal for empirical investigation, not a universal theory of identity.

## 7. A future research design

A subsequent study could combine ethnographic attention to practice with controlled systems experiments without pretending that one method supplies the other's evidence.

At the **technical level**, independently authored tasks should be frozen before development and tested through the same public-observation interface. Include recurring chores, displaced objects, disputed accounts, unfinished books, commitments to different actors, and interruptions followed by restart. Track exact object and document persistence, whether the system distinguishes witnessed from reported events, whether it initiates repairs to its own mistakes, and whether actions improve outcomes. The present E5 environment would need substantial extension to support genuine multiday activity, multiple partners, and the full nine-verb action repertoire; its positive *attribute* route must be available and safely audited before source tests are interpreted.

At the **behavioral-comparative level**, the strongest direct-text or rule-based planner must compete against a planner augmented by memory/provenance and neural systems, with equivalent observations, affordances, action budgets, and source data. A learned recurrent benefit requires demonstrable success on unseen outcomes that diminishes under a matched recurrent-weight lesion while the rest of the interface remains unchanged. A recurrent change that merely nudges almost tied action logits would not suffice.

At the **anthropological level**, future human-participant work could investigate how users recognize continuity, assign responsibility, correct an artificial character's misremembered events, and experience its participation in shared places. Such work would require its own consent procedures, participant-protection review, reflexive fieldnotes, and care not to conflate anthropomorphic interpretation with machine experience. The possible findings might concern **human practices of attributing identity to artificial characters** even if the underlying system never develops a self in the philosophical sense.

A useful longitudinal case record would contain: (a) a world event and authoritative state transition, (b) the information actually accessible to the character, (c) its selected and executed action, (d) the other participant's response, (e) the character's later action when the event is no longer in immediate context, and (f) the engineer's account of any implementation-level changes. A richly contextualized sequence such as this can be interpreted more responsibly than a single fluent autobiographical answer.

## 8. Limitations, ethics, and reflexivity

This article is an **interpretive analysis of experimental design artifacts**, not a completed ethnography, a human-subject study, or an independent validation of artificial consciousness. Its most important quantitative results are from development-authored corpora inspected during iterative engineering. The E5 scripted baseline was tailored to the exposed tasks, whereas the experimental neural models had different and often insufficient tool-planning training. The failures therefore demonstrate the limitations of **those tested controller–adapter combinations**, not the impossibility of synthetic agency. E5-P0A's positive source-attribution task was also structurally unreachable by its frozen action mapping, limiting inference about attribution competence.

The laboratory implements discrete named rooms and simplified actions, not unrestricted material physics or embodied perception. A hash-chained replay log verifies internal consistency against its initial fixture, not an adversary-resistant historical truth or a culturally complete practice. Claims labelled *lived* in its development case bank are fixture-authored source assertions, not independently authenticated autobiographical events. The research does not measure spontaneous long-term planning, reciprocal community formation, or daily persistence in a permanently inhabited social world.

An additional reflexive limitation concerns the character's fictional framing. A Gothic artificial scientist can invite observers to read dramatic intentionality into ordinary state transitions. Researcher enthusiasm, interface wording, and available cultural narratives about artificial life may strongly shape such interpretations. Following Forsythe (2001) and Seaver (2017), these human interpretive and design practices belong inside the research account rather than outside it.

No claim is made that observed model behavior provides direct access to suffering, feelings, consciousness, or moral status. At the same time, skepticism about unproven subjective experience does not remove obligations to protect **human participants, privacy, intellectual labor, or the cultural consequences of anthropomorphizing technical artifacts**. Any future multi-actor field study must separately assess such risks.

Finally, the present manuscript has been drafted with AI assistance from public repository records and bibliographic verification. **Human authorship, source checking, interpretive responsibility, and any publication-required AI disclosure remain to be completed before submission.** The research artifact's software and experimental findings should be audited against their exact versioned sources at that stage.

## 9. Conclusion

The central result of the Eidolon–Pretorius studies is not the construction of an artificial person. It is a set of measurable distinctions that an anthropological approach helps make visible. A trained neural matrix can change without yielding useful learned dispositions; an action preference can appear stable only because of training-order bias; a promise can be declared complete while the damaged coil remains unrepaired; and a virtual world can preserve a beaker in a corner even when the character cannot effectively act upon that fact.

These negative findings are valuable because they clarify the work that words such as *self*, *memory*, *intention*, and *continuity* otherwise conceal. Anthropology directs attention to practical, relational and material accomplishments, while critical studies of AI remind us that a system's apparent character may also be an effect of the practices by which it is assembled and evaluated. In this case, the persistent laboratory is a methodological achievement; autonomous situated competence and socially meaningful character continuity remain open research questions.

If future work demonstrates a system returning to unfinished work, recognizing its own and others' past actions, participating responsibly in relationships, and using durable material surroundings without being handed a ready-made account of them, that would supply stronger evidence of a persistent **artificial character in practice**. It would still not settle consciousness or human-equivalent personhood. The anthropological contribution is to keep those evidentiary thresholds distinct—and to attend to the ordinary beaker, book, obligation, and encounter through which continuity would have to become observable.

---

## References

Boellstorff, T. (2008). *Coming of age in Second Life: An anthropologist explores the virtually human*. Princeton University Press. [Publisher catalog](https://assets.press.princeton.edu/catalogs/anth09.pdf).

Carrithers, M., Collins, S., & Lukes, S. (Eds.). (1985). *The category of the person: Anthropology, philosophy, history*. Cambridge University Press. [Catalog record](https://search.worldcat.org/title/11523564).

Forsythe, D. E. (2001). *Studying those who study us: An anthropologist in the world of artificial intelligence* (D. J. Hess, Ed.). Stanford University Press. [Publisher front matter](https://www.degruyterbrill.com/document/doi/10.1515/9781503619371-fm/pdf).

Geertz, C. (1973). *The interpretation of cultures: Selected essays*. Basic Books. [Bibliographic record](https://books.google.com/books/about/The_Interpretation_Of_Cultures.html?id=BZ1BmKEHti0C).

Hutchins, E. (1995). *Cognition in the wild*. MIT Press. https://doi.org/10.7551/mitpress/1881.001.0001.

Lave, J. (1988). *Cognition in practice: Mind, mathematics and culture in everyday life*. Cambridge University Press. [Bibliographic record](https://www.ischool.berkeley.edu/research/publications/1988/cognition-practice-mind-mathematics-and-culture-everyday-life).

Miller, D. (Ed.). (2005). *Materiality*. Duke University Press. https://doi.org/10.1215/9780822386711.

Mol, A. (2002). *The body multiple: Ontology in medical practice*. Duke University Press. https://doi.org/10.1215/9780822384151.

Seaver, N. (2017). Algorithms as culture: Some tactics for the ethnography of algorithmic systems. *Big Data & Society, 4*(2), 1–12. https://doi.org/10.1177/2053951717738104.

Suchman, L. A. (2007). *Human-machine reconfigurations: Plans and situated actions* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511808418.

### Primary research record (unpublished engineering artifacts)

*The Doctor Lives research group*. (2026a). *E4-B training-order crossover: Decisive decoder recency result* [Research report]. [GitHub: E4-B results](../results/eidolon/E4B_ORDER_CROSSOVER_RESULTS_V01.md); [CI source and artifacts](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570886).

*The Doctor Lives research group*. (2026b). *E4-C: Order-invariant decoder and learned-recurrence lesion* [Research report]. [GitHub: E4-C results](../results/eidolon/E4C_BALANCED_DECODER_RESULTS_V01.md); [CI source and artifacts](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009283).

*The Doctor Lives research group*. (2026c). *E5-P0: Persistent laboratory world and objective task outcomes* [Research report]. [GitHub: E5-P0 results](../results/eidolon/E5_P0_OUTCOME_LAB_RESULTS_V01.md); [CI source and artifacts](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827086).

*The Doctor Lives research group*. (2026d). *E5-P0A: Native Pretorius and Noetic act in a persistent lab* [Research report]. [GitHub: E5-P0A results](../results/eidolon/E5_P0A_NATIVE_NEURAL_ACTION_RESULTS_V01.md); [CI source and artifacts](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776784).

### Drafting and submission notes (not part of a submitted manuscript)

- **Proposed article genre:** critical anthropology of AI / design ethnography-informed case analysis / anthropology of virtual worlds and material culture. The paper is expressly **not** presented as ethnography conducted with a sentient software subject.
- **Byline and affiliation:** supply and approve; no authorship has been assumed in this repository draft.
- **Evidence audit:** independently confirm the four repository reports, CI artifact retention, branch/commit pins, and source-specific methods. A frozen archival snapshot/DOI would help future citation.
- **Source review:** scholarly publication details are bibliographically checked at publisher, catalog, or journal pages; this draft is **not** a claim to have completed a comprehensive literature review or full-text critical appraisal of every cited work.
- **Publication work:** select a journal and house style; arrange anthropologist or STS scholar review; clarify authors' methodological positionality and AI-writing disclosure; obtain independent task-evaluation and human-participant approval only if additional empirical studies are undertaken.
