#!/usr/bin/env python3
"""
Planificador con BFS simple (PDDL).
"""
from collections import deque
from itertools import product
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def parse_pddl(path):
    raw = re.sub(r";[^\n]*", "", path.read_text(encoding="utf-8"))
    tokens = re.findall(r"\(|\)|[^\s()]+", raw.lower())
    stack = []
    result = None
    for token in tokens:
        if token == "(":
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError(f"Parentesis ')' inesperado en {path}")
            node = stack.pop()
            if not stack:
                if result is not None:
                    raise ValueError("Solo se esperaba una expresion principal")
                result = node
        else:
            if not stack:
                raise ValueError(f"Token fuera de parentesis: {token}")
            stack[-1].append(token)
    if stack or result is None:
        raise ValueError(f"Parentesis desbalanceados en {path}")
    return result


def typed_elements(tokens):
    """Convierte [x, y, -, tipo] en [(x,tipo),(y,tipo)]."""
    pending = []
    output = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "-":
            if not pending or i + 1 == len(tokens):
                raise ValueError("Declaracion de tipos no valida")
            output.extend((name, tokens[i + 1]) for name in pending)
            pending = []
            i += 2
        else:
            pending.append(tokens[i])
            i += 1
    output.extend((name, "object") for name in pending)
    return output


def atoms(expr):
    if expr[0] == "and":
        return expr[1:]
    return [expr]


def substitute(atom, mapping):
    return tuple(mapping.get(term, term) for term in atom)


def parse_domain(tree):
    assert tree[0] == "define"
    name = next(x[1] for x in tree if isinstance(x, list) and x[0] == "domain")
    parts = {p[0]: p for p in tree[1:] if isinstance(p, list) and p[0] != ":action"}
    predicate_defs = parts[":predicates"][1:]
    predicates = {p[0]: len([t for t in p[1:] if t.startswith("?")]) for p in predicate_defs}
    definitions = []
    for item in tree[1:]:
        if not (isinstance(item, list) and item[0] == ":action"):
            continue
        fields = {item[k]: item[k + 1] for k in range(2, len(item), 2)}
        params = typed_elements(fields[":parameters"])
        pre = []
        for a in atoms(fields[":precondition"]):
            if a[0] == "not":
                raise ValueError("Solo se usan precondiciones positivas STRIPS")
            pre.append(a)
        add = []
        delete = []
        for a in atoms(fields[":effect"]):
            if a[0] == "not":
                delete.append(a[1])
            else:
                add.append(a)
        definitions.append((item[1], params, pre, add, delete))
    return name, predicates, definitions


def parse_problem(tree):
    assert tree[0] == "define"
    sections = {x[0]: x for x in tree[1:] if isinstance(x, list)}
    domain_name = sections[":domain"][1]
    objects = typed_elements(sections[":objects"][1:])
    initial = frozenset(tuple(atom) for atom in sections[":init"][1:])
    goal = frozenset(tuple(atom) for atom in atoms(sections[":goal"][1]))
    return domain_name, objects, initial, goal


def ground_actions(definitions, objects):
    by_type = {}
    for name, ty in objects:
        by_type.setdefault(ty, []).append(name)
        by_type.setdefault("object", []).append(name)
    ground = []
    for name, params, pre, add, delete in definitions:
        types = [by_type.get(t, []) for _, t in params]
        for args in product(*types):
            mapping = dict(zip([var for var, _ in params], args))
            p = frozenset(substitute(a, mapping) for a in pre)
            a = frozenset(substitute(e, mapping) for e in add)
            d = frozenset(substitute(e, mapping) for e in delete)
            ground.append((name, args, p, a, d))
    return ground


def solve_bfs(initial, goal, actions):
    queue = deque([initial])
    parent = {initial: None}
    via_action = {}
    while queue:
        state = queue.popleft()
        if goal <= state:
            plan = []
            while parent[state] is not None:
                plan.append(via_action[state])
                state = parent[state]
            plan.reverse()
            return plan, len(parent)
        for action in actions:
            _, _, pre, add, delete = action
            if pre <= state:
                nxt = (state - delete) | add
                if nxt not in parent:
                    parent[nxt] = state
                    via_action[nxt] = action
                    queue.append(nxt)
    raise RuntimeError("Problema sin solucion")


def main():
    domain_name, predicates, definitions = parse_domain(parse_pddl(ROOT / "domain.pddl"))
    problem_domain, objects, initial, goal = parse_problem(parse_pddl(ROOT / "problem.pddl"))
    assert domain_name == problem_domain, "El dominio del problema no coincide"
    arities = predicates
    for clause in [*initial, *goal]:
        if clause[0] not in arities or len(clause) - 1 != arities[clause[0]]:
            raise ValueError(f"Predicado invalido en problema: {clause}")
    actions = ground_actions(definitions, objects)
    for _, _, pre, add, delete in actions:
        for clause in pre | add | delete:
            if clause[0] not in arities or len(clause) - 1 != arities[clause[0]]:
                raise ValueError(f"Predicado invalido en accion: {clause}")
    plan, states = solve_bfs(initial, goal, actions)
    assert len(plan) >= 5
    print(f"Dominio: {domain_name}")
    print(f"Predicados: {len(predicates)}")
    print(f"Esquemas de accion: {len(definitions)}")
    print(f"Acciones instanciadas: {len(actions)}")
    print(f"Estados explorados: {states}")
    print(f"Longitud minima del plan (BFS): {len(plan)} acciones")
    print("\nPLAN:")
    state = initial
    lines = []
    for index, (name, args, pre, add, delete) in enumerate(plan, 1):
        assert pre <= state, f"Precondicion incumplida en paso {index}"
        state = (state - delete) | add
        line = f"{index:02d}. ({name} {' '.join(args)})"
        print(line)
        lines.append(line)
    assert goal <= state
    print("\nMETA SATISFECHA:")
    for clause in sorted(goal):
        print("  (" + " ".join(clause) + ")")
    (ROOT / "plan_ejemplo.txt").write_text(
        "PLAN DE EJEMPLO - generado mediante busqueda BFS sobre domain.pddl y problem.pddl\n"
        "El planificador web podria encontrar otro orden igualmente correcto.\n\n"
        + "\n".join(lines)
        + "\n\nVerificacion: todas las precondiciones se satisfacen en su paso; meta final alcanzada.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
