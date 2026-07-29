from brain.domain.enums import KnowledgeType
from brain.retrieval.request import RetrievalRequest
from brain.services.selection import SelectionPolicy


class RetrievalPolicyBridge:
    def apply(
        self,
        request: RetrievalRequest,
        base_policy: SelectionPolicy,
    ) -> SelectionPolicy:
        all_existing: set[KnowledgeType] = (
            set(base_policy.required)
            | set(base_policy.preferred)
            | set(base_policy.optional)
            | set(base_policy.supplemental)
        )

        to_add: list[KnowledgeType] = []
        for kt in request.knowledge_types:
            if kt not in all_existing:
                to_add.append(kt)

        new_preferred = base_policy.preferred + tuple(to_add)

        return SelectionPolicy(
            required=base_policy.required,
            preferred=new_preferred,
            optional=base_policy.optional,
            supplemental=base_policy.supplemental,
        )
