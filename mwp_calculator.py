# Identifies Minimum Working Products

def calculate_mwp(logic_rules):
    # Use SAT Solver to find minimal configurations
    from pysat.solvers import Solver
    solver = Solver()
    
    # Add rules to the solver
    for rule in logic_rules:
        solver.add_clause(rule)
    
    # Extract MWPs
    mwp_list = []
    while solver.solve():
        model = solver.get_model()
        mwp_list.append(model)
        solver.add_clause([-lit for lit in model])  # Prevent duplicate solutions
    
    solver.delete()
    return mwp_list
