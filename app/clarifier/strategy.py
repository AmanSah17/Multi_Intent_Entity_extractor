def should_clarify(intent_conf, entity_conf):
    return intent_conf < 0.6 or entity_conf < 0.5

def generate_clarification(ctx):
    if not ctx.get("intent_clarity"):
        return templates.CLARIFY_INTENT
    if not ctx.get("time_range"):
        return templates.CLARIFY_TIME_RANGE
    return "I need more detail about the vessels you're referring to."
