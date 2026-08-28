from typing import List, Dict, Any

class RecommendationEngine:
    def __init__(self, weights: Dict[str, float] = None):
        # Default weights as per SRS Section 13.2
        self.weights = weights or {
            "skill_gap_coverage": 0.25,
            "goal_relevance": 0.2,
            "prerequisite_fit": 0.2,
            "difficulty_fit": 0.1,
            "preference_fit": 0.1,
            "career_relevance": 0.05,
            "historical_effectiveness": 0.05,
            "engagement_probability": 0.05,
            "redundancy_penalty": -0.1
        }

    def score_candidate(self, candidate: Dict[str, Any], learner_state: Dict[str, Any], skill_gap: Dict[str, Any]) -> float:
        """
        Calculate the hybrid recommendation score for a single resource candidate.
        """
        score = 0.0
        
        # 1. Skill Gap Coverage
        # Check how many of the candidate's skills match the identified skill gaps
        candidate_skills = set(candidate.get("skill_ids", []))
        gap_skills = set(skill_gap.get("missing_skills", []))
        overlap = len(candidate_skills.intersection(gap_skills))
        coverage_score = overlap / max(1, len(gap_skills))
        score += self.weights["skill_gap_coverage"] * coverage_score

        # 2. Goal Relevance (Mocked - usually from vector similarity)
        goal_relevance = candidate.get("goal_relevance_score", 0.5)
        score += self.weights["goal_relevance"] * goal_relevance

        # 3. Prerequisite Fit
        # Ensure learner meets the prerequisites for this candidate
        prerequisites = set(candidate.get("prerequisites", []))
        known_skills = set(learner_state.get("known_skills", []))
        if prerequisites.issubset(known_skills):
            prereq_fit = 1.0
        else:
            prereq_fit = 0.0
        score += self.weights["prerequisite_fit"] * prereq_fit

        # 4. Difficulty Fit
        # Compare candidate difficulty with learner level
        candidate_difficulty = candidate.get("difficulty", 0.5)
        learner_level = learner_state.get("estimated_mastery", 0.5)
        difficulty_fit = 1.0 - abs(candidate_difficulty - learner_level)
        score += self.weights["difficulty_fit"] * difficulty_fit
        
        # 5. Redundancy Penalty
        # Penalize if learner already knows skills covered by this candidate
        redundancy_overlap = len(candidate_skills.intersection(known_skills))
        if len(candidate_skills) > 0:
            redundancy_ratio = redundancy_overlap / len(candidate_skills)
            score += self.weights["redundancy_penalty"] * redundancy_ratio

        # Other factors can be implemented similarly...

        return max(0.0, score) # Ensure non-negative score

    def rank_candidates(self, candidates: List[Dict[str, Any]], learner_state: Dict[str, Any], skill_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank a list of candidate resources based on the scoring model.
        """
        scored_candidates = []
        for candidate in candidates:
            score = self.score_candidate(candidate, learner_state, skill_gap)
            candidate["recommendation_score"] = score
            scored_candidates.append(candidate)
            
        # Sort by score descending
        return sorted(scored_candidates, key=lambda x: x["recommendation_score"], reverse=True)

recommendation_engine = RecommendationEngine()
