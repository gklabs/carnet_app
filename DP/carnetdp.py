import pandas as pd
import numpy as np
from scipy.stats import truncnorm
import random

random.seed(42)
class vehicle:
    def __init__(self,eq_no,eq_desc,vtype,dept,dept_id, purchasedate,age2020,current_age,purchaseprice,depreciated2020,miles2020,vmt2020,mandr2020,cumulativemandr2020,totcum_mandr, mpg2020,emission2020, vmt, replacementvehicle_id, replacement_vehicle_desc,replacement_vehicle_purchaseprice,replacement_vehicle_mpge,replacement_vehicle_type,decision):
        self.eq_no = eq_no
        self.eq_desc = eq_desc
        self.age2020= age2020
        self.current_age= current_age
        self.dept= dept
        self.deptid = dept_id

        
        self.miles2020= miles2020
        self.mpg2020= mpg2020
        self.vmt2020 = vmt2020
        self.vmt=vmt
        self.mandr2020= mandr2020
        self.cumulativemandr= cumulativemandr2020
        self.depreceated2020= depreciated2020
        self.vtype= vtype
        
        
        self.replacementvehicle_id = replacementvehicle_id
        self.replacement_vehicle_desc = replacement_vehicle_desc
        self.replacement_vehicle_purchaseprice=replacement_vehicle_purchaseprice
        self.replacement_vehicle_mpge = replacement_vehicle_mpge	
        self.replacement_vehicle_type=  replacement_vehicle_type  

        self.decision= decision #dict

    @property
    def annualmiles(self):
        miles_dict= {}
        #Assigning same miles for all the years in the planning horizon
        for t in range(interval):
            miles_dict[t]= self.miles2020
        return miles_dict
    
    @property
    def mpg(self):
        mpg_dict= {}
        option= "constant"
        computedmpg= self.mpg2020
        if option == "constant":
            factor=1
        #assumes a 10% deterioration rate every year
        elif option == "deterioration":
            factor = 0.9
        for t in range(interval):
            computedmpg= computedmpg* factor
            mpg_dict[t]= computedmpg
        return mpg_dict

   
    @property
    def fuel(self):
        
        fuel_dict={}
        option = "constant"

        if option == "random":
        #truncated normal distribution for fuel price per gallon
            lower, upper= 2,3
            mu,sigma= 2.3,0.05
            f_x= truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
            f_p= f_x.rvs(interval)
        elif option == "constant":
            f_p= np.repeat(2.3,interval)
        
        for t in range(interval):
            fuel_dict[t]= self.annualmiles[t]/self.mpg[t] * f_p[t]
        return fuel_dict

    @property
    def mandr(self):
        option= "constant"
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

    @property
    def purchase(self,replacement_v,option):
        purchase_dict={}
        computedpp= replacement_v.pp
        if option == "constant":
            factor=1.1
        for t in range(interval):
            computedpp= computedpp* factor
            purchase_dict[t]= computedpp

        return purchase_dict
    
    @property
    def emission(self):

        emission_dict ={}
        for t in range(interval):
            fuel_consumed = self.annualmiles[t]/self.mpg[t]
            emission_dict[t]= fuel_consumed * carbon_factor
        
        return emission_dict
        

    @property
    def depreciation(self):
        age= self.current_age
        cur_depvalue = self.depreceated2020
        depreciation_dict={}

        for t in range(interval):
            age+=1

            if 0<= age <=1:
                cur_depvalue = cur_depvalue - 0.25*cur_depvalue
                depreciation_dict[t] = cur_depvalue
            elif age >=2:
                cur_depvalue = cur_depvalue - 0.12*cur_depvalue
                depreciation_dict[t] = cur_depvalue
        
        return depreciation_dict
    

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


    

# decides whether to keep or replace a given vehicle based on intrinsic numbers without the budget in mind
class dynamic_prog:
    def contributionfunction(self,v,t):
        decision= 'keep'
        #compute contribution function
        C_tx = np.zeros((t,interval-t))
        
        #initialize all the costs to zero
        P_t= 0
        M_t= 0
        E_t = 0
        F_t = 0
        g_t= {}

        g_t[interval]= 10000

        np.fill_diagonal(C_tx, 999999)
        #--- Current year costs ---- #
        # purchase cost adjusted with depreciation
        for x in range(t+1,interval):
            P_t = v.replacement_vehicle_purchaseprice - v.depreciation[x]
            
            for i in range(t,x):
                M_t = M_t+ v.mandr[i]
                E_t= E_t+ (v.emission[i] * emission_to_dollar)
                F_t = F_t+ v.fuel[i]

            C_tx[i][x] = P_t + M_t + E_t+ F_t


        # ----- Future years costs ---- #
        for i in range(interval,t,-1):
            for x in range(t+1,interval):
                g_t[i] = min(C_tx[i]+g_t[x])

        print(g_t)
        print("hi")
        decision= {}
        return decision


vehicle_info= pd.read_csv("vehicle_info_prefinal.csv",thousands=r',')
print(vehicle_info.head(10))
# replacement_info= pd.read_csv("replacement_info.csv")
vportfolio=[]
emission_to_dollar = 120
carbon_factor = 2.412

colnames= list(vehicle_info.columns.values)
for index,row in vehicle_info.iterrows():
    eq_no= row['equipmentid']
    eq_desc= row['vehicledescription']
    vtype = row['vehicle_type']
    dept= row['dept_name']
    dept_id =row['deptid']
    purchasedate= row['purchasedate']
    age2020= row['age2020']
    current_age = age2020
    purchaseprice= row['purchaseprice']
    depreciated2020 = row['depreceated value']
    miles2020= row['miles2020']
    vmt2020= row['cumulative_miles']
    mandr2020= row['maintenance2020']
    cumulativemandr2020= row['cumulative_maintenance']
    totcum_mandr = cumulativemandr2020
    mpg2020= row['mpg2020']
    emission2020= row['emissions2020']
    vmt= vmt2020
    replacementvehicle_id = row['replacementvehicle_id']
    replacement_vehicle_desc = row['replacement_vehicle_desc']
    replacement_vehicle_purchaseprice = row['replacement_vehicle_purchaseprice']
    replacement_vehicle_mpge = row['replacement_vehicle_mpge']		
    replacement_vehicle_type= row['replacement_vehicle_type']   
    decision = {}
    
    
    v= vehicle(eq_no,eq_desc,vtype,dept,dept_id, purchasedate,age2020,current_age,purchaseprice,depreciated2020,miles2020,vmt2020,mandr2020,cumulativemandr2020,totcum_mandr, mpg2020,emission2020, vmt, replacementvehicle_id, replacement_vehicle_desc,replacement_vehicle_purchaseprice,replacement_vehicle_mpge,replacement_vehicle_type,decision)
    
    vportfolio.append(v)

interval =  UI_params['end_year']- UI_params['start_year']

def main():
    print("interval:",interval)
    eligiblevehicles=[]
    
    for t in range(interval):
        for v in vportfolio:
            threshold = UI_params['min_miles_replacement_threshold']
            
            #check if vehicle is eligible based on threshold miles
           
            if (v.vmt >= threshold):
                eligiblevehicles.append(v)
                #start DP calculations
                dp_optimizer= dynamic_prog()
                v.decision = dp_optimizer.contributionfunction(v,t)

            v.current_age+=1
            v.vmt= v.vmt+ v.annualmiles[t]
            


            
                            
if __name__ == "__main__":
    main()



    