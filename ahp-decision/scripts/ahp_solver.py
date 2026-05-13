"""
AHP solver - calculations for the Analytic Hierarchy Process method.

Functions:
- compute_priorities(matrix): eigenvector + Consistency Ratio
- find_most_inconsistent_pair(matrix): locates the pair that most disrupts consistency
- aggregate(criteria_weights, alternative_matrices): final ranking of alternatives
- normalize_hard_data(values, benefit=True): convert hard data into AHP weights

Command-line usage:
    python ahp_solver.py --matrix '[[1,3,5],[1/3,1,2],[1/5,1/2,1]]'
"""

import json
import argparse
import numpy as np
from typing import List, Tuple, Dict


# Random Index for different matrix sizes (Saaty 1980)
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
}


def compute_priorities(matrix: List[List[float]]) -> Dict:
    """
    Computes the priority vector (weights) and Consistency Ratio for a
    comparison matrix.

    Uses the eigenvector method - the dominant eigenvector normalized
    to sum to 1.

    Returns dict: {
        'weights': [...],
        'lambda_max': float,
        'CI': float,    # Consistency Index
        'CR': float,    # Consistency Ratio
        'consistent': bool
    }
    """
    A = np.array(matrix, dtype=float)
    n = A.shape[0]

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix must be square")

    eigenvalues, eigenvectors = np.linalg.eig(A)

    # Take the largest (real) eigenvalue
    max_idx = np.argmax(eigenvalues.real)
    lambda_max = eigenvalues[max_idx].real
    principal_eigenvector = eigenvectors[:, max_idx].real

    # Normalize to sum to 1
    weights = principal_eigenvector / principal_eigenvector.sum()
    weights = np.abs(weights)  # guard against negative signs

    # Consistency Index and Consistency Ratio
    CI = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    RI = RI_TABLE.get(n, 1.59)
    CR = CI / RI if RI > 0 else 0.0

    return {
        'weights': weights.tolist(),
        'lambda_max': float(lambda_max),
        'CI': float(CI),
        'CR': float(CR),
        'consistent': bool(CR <= 0.10),
        'n': n
    }


def find_most_inconsistent_pair(matrix: List[List[float]]) -> Tuple[int, int, float]:
    """
    Finds the pair (i, j) that most disrupts consistency.

    Idea: for each pair we compare a_ij with (w_i / w_j).
    The larger the deviation ratio, the more "responsible" the pair is for
    the inconsistency.

    Returns: (i, j, deviation_factor) - i, j are indices,
    deviation_factor shows how far a_ij departs from the ideal w_i/w_j.
    """
    A = np.array(matrix, dtype=float)
    n = A.shape[0]
    result = compute_priorities(matrix)
    weights = np.array(result['weights'])

    worst_pair = (0, 1)
    worst_deviation = 0.0

    for i in range(n):
        for j in range(i + 1, n):
            ideal = weights[i] / weights[j]
            actual = A[i][j]
            # relative deviation on a logarithmic scale
            deviation = abs(np.log(actual) - np.log(ideal))
            if deviation > worst_deviation:
                worst_deviation = deviation
                worst_pair = (i, j)

    i, j = worst_pair
    suggested_value = weights[i] / weights[j]
    return {
        'i': int(i),
        'j': int(j),
        'current_value': float(A[i][j]),
        'suggested_value': float(suggested_value),
        'deviation_log': float(worst_deviation)
    }


