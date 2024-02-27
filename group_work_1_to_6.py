from gurobipy import *

# Parameters -------------------------------------------------------------------------------

T = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Demand per period
D = [53000, 52000, 53000, 38000, 32000, 19000, 27000, 35000, 36000, 38000, 42000, 48000]
print("D[0]",D[0])

# Selling price per piece to distributors
E = 75

# Working hours per piece
u = 2

# Number of regular working hours: 22*8
h = 176

# Maximum number of overtime hours
o_max = 10

# Labor costs monthly: 22*8*15
c_W = 2640

# Recruitment costs
c_H = 800

# Lay-off costs
c_L = 1000

# Cost of materials
c_P = 20

# Warehousing costs
c_I = 10

# Shortage costs
c_S = 12

# Third-party procurement costs
c_C = 67

# Overtime costs 
c_O = 18

model = Model()
model.setParam("MIPGap", 1e-10)

# Variables
# ----------------------------------------------------------------------

#Number of Employees in period t, (t = 0 -> initial period)
W = model.addVars([0]+T, name="W", vtype=GRB.INTEGER)

# Number of workers hired at period t
H = model.addVars(T, name="H", vtype=GRB.INTEGER)

# Number of workers laid off at period t
L = model.addVars(T, name="L", vtype=GRB.INTEGER)

# Production quantity in period t
P = model.addVars(T, name="P", vtype=GRB.INTEGER)

# Stock in period t, (or at the end of period t)
I = model.addVars([0] + T, name="I", vtype=GRB.INTEGER)

# Shortage in period t
S = model.addVars([0] + T, name="S", vtype=GRB.INTEGER)

# External procurement in period t
C = model.addVars(T, name="C", vtype=GRB.INTEGER)

# Overtime in period t
O = model.addVars(T, name="O", vtype=GRB.INTEGER)

# Constraints
# ----------------------------------------------------------------

# Set initial number of workers to 100
model.addConstr(W[0] == 100)

# Set the initial stock to 3000
model.addConstr(I[0] == 3000)

# Set the initial production quantity to 0
#model.addConstr(P[0] == 0)

# Set the initial shortage to 0
model.addConstr(S[0] == 0)

# Set the shortage in the end to 0 
model.addConstr(S[12] == 0)

# Number of employees
model.addConstrs(W[t] == W[t-1] + H[t] - L[t] for t in T)

# At most 150 hirings in period t
model.addConstrs(H[t] <= 150 for t in T)

# Maximum overtime in period t
model.addConstrs(O[t] <= W[t] * 10 for t in T)

# Production capacity in period t
model.addConstrs(P[t] <= (W[t]*22*8)/2 + O[t]/2 for t in T)

# Storage balance
# for t=1 we have I[1] = I[0] + P[1] + C[1] - D[0] - S[0] + S[1]
model.addConstrs(I[t] == I[t-1] + P[t] + C[t] - D[t-1] -S[t-1] + S[t] for t in T) # T has length 12 and max index 11, D ran out of index

# Objective function: maximization of profit
model.setObjective(
    sum(E * D[t-1] for t in T) - 
    sum(H[t] * c_H + L[t] * c_L + W[t] * c_W + O[t] * c_O + P[t] * c_P + C[t] * c_C + I[t] * c_I + S[t] * c_S for t in T),
    GRB.MAXIMIZE
)

model.optimize()

model.printAttr("X")

print("1) The annual profit of the optimal plan is ",model.objVal)
print("2)")
print("3)")
print("4) Number of employees per month:")
for t in T: 
    print("The number of employees in the period is {} {}.".format(t, W[t].X))
print("5) Number of inventory per month:")
for t in T:
    print("The number of inventory in the period is {} {}.".format(t, I[t].X))
print("6)")