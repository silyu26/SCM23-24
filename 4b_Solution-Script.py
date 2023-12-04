from gurobipy import *

#=============================
# Parameters 
#=============================

# Planning period and time periods
T = [1, 2, 3, 4, 5, 6]

# Working hours per piece
u = 4

# Number of regular working hours
h = 160

# Demand per period
D = [1600, 3000, 3200, 3800, 2200, 2200]

# Selling price per piece
E = 40

# Labor costs monthly
c_W = 640

# Recruitment costs
c_H = 300

# Dismissal costs
c_L = 500

# Cost of materials
c_P = 10

# Warehousing costs
c_I = 2

# Shortage costs
c_S = 5

# Third-party procurement costs
c_C = 30

# Overtime costs
c_O = 6

# Maximum number of overtime hours
o_max = 10


model = Model()
model.setParam("MIPGap", 1e-10)

#=============================
# Variables 
#=============================

# number of workers in period t, t = 0 -> initial period
W = model.addVars([0] + T, name="W", vtype=GRB.INTEGER)

# Number of workers hired at period t
H = model.addVars(T, name="H", vtype=GRB.INTEGER)

# Number of workers laid off at period t
L = model.addVars(T, name="L", vtype=GRB.INTEGER)

# Production quantity in period t
P = model.addVars(T, name="P", vtype=GRB.INTEGER)

# Stock in period t, or at the end of period t
I = model.addVars([0] + T, name="I", vtype=GRB.INTEGER)

# Shortage in period t
S = model.addVars([0] + T, name="S", vtype=GRB.INTEGER)

# External procurement in period t
C = model.addVars(T, name="C", vtype=GRB.INTEGER)

# Overtime in period t
O = model.addVars(T, name="O", vtype=GRB.INTEGER)

# Sales promotion in period t (Binary variable) ####################################################
delta = model.addVars([0] + T, name="delta", vtype=GRB.BINARY)

#=============================
# Constraints 
#=============================

# Set initial number of workers to 80
model.addConstr(W[0] == 80)

# Set the initial stock to 1000
model.addConstr(I[0] == 1000)

# Set the inventory in the last period to at least 500 units
model.addConstr(I[6] >= 500)

# Set missing quantities to 0
model.addConstr(S[0] == 0)

# No shortages at the end of the planning period, meet all demand
model.addConstr(S[6] == 0)

# Number of workers
model.addConstrs(
        W[t] == W[t - 1] + H[t] - L[t] for t in T)

# Production capacity
model.addConstrs(
        P[t] <= (h/u) * W[t] + O[t]/u for t in T)

# Overtime is limited
model.addConstrs(
        O[t] <= o_max * W[t] for t in T)



# Warehousing
model.addConstrs(
    I[t - 1] + P[t] + C[t] == D[t - 1] + S[t - 1] + I[t] - S[t] 
    - 0.2 * D[t - 1] * sum(delta[t_] for t_ in range(t-2, t) if t_ > 0)
    + delta[t] * (0.1 * D[t - 1] + 0.2 * sum(D[t_ - 1] for t_ in range(t+1, t+2+1) if t_ <= len(T)))
    for t in T)

#I[2] + P[3] + C[3] == D[2] + S[2] + I[3] - S[3]
#                      - 0.2 * D[2] * sum(delta[1] + delta[2])
#                      + delta[3] * (0.1 * D[2] + 0.2 * sum(D[3] + D[4]))

# Maximum one sales promotion over the planning period
model.addConstr(
    sum(delta[t] for t in T) <= 1)

# no promotion in period 0, 5,6
model.addConstr(delta[0]+delta[5]+delta[6] == 0)
# model.addConstrs(
#     delta[1] == 1 for t in T )

# Objective function: maximization of profit
model.setObjective(
    sum(E * D[t - 1] for t in T)
    - 1 * sum(D[t - 1] * delta[t] for t in T)
    + (E - 1) * sum(0.1 * D[t - 1] * delta[t] for t in T)
    - 1 * sum(delta[t] * D[t_ - 1] * 0.2 for t in T for t_ in range(t+1, t+2+1) if t_ <= len(T))
  - sum(c_W * W[t] + c_O * O[t] + c_H * H[t] + c_L * L[t] 
      + c_I * I[t] + c_S * S[t] + c_P * P[t] + c_C * C[t] for t in T) 
  , GRB.MAXIMIZE)


model.optimize()

model.printAttr("X")

print("Red Tomato Tools , the optimal production plan,"
      "profit of {} monetary units".format(model.objVal))

for t in T:
    print("The number of employees in the period is {} {}.".format(t, W[t].X))
    if H[t].X != 0:
        print("The number of newly recruited"
          " Employees in period {} {}.".format(t, H[t].X))
    if L[t].X != 0:
        print("The number of laid-off"
          " Employees in period {} {}.".format(t, L[t].X))

print("The costs for employee salaries amount to more than the planning"
      " period to {} monetary units.".format(sum(c_W * W[t].X for t in T)))
print("The costs for overtime amount to more than the planning"
      " period to {} monetary units.".format(sum(c_O * O[t].X for t in T)))
print("The costs for new hires amount to over the planning"
      " period to {} monetary units.".format(sum(c_H * H[t].X for t in T)))
print("The costs for redundancies amount to more than the planning"
      " period to {} monetary units.".format(sum(c_L * L[t].X for t in T)))
print("The costs for warehousing amount to more than the planning"
      " period to {} monetary units.".format(sum(c_I * I[t].X for t in T)))
print("The costs for shortfalls amount to more than the planning"
      " period to {} monetary units.".format(sum(c_S * S[t].X for t in T)))
print("The costs for production material amount to more than the planning"
      " period to {} monetary units.".format(sum(c_P * P[t].X for t in T)))
print("The costs for external procurement amount to over the planning"
      " period to {} monetary units.".format(sum(c_C * C[t].X for t in T)))










