import json


class Template:
    def __init__(self, template_config):
        self.rules = []
        self.parse_config(template_config)

    def parse_config(self, template_config):
        if isinstance(template_config, str):
            template_config = json.loads(template_config)
        for rule_config in template_config.get("rules", []):
            self.add_rule(Rule(rule_config))

    def get_rules_for_page(self, page_number):
        return [rule for rule in self.rules if rule.is_applicable(page_number)]

    def add_rule(self, rule):
        self.rules.append(rule)


class Rule:
    def __init__(self, rule_config):
        self.page_numbers = rule_config.get("page_numbers", [])
        self.coordinates = rule_config.get("coordinates", [])
        self.line_delimiters = rule_config.get("line_delimiters", [])
        self.fields = rule_config.get("fields", [])
        self.ignore_page = rule_config.get("ignore_page", False)
        self.validate_config()

    def validate_config(self):
        if not self.page_numbers or not self.coordinates:
            raise ValueError(
                "Rule configuration must include page_numbers and coordinates."
            )

    def is_applicable(self, page_number):
        return page_number in self.page_numbers
