import pandas as pd
from scipy.stats import truncnorm
import random

random.seed(42)
class vehicle:
    def __init__(self,eq_no,eq_desc,age,dept,miles2020,mpg2020,vmt2020,mandr2020,cumulativemandr,mpg,emission,vmt,decision,annualmiles,vtype,mandr,fuel):
        self.eq_no = eq_no
        self.eq_desc = eq_desc
        self.age= age
        self.dept= dept
        
        self.miles2020= miles2020
        self.mpg2020= mpg2020
        self.vmt2020 = vmt2020
        self.mandr2020= mandr2020
        self.cumulativemandr= cumulativemandr

        self.vtype= vtype 
        self.vmt= vmt

        self.mpg= mpg #dict
        self.decision= decision #dict
        self.annualmiles =annualmiles #dict
        self.emission= emission #dict
        self.mandr= mandr #dict
        self.fuel= fuel #dict

class portfoliocosts:
    def __init__(self,totfuelcost,totmandrcost,totpurchcost,totemission):
        self.totfuelcost= totfuelcost
        self.totmandrcost= totmandrcost
        self.totpurchcost= totpurchcost
        self.totemission= totemission

UI_params = {
    'initial_procurement_budget':1300000,
    'procurement_budget_growthrate':0.03,
    'start_year':2021,
    'end_year':2037,
    'emissions_target_pct_of_base':0.40,
    'min_miles_replacement_threshold':150000,#miles
    'max_vehicles_per_station':1000

    
    # 'objective_weights':{'cost':0.01,'emissions':0.99},
    # 'emissions_baseline': 1000,#metric tons
    # 'min_vehicle_age_replacement_threshold':60,#years
    # 'initial_maintenance_budget':1000000,
    # 'maintenance_budget_rate':0.03,
}
class projections:
    def annualmiles(self,v):
        miles_dict= {}
        #Assigning same miles for all the years in the planning horizon
        for t in interval:
            miles_dict[t]= v.miles2020
        return miles_dict

    def mpg(self,v, option):
        mpg_dict= {}
        computedmpg= v.mpg2020
        if option == "constant":
            factor=1
        #assumes a 10% deterioration rate every year
        elif option == "deterioration":
            factor = 0.9
            for t in range(interval):
                computedmpg= computedmpg* factor
                mpg_dict[t]= computedmpg
        return mpg_dict

    def fuel(self,v):
        
        fuel_dict={}

        #truncated normal distribution for fuel price per gallon
        lower, upper= 2,3
        mu,sigma= 2.3,0.05
        f_x= truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
        f_p= f_x.rvs(interval)
        
        for t in range(interval):
            fuel_dict[t]= v.annualmiles[t] * f_p[t]
        return fuel_dict

    def mandr(self,v,option):
        mandr_dict= {}
        computedmandr= v.mandr2020
        if option == "constant":
            factor= 1
        elif option == "growth":
            factor=1.15
        for t in range(interval):
            computedmandr= computedmandr *factor
            mandr_dict[t]= computedmandr
        
        return mandr_dict

    def purchase(self,v,replacement_v,option):
        purchase_dict={}
        computedpp= replacement_v.pp
        if option == "constant":
            factor=1.1
        for t in range(interval):
            computedpp= computedpp* factor
            purchase_dict[t]= computedpp

        return purchase_dict
    def emission(self):
        pass

class dynamic_prog:
    def contributionfuncion(self,v):
        decision= 'keep'
        #compute contribution function

        if v.decision== 'replace':
            #replace vehicle with corresponding AV
            replacevehicle(v)
                    
            
        return decision
       
    def replacevehicle(self,v,replacement_v):
        replacement_v= get_replacementvehicle(v)
        pass

vehicle_info= pd.read_csv("vehicle_info.csv")
# replacement_info= pd.read_csv("replacement_info.csv")
vportfolio=[]

colnames= list(vehicle_info.columns.values)
for index,rows in vehicle_info.iterrows():
    
    # equipmentid	description	dept	
    # deptid	purchasedate	purchaseprice	depreceated value	miles2020	cumulative_miles	maintenance2020	mpg2020	emissions2020

    v= vehicle(eq_no,eq_desc,age,dept,miles2020,mpg2020,vmt2020,
    mandr2020,cumulativemandr,mpg,emission,vmt,decision,annualmiles,vtype,mandr,fuel)
    vportfolio.append(v)

interval = UI_params['start_year'] - UI_params['end_year']
def main():
    
    eligiblevehicles=[]
    
    for t in range(interval):
        for v in vportfolio:
            #check if vehicle is eligible based on threshold miles
            if v.vmt>= UI_params['min_miles_replacement_threshold']:
                eligiblevehicles.append(v)
                #start DP calculations
                dp_optimizer= dynamic_prog()
                v.decision = dp_optimizer.contributionfuncion(v)
                
if __name__ == "__main__":
    main()



    