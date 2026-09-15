# logic_engine.py

class KnowledgeBase:
    """A declarative Knowledge Base storing Facts and Rules (Horn Clauses),
    with a Data-Driven Forward Chaining inference engine (Modus Ponens)."""

    def __init__(self):
        self.facts = set()   # unique string facts, e.g. "TargetVisible"
        self.rules = []      # list of tuples: ([premise1, premise2, ...], "conclusion")

    def tell_fact(self, fact_string):
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        self.facts = set()

    def forward_chain(self):
        """Repeatedly scans every rule, applying Modus Ponens whenever all premises
        of a rule are already known facts, until a full pass adds nothing new
        (fixed point reached)."""
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True