def aggregate(criteria_weights: List[float],
              alternative_matrices: List[List[List[float]]]) -> Dict:
    """
    Final synthesis: for each alternative computes a weighted sum of its
    weights across all criteria.

    criteria_weights: criteria weights [w1, w2, ..., wN]
    alternative_matrices: list of N alternative comparison matrices
                          (one per criterion)

    Returns dict with final scores and ranking.
    """
    n_criteria = len(criteria_weights)
    if len(alternative_matrices) != n_criteria:
        raise ValueError(
            f"Number of alternative matrices ({len(alternative_matrices)}) "
            f"must equal the number of criteria ({n_criteria})"
        )

    # For each criterion compute the alternatives' priority vector
    alt_priorities_per_criterion = []
    consistency_per_criterion = []
    for idx, mat in enumerate(alternative_matrices):
        result = compute_priorities(mat)
        alt_priorities_per_criterion.append(result['weights'])
        consistency_per_criterion.append({
            'CR': result['CR'],
            'consistent': bool(result['consistent'])
        })

    # Aggregation: final_score[k] = sum_i (criteria_weights[i] * alt_priorities[i][k])
    n_alternatives = len(alt_priorities_per_criterion[0])
    final_scores = np.zeros(n_alternatives)

    for i, w_crit in enumerate(criteria_weights):
        alt_weights = np.array(alt_priorities_per_criterion[i])
        final_scores += w_crit * alt_weights

    # Ranking
    ranking = np.argsort(-final_scores).tolist()

    return {
        'final_scores': final_scores.tolist(),
        'ranking': ranking,
        'alt_priorities_per_criterion': [
            list(p) for p in alt_priorities_per_criterion
        ],
        'consistency_per_criterion': consistency_per_criterion
    }


def normalize_hard_data(values: List[float], benefit: bool = True) -> List[float]:
    """
    Convert objective numeric data into AHP weights (summing to 1).

    benefit=True: larger is better (e.g. performance, salary, battery life)
    benefit=False: smaller is better (e.g. price, commute time, weight)

    For 'cost' (benefit=False) we use reciprocals.
    """
    arr = np.array(values, dtype=float)
    if not benefit:
        # guard against division by zero
        arr = 1.0 / np.maximum(arr, 1e-9)
    return (arr / arr.sum()).tolist()


def analyze_sensitivity(criteria_weights: List[float],
                        alternative_matrices: List[List[List[float]]],
                        winner_idx: int = None) -> Dict:
    """
    Simple sensitivity analysis: by how much each criterion's weight would
    need to change for the winner to change.

    Returns, for each criterion, the smallest weight change (delta) that
    flips the winner.
    """
    base_result = aggregate(criteria_weights, alternative_matrices)
    base_scores = np.array(base_result['final_scores'])
    if winner_idx is None:
        winner_idx = int(np.argmax(base_scores))

    n_criteria = len(criteria_weights)
    sensitivity = []

    for crit_idx in range(n_criteria):
        # Sweep this criterion's weight from 0 to 1, redistributing the rest proportionally
        original_w = criteria_weights[crit_idx]
        smallest_change = None

        for delta in np.arange(0.01, 1.0, 0.01):
            for direction in [+1, -1]:
                new_w = original_w + direction * delta
                if new_w < 0 or new_w > 1:
                    continue
                # redistribute
                others_sum = 1.0 - original_w
                if others_sum < 1e-9:
                    continue
                scale = (1.0 - new_w) / others_sum
                new_weights = [
                    new_w if i == crit_idx else criteria_weights[i] * scale
                    for i in range(n_criteria)
                ]
                new_result = aggregate(new_weights, alternative_matrices)
                new_winner = int(np.argmax(new_result['final_scores']))
                if new_winner != winner_idx:
                    smallest_change = delta
                    break
            if smallest_change is not None:
                break

        sensitivity.append({
            'criterion_idx': crit_idx,
            'original_weight': original_w,
            'min_change_to_flip_winner': smallest_change  # None = not possible in range
        })

    return {
        'winner_idx': winner_idx,
        'sensitivity': sensitivity
    }


# CLI
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AHP solver')
    parser.add_argument('--matrix', type=str, required=False,
                        help='Comparison matrix as JSON, e.g. [[1,3],[0.333,1]]')
    parser.add_argument('--mode', type=str, default='priorities',
                        choices=['priorities', 'inconsistency'],
                        help='priorities = compute weights+CR; inconsistency = find the worst pair')
    args = parser.parse_args()

    if args.matrix:
        matrix = json.loads(args.matrix)
        if args.mode == 'priorities':
            result = compute_priorities(matrix)
        else:
            result = find_most_inconsistent_pair(matrix)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Test
        test_matrix = [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]
        print("Test - 3x3 matrix (price, quality, brand):")
        print(json.dumps(compute_priorities(test_matrix), indent=2, ensure_ascii=False))
