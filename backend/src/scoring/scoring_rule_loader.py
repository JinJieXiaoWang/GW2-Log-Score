import os
import json
from typing import Dict, Any, List, Optional


class ScoringRuleLoader:
    def __init__(self):
        self.config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )
        self.scoring_rules = self._load_scoring_rules()

    def _load_scoring_rules(self) -> Dict[str, Any]:
        rules_path = os.path.join(self.config_dir, "scoring_rules.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._get_default_rules()

    def _get_default_rules(self) -> Dict[str, Any]:
        return {
            "version": "unknown",
            "default_threshold": 80,
            "profession_specialization_rules": {},
            "fallback_role_rules": {}
        }

    def get_version(self) -> str:
        return self.scoring_rules.get("version", "unknown")

    def get_mode(self) -> str:
        return self.scoring_rules.get("mode", "WvW")

    def get_threshold(self) -> int:
        return self.scoring_rules.get("default_threshold", 80)

    def get_dimension_definitions(self) -> Dict[str, Any]:
        return self.scoring_rules.get("dimension_definitions", {})

    def get_normalization_rules(self) -> Dict[str, Any]:
        return self.scoring_rules.get("normalization_rules", {})

    def get_squad_size_rules(self) -> Dict[str, Any]:
        return self.scoring_rules.get("squad_size_rules", {
            "small_squad_threshold": 20,
            "small_squad_modifiers": {}
        })

    def get_profession_specialization_rule(
        self,
        profession: str,
        specialization: str,
        stance: str = None,
        weapon: str = None
    ) -> Optional[Dict[str, Any]]:
        rules = self.scoring_rules.get("profession_specialization_rules", {})

        if stance:
            key = f"{profession}-{specialization}-{stance}"
            if key in rules:
                return rules[key]

        if weapon:
            key = f"{profession}-{specialization}-{weapon}"
            if key in rules:
                return rules[key]

        key = f"{profession}-{specialization}"
        if key in rules:
            return rules[key]

        return None

    def get_fallback_role_rule(self, role: str) -> Optional[Dict[str, Any]]:
        fallback_rules = self.scoring_rules.get("fallback_role_rules", {})
        return fallback_rules.get(role)

    def get_scoring_rule_for_player(
        self,
        profession: str,
        specialization: str = None,
        stance: str = None,
        weapon: str = None,
        role: str = None
    ) -> Dict[str, Any]:
        prof_spec_rule = self.get_profession_specialization_rule(
            profession, specialization, stance, weapon
        )
        if prof_spec_rule:
            return {
                "type": "profession_specialization",
                "rule": prof_spec_rule,
                "dimension_weights": prof_spec_rule.get("dimension_weights", {}),
                "data_sources": prof_spec_rule.get("data_sources", {})
            }

        if role:
            role_rule = self.get_fallback_role_rule(role)
            if role_rule:
                return {
                    "type": "role_fallback",
                    "rule": role_rule,
                    "dimension_weights": role_rule.get("dimension_weights", {}),
                    "data_sources": role_rule.get("data_sources", {})
                }

        default_rule = self.get_fallback_role_rule("DPS")
        return {
            "type": "default",
            "rule": default_rule,
            "dimension_weights": default_rule.get("dimension_weights", {}),
            "data_sources": default_rule.get("data_sources", {})
        }

    def get_all_dimension_keys(self) -> List[str]:
        dimensions = self.get_dimension_definitions()
        return list(dimensions.keys())


scoring_rule_loader = ScoringRuleLoader()
