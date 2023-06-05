import rowordnet as rwn

if __name__ == "__main__":
    wn = rwn.RoWordNet()

    word = "uzufruct"

    # synset_ids = wn.synsets(literal=word)
    # synset_object = wn("ENG30-05179180-n")

    synset_id = wn.synsets("uzufruct")[
        0
    ]
    print("\nPrint all outbound relations of {}".format(wn.synset(synset_id)))
    outbound_relations = wn.outbound_relations(synset_id)
    for outbound_relation in outbound_relations:
        target_synset_id = outbound_relation[0]
        relation = outbound_relation[1]
        print(
            "\tRelation [{}] to synset {}".format(relation, wn.synset(target_synset_id))
        )
